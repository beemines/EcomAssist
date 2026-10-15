"""有界理解/分类评估；默认零上游，聊天只导入真实浏览器关联证据。"""
import argparse
import asyncio
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.core.errors import ServiceError
from app.workflow.entities import explicit_order_ids, validate_resolved_entities
from app.workflow.intent import IntentClassifier, route_intent
from app.workflow.prompts import INTENT_SYSTEM, UNDERSTANDING_SYSTEM
from app.workflow.understanding import QueryUnderstanding

CASES = Path(__file__).with_name('intent_routing_cases.jsonl')
BROWSER_SCENARIOS = ('policy-no-picker', 'logistics-refund-logistics', 'missing-order-select-resume',
                     'pause-refresh-restart-new-message', 'refund-form-cancel-submit',
                     'duplicate-and-cross-conversation', 'repair-no-refund', 'complaint-social-other')
SCORER_VERSION = 'request-semantics-v3-whole-query'


def preserved_request(case, query):
    """六条固定题的整句请求契约；未知表达保守失败，不是通用NLP判官。

    主语、动作和疑问方式均显式枚举，只允许无语义标点变化及有限同义词。
    fullmatch消费整句，故任意新增时间/否定/结论分句都不能借合法后缀通过。
    只有通用保修题允许型号或唯一来源订单；具体退货必须保留订单身份。
    """
    lamp_order = r'订单1001(?:的(?:明辉护眼台灯)?MH-LP200)?'
    dispenser = r'(?:明辉饮水机)?MH-WD100'
    dispenser_order = rf'订单1002(?:的{dispenser})?'
    eligibility = r'(?:能(?:申请)?退(?:货)?[吗么不]|能不能(?:申请)?退(?:货)?)[？?]?'
    warranty_subject = rf'(?:{dispenser_order}|{dispenser})'
    patterns = {
        'dialogue-1-2': rf'(?:请问)?{lamp_order}{eligibility}',
        'dialogue-3-3': rf'(?:请问)?{dispenser_order}{eligibility}',
        'dialogue-1-3': r'(?:请问)?订单1001的物流(?:现在|目前)到哪(?:里|儿)?了[？?]?',
        'dialogue-5-2': r'(?:请为)?订单1001申请退货[。.!！]?',
        'dialogue-5-3': r'(?:请)?(?:查|查询)订单1001的配送进度[。.!！？?]?',
        'dialogue-6-2': rf'(?:请问)?{warranty_subject}的保修(?:期限|期|时间)?(?:是|有|为)?(?:多久|多长(?:时间)?|多少(?:年|个月|天))[？?]?',
    }
    case_id = case.get('id')
    # 兼容独立的同一保修契约测试，不将任意含“保修”的未知题套入本题。
    if case_id is None and case['expected_query'] == 'MH-WD100的保修期限是多久？':
        case_id = 'dialogue-6-2'
    pattern = patterns.get(case_id)
    return pattern is not None and re.fullmatch(pattern, query.strip()) is not None


def digest(value):
    """稳定摘要仅覆盖公开样例/Prompt/证据，不读取密钥。"""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True).encode()).hexdigest()


def fixture_messages(rows):
    """只转换明确提供的事实消息，不接触expected标注。"""
    classes = {'user': HumanMessage, 'assistant': AIMessage, 'tool': ToolMessage}
    return [classes[row['role']](**{key: value for key, value in row.items() if key != 'role'}) for row in rows]


class RecordingModel:
    """包裹原结构化网络边界，保存实际公开响应及消息摘要。"""
    def __init__(self, model):
        self.model, self.calls = model, []

    def with_structured_output(self, schema, **kwargs):
        """复用生产结构化接口，记录错误调用也不自动重试。"""
        bound, owner = self.model.with_structured_output(schema, **kwargs), self
        class Recorded:
            async def ainvoke(self, messages):
                """开始即记一次尝试，原样返回结构化结果。"""
                row = {'input_hash': digest([m.model_dump(mode='json') for m in messages]), 'raw': None}
                owner.calls.append(row)
                output = await bound.ainvoke(messages)
                raw = output.get('raw') if isinstance(output, dict) else None
                if raw is not None:
                    row.update(raw=raw.content, finish_reason=raw.response_metadata.get('finish_reason'),
                               usage=raw.usage_metadata)
                return output
        return Recorded()


def score(case, row, history):
    """按明确标注核对工程指标，允许语义等价消解但不放宽完整透传。"""
    query = row.get('resolved_question')
    checks = {'intent': row.get('intent') == case['expected_intent'],
              'route': row.get('route') == case['expected_route'], 'protocol': query is not None and row.get('intent') is not None}
    if case.get('full_passthrough'):
        checks['full_passthrough'] = query == case['query']
    if case.get('resolvable'):
        required_models = set(re.findall(r'[A-Z]+-[A-Z0-9]+', case['expected_query']))
        orders = explicit_order_ids(query or '')
        models = set(re.findall(r'[A-Z]+-[A-Z0-9]+', query or ''))
        order_match = bool(orders) and orders == {case['antecedent']}
        model_match = case['expected_route'] == 'knowledge' and bool(required_models) and required_models <= models
        checks['resolvable'] = bool(query) and (order_match or model_match) and orders <= {case['antecedent']} and models <= required_models and preserved_request(case, query)
    if case.get('preserve_ambiguity'):
        checks['ambiguity_zero_guess'] = query is not None and not (explicit_order_ids(query) - explicit_order_ids(case['query']))
    try:
        validate_resolved_entities(case['query'], query or '', history)
        identifiers = explicit_order_ids(case['query'])
        entities = set(re.findall(r'[A-Z]+-[A-Z0-9]+|\d+(?:\.\d+)?\s*(?:元|天|小时|个月|年|毫升|升|公斤|千克|克)', case['query']))
        checks['entity_preservation'] = query is not None and identifiers <= explicit_order_ids(query) and all(e in query for e in entities)
    except ServiceError:
        checks['entity_preservation'] = False
    return checks


async def evaluate(*, mode='understanding', split='acceptance', live=False, model=None,
                   case_id=None, previous=None, evidence=None, model_name=None, on_update=None):
    """固定split全分母；失败依赖链阻断，定点只复用既有有效观测。"""
    cases = [json.loads(line) for line in CASES.read_text(encoding='utf-8').splitlines() if line.strip()]
    cases = [case for case in cases if case['split'] == split]
    if case_id and case_id not in {case['id'] for case in cases}:
        raise ValueError('case-id is not in selected split')
    report = {'mode': mode, 'split': split, 'live': live, 'scorer_version': SCORER_VERSION, 'created_at': datetime.now(timezone.utc).isoformat(),
              'sample_hash': digest(cases), 'prompt_hash': digest([UNDERSTANDING_SYSTEM, INTENT_SYSTEM]),
              'implementation_hash': digest({name: (CASES.parents[1] / name).read_text(encoding='utf-8') for name in
                  ('app/workflow/understanding.py', 'app/workflow/intent.py', 'evals/evaluate_intent_routing.py')}),
              'model': model_name or ('injected-test-boundary' if model else None), 'model_calls': 0,
              'results': [], 'metrics': {}, 'full_chain': {'passed': 0, 'total': len(cases), 'not_executed': len(cases)}}
    recorder = RecordingModel(model) if model is not None else None
    histories, valid = {}, {}
    previous_rows = {}
    sources = previous if isinstance(previous, list) else [previous] if previous else []
    for source in sources:
        if (source.get('sample_hash') != report['sample_hash'] or source.get('model') != report['model']
                or source.get('mode') != 'understanding' or source.get('live') is not True):
            continue
        for observed in source.get('results', []):
            if observed.get('status') == 'passed' and observed.get('checks') and all(observed['checks'].values()):
                previous_rows[observed['id']] = (observed, source['prompt_hash'], digest(source), source.get('implementation_hash'))
    for case in cases:
        row = {'id': case['id'], 'dialogue_id': case['dialogue_id'], 'turn': case['turn'],
               'raw_question': case['query'], 'status': 'not_executed', 'model_calls': 0,
               'history': [], 'checks': {}, 'usage': {}, 'raw_outputs': []}
        report['results'].append(row)
        dialogue = case['dialogue_id']
        selected = live and mode == 'understanding' and (case_id is None or case['id'] == case_id)
        old_source = previous_rows.get(case['id'])
        old = old_source[0] if old_source else None
        if not selected and old and old.get('raw_question') == case['query'] and (case['turn'] == 1 or valid.get(dialogue) == case['turn'] - 1):
            # 历史结果只作定点前提，不计作本次重新执行或新通过。
            histories[dialogue] = fixture_messages(old.get('history', [])) + [HumanMessage(old['raw_question']), AIMessage(old['resolved_question'])]
            valid[dialogue] = case['turn']
            row['reused_history_hash'] = digest(old)
            row['source_prompt_hash'], row['source_report_hash'], row['source_implementation_hash'] = old_source[1:]
            continue
        if not selected:
            continue
        if case['turn'] > 1 and valid.get(dialogue) != case['turn'] - 1:
            row.update(status='blocked', error='previous_turn_not_valid')
            continue
        if recorder is None:
            raise ValueError('live understanding requires configured model')
        history = list(histories.get(dialogue, [])) + fixture_messages(case.get('history_fixture', []))
        row['history'] = [dict(role='user' if isinstance(m, HumanMessage) else 'tool' if isinstance(m, ToolMessage) else 'assistant', content=m.content,
                               **({'tool_calls': m.tool_calls} if isinstance(m, AIMessage) and m.tool_calls else {}),
                               **({'tool_call_id': m.tool_call_id} if isinstance(m, ToolMessage) else {})) for m in history]
        start = len(recorder.calls)
        understanding = QueryUnderstanding(recorder, input_budget=8000, timeout_seconds=60)
        classifier = IntentClassifier(recorder, input_budget=8000, timeout_seconds=60)
        try:
            resolved = await understanding.resolve(case['query'], history)
            row['resolved_question'] = resolved.query
            result = await classifier.classify(resolved.query)
            row.update(intent=result.intent, raw_intent=result.raw_intent, confidence=result.confidence, route=route_intent(result.intent))
            row['checks'] = score(case, row, history)
            row['status'] = 'passed' if all(row['checks'].values()) else 'failed'
        except ServiceError as exc:
            row.update(status='failed', error=exc.code, error_message=exc.message)
            if getattr(exc, 'finish_reason', None) in ('length', 'content_filter'):
                row['finish_reason'] = exc.finish_reason
            row['checks'] = score(case, row, history)
        finally:
            row['usage'] = {'understanding': understanding.usage, 'classification': classifier.usage}
            row['raw_outputs'] = recorder.calls[start:]
            row['model_calls'] = len(row['raw_outputs'])
        valid[dialogue] = case['turn'] if row['status'] == 'passed' else 0
        if valid[dialogue]:
            histories[dialogue] = history + [HumanMessage(case['query']), AIMessage(row['resolved_question'])]
        summarize(report, cases)
        if on_update:
            on_update(report)
    if mode == 'chat' and live and evidence:
        evidence = await verify_chat_storage(evidence)
        import_chat_evidence(report, evidence)
    summarize(report, cases)
    return report


async def verify_chat_storage(evidence):
    """导入时再读实际SQL和指定原始完成根，JSON自报true不构成证据。"""
    import runpy
    evidence = json.loads(json.dumps(evidence))
    if evidence.get('mode') != 'live':
        return evidence
    snapshot = None
    for item in evidence.get('results', []):
        item['storage_revalidated'] = False
        root = item.get('root_evidence', {})
        cid, aid, checkpoint = item.get('conversation_id'), root.get('assistant_message_id'), root.get('checkpoint_id')
        if (item.get('status') != 'PASS' or item.get('name') not in BROWSER_SCENARIOS
                or not all(isinstance(value, str) and value for value in (cid, aid, checkpoint))
                or not Path(item.get('screenshot', '')).is_file()):
            item['storage_verification_error'] = 'missing_actual_browser_root_locator'
            continue
        try:
            if snapshot is None:
                snapshot = runpy.run_path(str(CASES.parents[1] / 'scripts/intent-routing-storage-evidence.py'))['snapshot']
            actual = await snapshot(cid, aid, checkpoint)
            sql, stored = actual.get('sql_evidence', {}), actual.get('root_evidence', {})
            verified = (sql.get('verified') is True and stored.get('durable') is True
                and sql.get('assistant_message_id') == aid == stored.get('assistant_message_id')
                and stored.get('checkpoint_id') == checkpoint
                and all(stored.get(key) == root.get(key) for key in ('raw_question', 'resolved_question', 'intent', 'route')))
            item['storage_revalidated'] = verified
            item['local_storage_hash'] = digest({'sql': sql, 'root': stored})
            if not verified:
                item['storage_verification_error'] = 'local_sql_root_mismatch'
        except Exception as exc:
            item['storage_verification_error'] = type(exc).__name__
    return evidence


def import_chat_evidence(report, evidence):
    """只接受实际live逐case记录且附关联SQL和持久完成根的证据，不发送聊天。"""
    if evidence.get('mode') != 'live':
        return
    by_id = {r.get('case_id'): r for r in evidence.get('results', [])}
    for row in report['results']:
        item = by_id.get(row['id'])
        if not item:
            continue
        sql, root = item.get('sql_evidence', {}), item.get('root_evidence', {})
        linked = (item.get('status') == 'PASS' and item.get('storage_revalidated') is True and item.get('requests') and item.get('screenshot')
                  and sql.get('verified') is True and root.get('durable') is True
                  and sql.get('conversation_id') == root.get('conversation_id') == item.get('conversation_id')
                  and sql.get('assistant_message_id') == root.get('assistant_message_id'))
        row.update(status='passed' if linked else 'failed', evidence_hash=digest(item))
    report['browser_evidence_hash'] = digest(evidence)
    by_name = {item.get('name'): item for item in evidence.get('results', [])}
    report['browser_scenarios'] = {'total': len(BROWSER_SCENARIOS),
        'passed': sum(by_name.get(name, {}).get('status') == 'PASS' and by_name[name].get('storage_revalidated') is True for name in BROWSER_SCENARIOS),
        'not_executed': sum(name not in by_name for name in BROWSER_SCENARIOS),
        'results': [{key: value for key, value in item.items() if key in ('name', 'status', 'storage_revalidated', 'storage_verification_error', 'local_storage_hash')} for item in evidence.get('results', [])]}
    report['benchmark_full_chain'] = {'passed': sum(r['status'] == 'passed' for r in report['results']), 'total': len(report['results']),
                            'not_executed': sum(r['status'] == 'not_executed' for r in report['results'])}
    report['full_chain'] = {key: report['browser_scenarios'][key] for key in ('passed', 'total', 'not_executed')}


def summarize(report, cases):
    """所有指标分母由固定样例而非成功输出派生，缺失不能记通过。"""
    counts = Counter(row['status'] for row in report['results'])
    report['counts'] = {'total': len(cases), **{s: counts[s] for s in ('passed', 'failed', 'blocked', 'not_executed')}}
    report['model_calls'] = sum(row['model_calls'] for row in report['results'])
    eligibility = {'intent': lambda c: True, 'route': lambda c: c.get('critical'), 'protocol': lambda c: True,
                   'full_passthrough': lambda c: c.get('full_passthrough'), 'resolvable': lambda c: c.get('resolvable'),
                   'ambiguity_zero_guess': lambda c: c.get('preserve_ambiguity'), 'entity_preservation': lambda c: True}
    for name, eligible in eligibility.items():
        pairs = [(case, row) for case, row in zip(cases, report['results']) if eligible(case)]
        report['metrics'][name] = {'passed': sum(row['checks'].get(name) is True for _, row in pairs), 'total': len(pairs)}
    report['usage'] = {kind: sum(row['usage'].get(stage, {}).get(kind, 0) for row in report['results'] for stage in ('understanding', 'classification')) for kind in ('actual', 'estimated', 'actual_calls', 'estimated_calls')}


def main(argv=None):
    """缺省只写报告；live理解才创建固定配置的在线客户端。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=['understanding', 'chat'], default='understanding')
    parser.add_argument('--split', choices=['acceptance', 'development'], default='acceptance')
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--case-id')
    parser.add_argument('--previous', type=Path, action='append')
    parser.add_argument('--evidence', type=Path)
    args = parser.parse_args(argv)
    if args.output.exists():
        parser.error('output already exists; preserve original evidence and choose a fresh path')
    if args.mode == 'chat' and args.live and not args.evidence:
        parser.error('live chat imports --evidence; it never sends duplicate chats')
    def read(path):
        """读取已有报告，不覆盖证据。"""
        return json.loads(path.read_text(encoding='utf-8')) if path else None
    def save(report):
        """逐轮落盘保留已付费观测，意外中断也保留前轮证据。"""
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    async def run():
        """在线资源仅在显式授权路径拥有并关闭。"""
        import httpx
        async with httpx.AsyncClient() as client:
            model, name = None, None
            if args.live and args.mode == 'understanding':
                from app.config import load_settings
                from app.core.llm import create_model, model_with_output_budget
                settings = load_settings()
                name = settings.llm_model
                model = model_with_output_budget(create_model(settings, http_async_client=client,
                    reasoning_effort=settings.online_reasoning_effort), settings, 2048)
            return await evaluate(mode=args.mode, split=args.split, live=args.live, model=model, model_name=name,
                case_id=args.case_id, previous=[read(path) for path in args.previous or []], evidence=read(args.evidence), on_update=save)
    report = asyncio.run(run())
    save(report)
    print(json.dumps({key: report[key] for key in ('counts', 'model_calls', 'metrics', 'usage')}, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
