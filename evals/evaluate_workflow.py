"""固定 Workflow 有界验收；默认只生成未执行报告，真实调用须显式 --live。"""
import argparse
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path

from app.workflow.intent import route_intent, social_fast_path


ROOT = Path(__file__).resolve().parents[1]
CHAT_CASES = [
    {'id': 'policy', 'question': '退货政策是什么？', 'expected_intent': '退款退货'},
    {'id': 'logistics', 'question': '订单1001的包裹到哪里了？', 'expected_intent': '物流'},
    {'id': 'two-step', 'question': '先查订单1001的状态，再按订单查物流', 'expected_intent': '物流'},
    {'id': 'complaint', 'question': '我要投诉客服态度', 'expected_intent': '投诉'},
    {'id': 'social', 'question': '你好', 'expected_intent': '闲聊'},
    {'id': 'usage-help', 'question': '新买的商品不太会用，能帮我看看吗？', 'expected_intent': '售后'},
    {'id': 'mh-lp200', 'question': 'MH-LP200 能装多少猫砂？', 'expected_intent': '商品咨询'},
    {'id': 'out-of-library', 'question': '你们提供宠物洗澡美容服务吗，具体价格是多少？', 'expected_intent': '商品咨询'},
]
STATUSES = ('passed', 'misclassified', 'refused', 'errors', 'timeouts', 'truncated', 'not_executed')


def load_intent_cases():
    """读取已审定的21题七意图与3题边界金标，不传给生成模型。"""
    return [json.loads(line) for line in (ROOT / 'evals/workflow_intent_cases.jsonl').read_text(
        encoding='utf-8').splitlines() if line.strip()]


def report_for(mode, cases, execution):
    """逐题保存真实状态分母与调用统计，未执行默认不能通过。"""
    counts = {'total': len(cases), 'attempted': sum(row['status'] != 'not_executed' for row in cases)}
    counts.update({status: sum(row['status'] == status for row in cases) for status in STATUSES})
    return {'title': f"Workflow {mode} 验收：{'真实' if execution == 'live' else '受控（未证明真实模型质量）'}",
        'execution': execution, 'mode': mode, 'created_at': datetime.now(timezone.utc).isoformat(),
        'counts': counts, 'model_calls': sum(row.get('model_calls', 0) for row in cases),
        'usage_scope': '32000仅统计意图+Agent决策/最终；query改写及充分性使用原独立预算/期限，未计入该账本。',
        'cases': cases}


def unexecuted_report(mode):
    """无需配置或模型，输出所有固定场景的未执行状态。"""
    cases = load_intent_cases() if mode == 'intent' else CHAT_CASES
    return report_for(mode, [{**case, 'status': 'not_executed', 'model_calls': 0} for case in cases], 'controlled')


def failure_status(exc):
    """区分超时、显式截断与错误；非法输出不猜测为知识拒答。"""
    if isinstance(exc, TimeoutError) or getattr(exc, 'code', None) == 'upstream_timeout':
        return 'timeouts'
    if getattr(exc, 'finish_reason', None) == 'length':
        return 'truncated'
    return 'errors'


async def evaluate_intent(cases, classify, *, execution):
    """每个非社交原问题至多一次，首次失败停止并保留后续未执行。"""
    rows, stopped = [], False
    for case in cases:
        row = {**case, 'status': 'not_executed', 'model_calls': 0}
        if not stopped:
            try:
                if social_fast_path(case['question']):
                    actual = {'intent': '闲聊', 'usage': {'actual_calls': 0, 'estimated_calls': 0}}
                else:
                    row['model_calls'] = 1
                    actual = await classify(case['question'])
                row.update(actual_intent=actual['intent'], actual_route=route_intent(actual['intent']),
                    usage=actual['usage'])
                row['status'] = 'passed' if (row['actual_intent'] == case['expected_intent']
                    and row['actual_route'] == case['expected_route']) else 'misclassified'
                stopped = row['status'] != 'passed'
            except Exception as exc:
                row.update(status=failure_status(exc), error={'type': type(exc).__name__,
                    'code': getattr(exc, 'code', None)})
                stopped = True
        rows.append(row)
    return report_for('intent', rows, execution)


def chat_outcome(events, state):
    """只有合法完成根快照配合done可分类，错误永不冒充资料不足。"""
    errors = [event['data'] for event in events if event['event'] == 'error']
    if errors:
        return 'timeouts' if errors[0].get('code') == 'upstream_timeout' else 'errors'
    done = [event for event in events if event['event'] == 'done']
    if not done:
        return 'truncated'
    if len(done) != 1 or events[-1]['event'] != 'done' or state.get('turn_status') != 'completed':
        return 'errors'
    return 'refused' if state.get('quality', {}).get('useful') is False else 'passed'


def case_outcome(case_id, row):
    """对合法终态再核对固定场景语义，拒答保留单独统计且不计通过。"""
    status = row['status']
    if status not in ('passed', 'refused'):
        return status
    if row.get('browser_status') != 'PASS':
        return 'errors'
    trace = [item['name'] for item in row.get('tool_trace', [])]
    if case_id == 'social' and (row['model_calls'] != 0 or trace):
        return 'errors'
    if case_id == 'out-of-library' and status != 'refused':
        return 'errors'
    if case_id == 'two-step' and trace != ['query_order', 'query_logistics']:
        return 'errors'
    return status


def recorded_usage(values):
    """父子图共享累计账本，选择最大已持久化值而非重复累加分类成本。"""
    return max(values, key=lambda value: value.get('actual', 0) + value.get('estimated', 0),
        default={'actual': 0, 'estimated': 0, 'actual_calls': 0, 'estimated_calls': 0})


async def live_intent():
    """沿用已授权在线配置、2048上限与零重试，关闭自有HTTP客户端。"""
    import httpx
    from app.config import load_settings
    from app.core.llm import create_model, model_with_output_budget
    from app.workflow.intent import IntentClassifier
    settings = load_settings()
    async with httpx.AsyncClient() as client:
        model = create_model(settings, http_async_client=client, reasoning_effort=settings.online_reasoning_effort)
        classifier = IntentClassifier(model_with_output_budget(model, settings, settings.intent_max_output_tokens),
            input_budget=settings.tool_input_token_budget, timeout_seconds=settings.llm_timeout_seconds)

        async def classify(question):
            """只发送原话，金标仅在返回后用于报告比较。"""
            intent = await classifier.classify(question)
            return {'intent': intent, 'usage': dict(classifier.usage)}

        return await evaluate_intent(load_intent_cases(), classify, execution='live')


async def live_chat_evidence(evidence_path):
    """读取真实浏览器原始SSE，独立核对自有SQL流水与官方SQLite根状态。"""
    from sqlalchemy import select
    from app.config import load_settings
    from app.db.models import Conversation, LowConfidenceQuestion, Message, Ticket
    from app.db.session import Database
    from app.workflow.persistence import checkpoint_config, checkpoint_path, open_checkpointer
    settings = load_settings()
    evidence = json.loads(Path(evidence_path).read_text(encoding='utf-8'))
    if evidence.get('mode') != 'live' or not evidence.get('run_id') or evidence.get('url') != 'http://127.0.0.1:8002/':
        raise ValueError('需要自有8002真实浏览器证据')
    database = Database(settings.database_url)
    rows = []
    try:
        async with open_checkpointer(checkpoint_path(settings, ROOT)) as saver:
            for case in CHAT_CASES:
                found = next((item for item in evidence['results'] if item['name'] == case['id']), None)
                row = {**case, 'status': 'not_executed', 'model_calls': 0}
                if found is not None and found.get('status') != 'NOT_EXECUTED':
                    row.update(found)
                    conversation_id = found.get('conversation_id')
                    events = found.get('events', [])
                    if not conversation_id:
                        row['status'] = 'errors'
                    else:
                        saved = await saver.aget_tuple(checkpoint_config(conversation_id))
                        state = saved.checkpoint['channel_values'] if saved else {}
                        checkpoints, namespaces = [], set()
                        async for child in saver.alist({'configurable': {'thread_id': conversation_id}}, limit=30):
                            namespace = child.config['configurable'].get('checkpoint_ns', '')
                            if namespace in namespaces:
                                continue
                            namespaces.add(namespace)
                            values = child.checkpoint['channel_values']
                            checkpoints.append({'namespace': namespace,
                                'checkpoint_id': child.config['configurable']['checkpoint_id'],
                                'nodes_seen': list(child.checkpoint.get('versions_seen', {})),
                                'pending_channels': [channel for _, channel, _ in child.pending_writes],
                                'usage': values.get('usage', {}), 'decision_count': values.get('decision_count'),
                                'tool_call_count': values.get('tool_call_count'),
                                'tool_trace': values.get('tool_trace', [])})
                        async with database.session() as session:
                            conversation = await session.get(Conversation, int(conversation_id))
                            if conversation is None or conversation.user_id != 'demo-user':
                                raise ValueError('浏览器自有会话不存在或身份异常')
                            messages = (await session.scalars(select(Message).where(
                                Message.conversation_id == int(conversation_id)).order_by(Message.id))).all()
                            tickets = (await session.scalars(select(Ticket).where(
                                Ticket.conversation_id == int(conversation_id)))).all()
                            refusals = (await session.scalars(select(LowConfidenceQuestion).where(
                                LowConfidenceQuestion.conversation_id == int(conversation_id)))).all()
                        row.update(status=chat_outcome(events, state), actual_intent=state.get('intent'),
                            browser_status=found['status'],
                            route=state.get('route'), tool_trace=max([item['tool_trace'] for item in checkpoints], key=len, default=[]),
                            node_checkpoint_versions=list(saved.checkpoint.get('versions_seen', {})) if saved else [],
                            checkpoints=checkpoints,
                            decision_count=max((item['decision_count'] or 0 for item in checkpoints), default=0),
                            tool_call_count=max((item['tool_call_count'] or 0 for item in checkpoints), default=0),
                            usage=recorded_usage([item['usage'] for item in checkpoints]), quality=state.get('quality', {}),
                            citations=state.get('citations', []), turn_status=state.get('turn_status'),
                            sql_messages=[{'id': str(message.id), 'role': message.role,
                                'content': message.content, 'tool_calls': message.tool_calls,
                                'tool_call_id': message.tool_call_id} for message in messages],
                            tickets=[{'ticket_no': ticket.ticket_no, 'description': ticket.description,
                                'ticket_type': ticket.ticket_type} for ticket in tickets],
                            refusal_rows=[{'id': str(refusal.id), 'raw_question': refusal.raw_question,
                                'source': refusal.source} for refusal in refusals],
                            ticket_delta=len(tickets), checkpoint_id=saved.config['configurable']['checkpoint_id'] if saved else None)
                        row['model_calls'] = row['usage'].get('actual_calls', 0) + row['usage'].get('estimated_calls', 0)
                        row['model_calls_scope'] = '已持久化账本；失败调用本身的用量未保存，不能作为全部收费调用数'
                        row['usage_complete'] = row['status'] in ('passed', 'refused')
                        if row['status'] in ('passed', 'refused'):
                            done = [event['data'] for event in events if event['event'] == 'done'][0]
                            if (done['message_id'] != state.get('final_message_id')
                                    or done['conversation_id'] != conversation_id
                                    or not any(str(message.id) == done['message_id'] and message.role == 'assistant' for message in messages)
                                    or not any(message.role == 'user' and message.content == case['question'] for message in messages)):
                                row['status'] = 'errors'
                            elif state.get('intent') != case['expected_intent']:
                                row['status'] = 'misclassified'
                            elif found['status'] != 'PASS':
                                row['status'] = 'errors'
                        row['status'] = case_outcome(case['id'], row)
                rows.append(row)
    finally:
        await database.dispose()
    report = report_for('chat', rows, 'live')
    report.update(run_id=evidence['run_id'], browser_evidence=str(evidence_path), restart=evidence.get('restart'))
    report['supplemental'] = [item for item in evidence['results'] if item['name'] not in {case['id'] for case in CHAT_CASES}]
    return report


async def owned_sql_snapshot(conversation_id):
    """只读当前浏览器创建的单一会话，供按钮前后及重启阶段比较真实增量。"""
    from sqlalchemy import select
    from app.config import load_settings
    from app.db.models import Conversation, Message, Ticket
    from app.db.session import Database
    if not conversation_id.isdecimal() or not 0 < int(conversation_id) < 2**64:
        raise ValueError('invalid owned conversation id')
    database = Database(load_settings().database_url)
    try:
        async with database.session() as session:
            conversation = await session.get(Conversation, int(conversation_id))
            if conversation is None or conversation.user_id != 'demo-user':
                raise ValueError('not a browser-created conversation')
            messages = (await session.scalars(select(Message).where(
                Message.conversation_id == int(conversation_id)).order_by(Message.id))).all()
            tickets = (await session.scalars(select(Ticket).where(Ticket.conversation_id == int(conversation_id)))).all()
        return {'conversation_id': conversation_id, 'conversation_status': conversation.status,
            'messages': [{'id': str(message.id), 'role': message.role, 'content': message.content,
                'tool_calls': message.tool_calls, 'tool_call_id': message.tool_call_id} for message in messages],
            'tickets': [{'ticket_no': ticket.ticket_no, 'description': ticket.description,
                'ticket_type': ticket.ticket_type} for ticket in tickets]}
    finally:
        await database.dispose()


def main():
    """显式真实开关防止默认CLI付费，写入独立输出且失败返回非零。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode', choices=('intent', 'chat'), required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--live', action='store_true')
    parser.add_argument('--evidence', type=Path)
    parser.add_argument('--snapshot-conversation')
    args = parser.parse_args()
    if args.snapshot_conversation:
        if not args.live or args.mode != 'chat':
            parser.error('单会话只读SQL快照须显式 --live --mode chat')
        snapshot = asyncio.run(owned_sql_snapshot(args.snapshot_conversation))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        return 0
    if args.live and args.mode == 'chat' and not args.evidence:
        parser.error('真实chat只读取已执行的浏览器证据，必须提供 --evidence，避免重复收费')
    report = (asyncio.run(live_intent()) if args.live and args.mode == 'intent'
        else asyncio.run(live_chat_evidence(args.evidence)) if args.live else unexecuted_report(args.mode))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'execution': report['execution'], 'counts': report['counts'], 'model_calls': report['model_calls']}, ensure_ascii=False))
    return 1 if any(report['counts'][key] for key in ('misclassified', 'errors', 'timeouts', 'truncated')) else 0


if __name__ == '__main__':
    raise SystemExit(main())
