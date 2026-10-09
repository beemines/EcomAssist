# 冻结输入、公平比较四策略；默认只使用本次拥有的测试资源，台账长期保留。
import argparse
import asyncio
from contextlib import AsyncExitStack
from dataclasses import asdict
from hashlib import sha256
import json
import math
from pathlib import Path
from time import monotonic
from uuid import uuid4

import httpx
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from sqlalchemy import delete, select

from app.config import load_settings
from app.core.answer_validation import REFUSAL_TEXT, validate_answer
from app.core.errors import ServiceError
from app.core.evidence import build_evidence
from app.core.llm import create_model, model_with_output_budget
from app.core.prompts import build_grounded_answer_system_prompt
from app.core.sufficiency import SufficiencyService
from app.db.models import KnowledgeChunk
from app.db.session import Database
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
from app.knowledge.ingestion import import_document
from app.quality.repository import QualityRepository
from app.quality.types import FaithCaseInput
from app.repositories.knowledge import KnowledgeRepository, _record
from app.retrieval.milvus import HybridMilvusIndex
from app.retrieval.query import QueryPlanner
from app.retrieval.rerank import SiliconFlowReranker
from app.retrieval.service import RetrievalService, faq_payload
from evals.faithfulness import FaithfulnessJudge, JUDGE_VERSION, JUDGE_PROMPT
from evals.knowledge_recovery import OwnedRepository, attempt_cleanup, test_settings, timestamp, write_checkpoint
from evals.retrieval_metrics import choose_threshold, retrieval_metrics

STRATEGIES = ('dense', 'bm25', 'hybrid', 'hybrid_rerank')
BUCKETS = ('A_policy', 'B_model', 'C_colloquial', 'D_unanswerable', 'E_multi')
DOCUMENTS = ('demo-policy.md', 'demo-faq.md', 'demo-manual.md', 'retrieval-models.md')


# 保留错误因果类型而不序列化异常文字，避免密钥/供应商正文进入日志。
def failure_details(exc):
    """提取安全错误码和异常因果类型，不序列化供应商或敏感异常文字。"""
    result = dict(error_type=type(exc).__name__, error_code=getattr(exc, 'code', 'evaluation_error'))
    causes, seen, cause = [], set(), exc.__cause__
    while cause is not None and id(cause) not in seen:
        seen.add(id(cause))
        causes.append(type(cause).__name__)
        cause = cause.__cause__
    result['cause_types'] = causes
    return result


# 非流式结构化调用保留结束原因、usage与长度；流式答案不提前读取正文。
def model_http_hooks(report):
    """构造真实模型请求计数和非流式安全响应摘要钩子。"""
    requests = report.setdefault('model_requests', [])
    async def count(request):
        """按实际发送的模型请求计数，并记录操作类别和生效输出预算。"""
        body = json.loads(request.content)
        key = body.get('model', 'unknown')
        report['model_request_count'][key] = report['model_request_count'].get(key, 0) + 1
        row = dict(model=key, stream=body.get('stream', False),
                   max_output_tokens=body.get('max_tokens', body.get('max_completion_tokens')))
        prompt = body.get('messages', [{}])[0].get('content', '')
        row['operation'] = ('query' if '只整理本轮原话' in prompt else 'sufficiency' if '直接判断当前证据' in prompt
                            else 'judge' if '你是证据忠实度裁判' in prompt else 'generation' if row['stream']
                            else 'embedding' if 'input' in body else 'rerank' if 'documents' in body else 'unknown')
        if row['operation'] in ('query', 'sufficiency', 'judge'):
            content = body['messages'][-1]['content']
            row['question'] = content if row['operation'] == 'query' else json.loads(content)['question']
        request.extensions['evaluation_call_id'] = len(requests)
        requests.append(row)
    async def observe(response):
        """保留结束原因和用量；流式请求交给调用者读取，不提前缓冲。"""
        row = requests[response.request.extensions['evaluation_call_id']]
        row['http_status'] = response.status_code
        if row['stream']:
            return
        try:
            data = json.loads(await response.aread())
            if 'choices' in data:
                row['response_metadata'] = dict(model=data.get('model'), usage=data.get('usage'),
                    choices=[dict(finish_reason=c.get('finish_reason'),
                        content_characters=len(c.get('message', {}).get('content') or ''),
                        reasoning_characters=len(c.get('message', {}).get('reasoning_content') or ''))
                        for c in data['choices']])
        except (ValueError, TypeError):
            row['response_metadata_error'] = 'non_json_response'
    return {'request': [count], 'response': [observe]}


def map_gold(cases, rows):
    """按冻结原文三元组映射全部物理主键，缺失金标立即失败。"""
    triples = {}
    for row in rows:
        triples.setdefault((row.section_path, row.questions, row.answer), []).append(row.id)
    result = {}
    for case in cases:
        identifiers, duplicates, mappings = set(), 0, []
        for ref in case['gold_chunk_refs']:
            key = (ref['section_path'], ref['questions'], ref['answer'])
            ids = triples.get(key)
            if not ids:
                raise ValueError('missing gold triple for ' + case['eval_id'])
            identifiers.update(ids)
            duplicates += len(ids) - 1
            mappings.append(dict(ref=ref, ids=sorted(ids)))
        result[case['eval_id']] = dict(ids=sorted(identifiers), duplicates=duplicates, mappings=mappings)
    return result


# 每种指标保留自己的有效分母；失败不伪装成零或全量成功。
def summarize(records):
    """按桶和策略汇总独立有效分母，同时保留错误和未执行数量。"""
    groups = []
    for bucket in ('overall', *BUCKETS):
        for strategy in STRATEGIES:
            selected = [r for r in records if r['strategy'] == strategy and (bucket == 'overall' or r['bucket'] == bucket)]
            row = dict(bucket=bucket, strategy=strategy, total=len(selected),
                       attempted=sum(r['status'] != 'not_attempted' for r in selected),
                       completed=sum(r['status'] == 'ok' for r in selected),
                       errors=sum(r['status'] == 'error' for r in selected),
                       not_attempted=sum(r['status'] == 'not_attempted' for r in selected))
            for metric in ('recall_at_10', 'recall_at_50', 'mrr_at_10', 'prompt_recall', 'faithfulness'):
                values = [r[metric] for r in selected if r.get(metric) is not None]
                row[metric] = sum(values) / len(values) if values else None
                row[metric + '_n'] = len(values)
            no_gold = [r for r in selected if not r['gold_ids'] and 'refused' in r]
            row.update(refusal_accuracy=sum(r['refused'] for r in no_gold) / len(no_gold) if no_gold else None,
                       refusal_n=len(no_gold), wrong_allow=sum(not r['refused'] for r in no_gold),
                       all_required_count=sum(r.get('all_required', False) for r in selected))
            groups.append(row)
    return groups


def save_report(output, report):
    """原子保存逐题JSON检查点并生成同名总体与分桶Markdown报告。"""
    if output is None:
        return
    output.parent.mkdir(parents=True, exist_ok=True)
    if 'records' in report:
        report.update(attempted=sum(r['status'] != 'not_attempted' for r in report['records']),
                      not_attempted=sum(r['status'] == 'not_attempted' for r in report['records']),
                      errors=sum(r['status'] == 'error' for r in report['records']),
                      summary=summarize(report['records']))
    write_checkpoint(output, report)
    lines = ['# 混合检索评估', '', f"运行类型：{report['kind']}；模式：{report['mode']}；通过：{report.get('passed', False)}。",
             '', 'hybrid_rerank 额外使用冻结重排门槛，其他三策略仅内容自评；生成变化不能全部归因于排序。',
             '', f"已尝试 {report.get('attempted', 0)}；未执行 {report.get('not_attempted', 0)}；错误 {report.get('errors', 0)}；改写错误 {len(report.get('query_errors', []))}。",
             f"清理：{report.get('cleanup', 'pending')}。裁判版本：{JUDGE_VERSION}；拒答无断言的忠实度为 n/a。", '']
    if report.get('calibration'):
        lines += ['```json', json.dumps(report['calibration'], ensure_ascii=False, indent=2), '```', '']
    lines += ['各指标显示均值 / 有效分母；具体错误和未执行行见同名 JSON。', '',
              '| 桶 | 策略 | 完成/总数 | 错误/未执行 | Recall10 | Recall50 | MRR10 | Prompt覆盖 | Faithfulness | 无答案拒答率 |',
              '|---|---|---|---|---|---|---|---|---|---|']
    def show(row, metric):
        """格式化一个指标的均值和有效分母，空分母显示不适用。"""
        value = row.get(metric)
        return f"{value:.3f} / {row[metric + '_n']}" if value is not None else 'n/a / 0'
    for row in report.get('summary', []):
        refusal = f"{row['refusal_accuracy']:.3f} / {row['refusal_n']}" if row['refusal_accuracy'] is not None else 'n/a / 0'
        lines.append('| ' + ' | '.join([row['bucket'], row['strategy'], f"{row['completed']}/{row['total']}",
            f"{row['errors']}/{row['not_attempted']}", *[show(row, metric) for metric in (
                'recall_at_10', 'recall_at_50', 'mrr_at_10', 'prompt_recall', 'faithfulness')], refusal]) + ' |')
    output.with_suffix('.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')


def initial_report(cases, gold, *, database_mode, kind, mode='compare'):
    """为所有题目及策略预建未执行行，避免初始化失败丢失剩余数量。"""
    strategies = ('hybrid_rerank',) if mode == 'calibrate' else STRATEGIES
    return dict(kind=kind, mode=mode, runner_version='shared-rewrite-budget-v2',
        budget_accounting='Shared rewrite elapsed is charged independently to every strategy FAQ/chat deadline.',
        started_at=timestamp(), passed=False, query_errors=[], cleanup_errors=[],
        records=[dict(**case, ledger_eval_id=('T' if database_mode == 'test' else '') + case['eval_id'],
                      gold_ids=gold.get(case['eval_id'], {}).get('ids', []), strategy=strategy,
                      status='not_attempted', error_code='not_attempted') for case in cases for strategy in strategies])


# 复用线上消息/预算/自评/astream/校验；query并发最多2，题内四策略共享唯一计划。
async def evaluate_cases(cases, *, gold, planner, retrieval, model, judge, quality, settings,
                         database_mode, output, kind='actual', report=None):
    """复用完整线上检索、证据、自评、流式生成及裁判链公平比较四策略。"""
    report = report if report is not None else initial_report(cases, gold, database_mode=database_mode, kind=kind)
    report.update(gold_mapping=gold, threshold=settings.rerank_min_score,
        threshold_difference='hybrid_rerank uses calibrated score gate; other strategies content self-check only')
    sufficiency = SufficiencyService(model_with_output_budget(model, settings, settings.sufficiency_max_output_tokens),
        input_budget=settings.tool_input_token_budget,
        timeout=settings.sufficiency_timeout_seconds, minimum_rerank_score=settings.rerank_min_score)
    semaphore = asyncio.Semaphore(2)
    save_report(output, report)

    async def query(case):
        """在两个并发槽内执行单题唯一改写，并逐策略保存结果和故障。"""
        async with semaphore:
            rewrite_started = monotonic()
            try:
                plan = await planner.plan(case['query'])
            except Exception as exc:
                report['query_errors'].append(dict(eval_id=case['eval_id'], stage='rewrite',
                    rewrite_latency_seconds=monotonic() - rewrite_started, **failure_details(exc)))
                save_report(output, report)
                print(f"rewrite {case['eval_id']}: {type(exc).__name__}", flush=True)
                return
            # 四策略共享一次改写；分别扣除相同耗时，避免后续策略承担前一策略耗时。
            rewrite_elapsed = monotonic() - rewrite_started
            faq_remaining = max(0., settings.faq_timeout_seconds - rewrite_elapsed)
            chat_remaining = max(0., settings.chat_timeout_seconds - rewrite_elapsed)
            for strategy in STRATEGIES:
                record = next(r for r in report['records'] if r['eval_id'] == case['eval_id'] and r['strategy'] == strategy)
                record.update(status='running', error_code=None, standard=plan.standard, expansions=plan.expansions,
                    rewrite_latency_seconds=rewrite_elapsed, faq_remaining_seconds=faq_remaining,
                    chat_remaining_seconds=chat_remaining)
                started, stage = monotonic(), 'retrieval'
                save_report(output, report)
                try:
                    async with asyncio.timeout(chat_remaining):
                        async with asyncio.timeout(faq_remaining):
                            bundle = await retrieval.retrieve(case['query'], category=case.get('category'),
                                                               strategy=strategy, query_plan=plan)
                        ids = [m.chunk.id for m in bundle.matches]
                        candidates = [hit.id for hit in bundle.candidates]
                        gold_ids = set(record['gold_ids'])
                        record.update(ranked_ids=ids, candidate_ids=candidates,
                            candidate_scores=[asdict(h) for h in bundle.candidates],
                            ranked_scores=[dict(id=m.chunk.id, score=m.score, score_kind=m.score_kind) for m in bundle.matches],
                            recall_at_10=retrieval_metrics(ids, gold_ids, k=10)['recall'],
                            recall_at_50=retrieval_metrics(candidates, gold_ids, k=50)['recall'],
                            mrr_at_10=retrieval_metrics(ids, gold_ids, k=10)['mrr'],
                            all_required=bool(gold_ids) and gold_ids.issubset(ids))
                        stage = 'evidence'
                        # 完整单次FAQ工具申请，参数沿用本轮原话连续片段。
                        request = AIMessage('', tool_calls=[dict(name='query_faq', args={'keyword':case['query'][:128]}, id='eval-faq')])
                        packet = build_evidence(system=SystemMessage(build_grounded_answer_system_prompt()), turns=[],
                            current=HumanMessage(case['query']), request=request, payload=faq_payload(bundle),
                            budget=settings.tool_input_token_budget)
                        record.update(evidence=packet.payload, citations=[asdict(c) for c in packet.citations],
                            generation_input=[m.model_dump(mode='json') for m in packet.messages],
                            prompt_recall=retrieval_metrics([int(c.chunk_id) for c in packet.citations], gold_ids, k=10)['recall'])
                        stage = 'sufficiency'
                        decision = await sufficiency.check(case['query'], packet)
                        record.update(self_check=decision.model_dump(), refused=not decision.useful,
                                      refusal_correct=(not decision.useful) == case['expected_refusal'])
                        stage = 'generation'
                        text, finishes = '', set()
                        if decision.useful:
                            async for chunk in model.astream(packet.messages):
                                if chunk.tool_calls or chunk.invalid_tool_calls:
                                    raise ServiceError('invalid_answer', '最终模型申请工具。', 502)
                                text += chunk.text
                                finish = chunk.response_metadata.get('finish_reason')
                                if finish:
                                    finishes.add(finish)
                        else:
                            text, finishes = REFUSAL_TEXT, {'stop'}
                        record.update(answer=text, finish_reasons=sorted(finishes))
                        validate_answer(text, finishes, packet, decision)
                        stage = 'judge'
                        judgment = await judge.judge(case['query'], text, packet.citations)
                        record.update(judge=judgment, faithfulness=judgment['score'])
                        unsupported = [c for c in judgment['claims'] if c['support'] is False]
                        if unsupported:
                            stage = 'ledger'
                            await quality.record_fabrication(FaithCaseInput(record['ledger_eval_id'], case['bucket'],
                                case['query'], strategy, text, json.dumps(unsupported, ensure_ascii=False),
                                record['citations'], settings.llm_model))
                            record['fabrication_persisted'] = True
                        record['status'] = 'ok'
                except Exception as exc:
                    record.update(status='error', error_stage=stage, failure_details=failure_details(exc), error_type=type(exc).__name__,
                        error_code='judge_error' if stage == 'judge' else getattr(exc, 'code', stage + '_error'))
                finally:
                    record['latency_seconds'] = monotonic() - started + rewrite_elapsed
                    save_report(output, report)
                    print(f"{case['eval_id']} {strategy}: {record['status']} {record.get('error_code') or ''}", flush=True)
    await asyncio.gather(*(query(case) for case in cases))
    report.update(passed=not report['query_errors'] and all(r['status'] == 'ok' for r in report['records']), finished_at=timestamp())
    save_report(output, report)
    return report


async def calibrate_cases(cases, *, gold, planner, retrieval, output, report):
    """逐题收集真实有限重排分；八题全部合法后才选择拒答门槛。"""
    samples = []
    for case, record in zip(cases, report['records']):
        started = monotonic()
        try:
            plan = await planner.plan(case['query'])
        except Exception as exc:
            report['query_errors'].append(dict(eval_id=case['eval_id'], stage='rewrite', **failure_details(exc)))
            save_report(output, report)
            continue
        record.update(status='running', standard=plan.standard, expansions=plan.expansions, error_code=None)
        save_report(output, report)
        try:
            bundle = await retrieval.retrieve(case['query'], category=case.get('category'),
                                               strategy='hybrid_rerank', query_plan=plan)
            score = max((m.score for m in bundle.matches), default=None)
            if score is None or not math.isfinite(score):
                raise ValueError('calibration needs observed finite rerank score')
            ids = [m.chunk.id for m in bundle.matches]
            sufficient = case['evidence_sufficient'] and set(record['gold_ids']).issubset(ids)
            samples.append(dict(eval_id=case['eval_id'], score=score, sufficient=sufficient))
            record.update(status='ok', ranked_ids=ids, candidate_ids=[h.id for h in bundle.candidates],
                evidence=faq_payload(bundle), best_score=score, sufficient=sufficient,
                annotated_sufficient=case['evidence_sufficient'], gold_covered=set(record['gold_ids']).issubset(ids))
        except Exception as exc:
            record.update(status='error', error_stage='retrieval', failure_details=failure_details(exc), error_type=type(exc).__name__,
                          error_code=getattr(exc, 'code', 'calibration_error'))
        record['latency_seconds'] = monotonic() - started
        save_report(output, report)
        print(f"calibrate {case['eval_id']}: {record['status']}", flush=True)
    if len(samples) == len(cases) == 8 and not report['query_errors']:
        report.update(calibration=choose_threshold(samples), passed=True)
    else:
        report.update(calibration=None, calibration_error='all eight actual valid samples required; no partial recommendation')
    save_report(output, report)


class ScopedRepository(OwnedRepository):
    # 所有作业读回和回填都局限本次拥有主键，不消费测试库其他任务。
    async def done_page(self, *, after_id=0, limit=20):
        """只分页读取本次拥有的已完成知识，隔离其他测试任务数据。"""
        async with self.database.session() as session:
            rows = (await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.id.in_(self.ids),
                KnowledgeChunk.id > after_id, KnowledgeChunk.vectorize_status == 'done')
                .order_by(KnowledgeChunk.id).limit(limit))).all()
            return [_record(r) for r in rows]

    async def get_done(self, ids):
        """回填只允许本次拥有主键，不将外部命中纳入评估正文。"""
        return await super().get_done([identifier for identifier in ids if identifier in self.ids])


# HTTP请求钩子按实际发出次数计数，包含失败；不记录请求正文/地址/密钥。
async def evaluate(cases, *, mode, database_mode, output):
    """拥有测试资源并冻结输入，调用真实评估后保留台账且独立清理临时资源。"""
    report = initial_report(cases, {}, database_mode=database_mode, kind='actual', mode=mode)
    report.update(cleanup='pending', model_request_count={}, database_mode=database_mode,
                  judge_version=JUDGE_VERSION, judge_prompt=JUDGE_PROMPT, owned_ids=[])
    save_report(output, report)
    database, index, ids = None, None, []
    try:
        settings = test_settings() if database_mode == 'test' else load_settings()
        report.update(database=f'{settings.mysql_host}:{settings.mysql_port}/{settings.mysql_database}',
            online_model=settings.llm_model, embedding_model=settings.embedding_model, rerank_model=settings.rerank_model,
            input_budget=settings.tool_input_token_budget, online_output_budget=settings.max_output_tokens,
            query_output_budget=settings.query_max_output_tokens, sufficiency_output_budget=settings.sufficiency_max_output_tokens,
            query_timeout_seconds=settings.query_timeout_seconds, sufficiency_timeout_seconds=settings.sufficiency_timeout_seconds,
            faq_timeout_seconds=settings.faq_timeout_seconds, chat_timeout_seconds=settings.chat_timeout_seconds,
            judge_input_budget=settings.faith_judge_input_token_budget, judge_output_budget=settings.faith_judge_max_output_tokens,
            retries=0, threshold=settings.rerank_min_score,
            corpus_hashes={name:sha256((Path('knowledge-docs') / name).read_bytes()).hexdigest() for name in DOCUMENTS},
            cases_sha256=sha256(json.dumps(cases, sort_keys=True,ensure_ascii=False).encode()).hexdigest())
        if mode == 'compare' and settings.rerank_min_score is None:
            raise ServiceError('missing_calibrated_threshold', '比较需要八题有效校准产生的有限重排门槛。', 422)
        database = Database(settings.database_url)
        collection = 'knowledge_test_' + uuid4().hex if database_mode == 'test' else settings.milvus_collection
        report['collection'] = collection
        async with AsyncExitStack() as resources:
            http = httpx.AsyncClient(event_hooks=model_http_hooks(report))
            resources.push_async_callback(attempt_cleanup, report['cleanup_errors'], 'shared_http_close', http.aclose)
            embedder = SiliconFlowEmbedder(settings, http_client=http)
            reranker = SiliconFlowReranker(settings, http_client=http)
            index = HybridMilvusIndex(str(settings.milvus_uri), collection=collection, timeout=settings.milvus_timeout_seconds)
            resources.push_async_callback(attempt_cleanup, report['cleanup_errors'], 'index_close', index.aclose)
            model = create_model(settings, http_async_client=http)
            # 每个实例构造成功后立即注册，后续构造失败也不泄漏已拥有的客户端。
            resources.callback(model.root_client.close)
            judge_model = create_model(settings.model_copy(update={'max_output_tokens':settings.faith_judge_max_output_tokens}), http_async_client=http)
            # 异步SDK借用上方HTTP，由唯一所有者关闭；独立同步客户端各关闭一次。
            resources.callback(judge_model.root_client.close)
            try:
                repository = KnowledgeRepository(database)
                if database_mode == 'test':
                    for name in DOCUMENTS:
                        ids.extend(await import_document(Path('knowledge-docs') / name, 'faq', repository))
                        report['owned_ids'] = list(ids)
                        save_report(output, report)
                    repository = ScopedRepository(database, ids)
                    await index.ensure_collection()
                    report['vectorized_count'] = await HybridKnowledgeJobs(repository, embedder, index).vectorize_pending()
                    rows = await repository.get_done(ids)
                else:
                    await index.ensure_collection(create_if_missing=False)
                    rows, cursor = [], 0
                    while batch := await repository.done_page(after_id=cursor):
                        rows.extend(batch)
                        cursor = batch[-1].id
                gold = map_gold(cases, rows)
                report.update(gold_mapping=gold, frozen_corpus=[asdict(r) for r in rows])
                for record in report['records']:
                    record['gold_ids'] = gold[record['eval_id']]['ids']
                planner = QueryPlanner(model_with_output_budget(model,settings,settings.query_max_output_tokens),
                    settings.tool_input_token_budget, timeout=settings.query_timeout_seconds)
                retrieval = RetrievalService(repository, embedder, index, planner, reranker)
                if mode == 'calibrate':
                    await calibrate_cases(cases, gold=gold, planner=planner, retrieval=retrieval, output=output, report=report)
                else:
                    await evaluate_cases(cases, gold=gold, planner=planner, retrieval=retrieval, model=model,
                        judge=FaithfulnessJudge(judge_model, settings.faith_judge_input_token_budget),
                        quality=QualityRepository(database), settings=settings, database_mode=database_mode,
                        output=output, kind='actual', report=report)
            finally:
                if database_mode == 'test':
                    async def clean_rows():
                        """只在短事务中删除本次导入的知识，不删除编造台账。"""
                        async with database.session() as session, session.begin():
                            await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id.in_(ids)))
                    await attempt_cleanup(report['cleanup_errors'], 'owned_knowledge_rows', clean_rows)
                    async def clean_collection():
                        """在固定清理期限内删除本次UUID集合，保留其他集合。"""
                        async with asyncio.timeout(index.timeout):
                            if await index._call('has_collection', collection):
                                await index._call('drop_collection', collection)
                    await attempt_cleanup(report['cleanup_errors'], 'owned_collection', clean_collection)
    except Exception as exc:
        report.update(passed=False, error_code=getattr(exc, 'code', 'initialization_error'),
                      failure_details=failure_details(exc), error_type=type(exc).__name__)
    finally:
        if database is not None:
            await attempt_cleanup(report['cleanup_errors'], 'database_dispose', database.dispose)
        report.update(cleanup='failed' if report['cleanup_errors'] else 'owned_temporary_resources_removed_ledger_preserved'
                      if database_mode == 'test' else 'configured_resources_and_ledger_preserved', finished_at=timestamp())
        if report['cleanup_errors']:
            report['passed'] = False
        save_report(output, report)
    return report


def main(argv=None):
    """解析默认测试库的校准或比较CLI，保留历史报告并以非零退出表示错误。"""
    parser = argparse.ArgumentParser(description='真实八题校准与四策略合成数据评估')
    parser.add_argument('--mode', required=True, choices=('calibrate', 'compare'))
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--cases', type=Path)
    parser.add_argument('--database', default='test', choices=('test', 'configured'))
    args = parser.parse_args(argv)
    if args.output.exists() or args.output.with_suffix('.md').exists():
        parser.error('output already exists; choose a new report path to preserve history')
    path = args.cases or Path('evals/retrieval_calibration.jsonl' if args.mode == 'calibrate' else 'evals/retrieval_cases.jsonl')
    cases = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    if len({c['eval_id'] for c in cases}) != len(cases):
        parser.error('duplicate eval_id')
    report = asyncio.run(evaluate(cases, mode=args.mode, database_mode=args.database, output=args.output))
    print(json.dumps({key:report.get(key) for key in ('passed','attempted','not_attempted','errors','model_request_count','calibration','error_code')}, ensure_ascii=False))
    return 0 if report['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
