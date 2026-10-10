"""借用隔离资源执行四策略公平比较，保存诚实的逐阶段检查点。"""

import asyncio
from collections.abc import Mapping, Sequence
from dataclasses import asdict
import json

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.config import Settings
from app.core.answer_validation import (REFUSAL_TEXT, FinalAnswerStream, close_answer_stream,
                                        ensure_answer_active, validate_answer)
from app.core.evidence import build_evidence
from app.core.llm import model_with_output_budget
from app.core.prompts import build_grounded_answer_system_prompt
from app.core.sufficiency import SufficiencyService
from app.quality.types import FaithCaseInput
from app.rag_evaluation.contracts import EvalCase, FrozenDataset
from app.rag_evaluation.audit import build_source_map
from app.rag_evaluation.judgment import GenerationJudge, JudgeError
from app.rag_evaluation.report import CASE_FIELDS, STRATEGIES, case_metrics
from app.rag_evaluation.resources import OwnedResources
from app.rag_evaluation.store import RunStore, StoreError
from app.retrieval.service import RetrievalService, faq_payload
from app.retrieval.types import validate_category


def _seed(case: EvalCase, strategy: str, id_map: Mapping[str, int], source_map_id: str | None = None) -> dict:
    """复制完整元数据并映射金标，生成与检索只取得题面及实际证据。"""
    row = dict.fromkeys(CASE_FIELDS)
    row.update(eval_id=case.eval_id, strategy=strategy, bucket=case.bucket, difficulty=case.difficulty,
        category=case.category, should_refuse=case.should_refuse, query=case.query,
        status='not_attempted', stage='rewrite', mapped_groups=[{
            'group_id': group.group_id,
            'alternatives': [[id_map[key] for key in bundle] for bundle in group.alternatives]
        } for group in case.groups])
    row['audit'] = None if source_map_id is None else dict(audit_version=1, source_map_id=source_map_id,
        gold_groups=[{'group_id': group.group_id, 'alternatives': [list(bundle) for bundle in group.alternatives]}
            for group in case.groups],
        answer_points=[dict(point_id=point.point_id, text=point.text, condition=point.condition,
            aliases=list(point.aliases)) for point in case.points], candidate_ranking=None, final_ranking=None)
    return row


def _failure(exc: Exception, stage: str) -> dict:
    """只保存安全阶段标识与固定消息，异常原文不会成为公共错误。"""
    return {'code': stage + '_error', 'type': type(exc).__name__, 'message': '该阶段执行失败'}


def _storage_failure(exc: BaseException) -> StoreError | None:
    """穿过 SDK/服务异常包装定位计数发布故障，避免把本地写盘故障当模型错误。"""
    pending, seen = [exc], set()
    while pending:
        current = pending.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))
        if isinstance(current, StoreError):
            return current
        pending.extend(link for link in (current.__cause__, current.__context__) if link is not None)
    return None


class EvaluationRunner:
    """每题一次改写、固定四路顺序；题并发2，资源和运行终态由 manager 拥有。"""

    def __init__(self, resources: OwnedResources, store: RunStore, run_id: str, settings: Settings):
        """只借用已准备资源，不创建客户端或第二套实际请求计数器。"""
        self.resources, self.store, self.run_id, self.settings = resources, store, run_id, settings
        self.retrieval = RetrievalService(resources.repository, resources.embedder, resources.index,
                                          resources.planner, resources.reranker)

    async def _publish(self, row: dict) -> None:
        """阶段产物完成后原子保存记录及重算分数，再发布当前运行阶段。"""
        row['metrics'] = None
        row['metrics'] = case_metrics(row)
        await self.store.put_case(self.run_id, row)
        await self.store.update(self.run_id, {'stage': row['stage']})

    def _active(self, cancel_event: asyncio.Event, deadline: float | None = None) -> None:
        """每个 awaited 依赖后复查取消及绝对期限，吞取消不能转成成功。"""
        if cancel_event.is_set():
            raise asyncio.CancelledError()
        ensure_answer_active(deadline)

    async def run_cases(self, dataset: FrozenDataset, id_map: Mapping[str, int],
                        case_ids: Sequence[str], cancel_event: asyncio.Event) -> str:
        """先完整 seed 后执行；只返回评估 outcome，cleanup/终态/lease 由 manager 处理。"""
        by_id = {case.eval_id: case for case in dataset.cases}
        selected = tuple(case_ids)
        if len(set(selected)) != len(selected) or any(key not in by_id for key in selected):
            raise ValueError('invalid evaluation case selection')
        cases = tuple(by_id[key] for key in selected)
        source_map = build_source_map(dataset, id_map)
        rows = {(case.eval_id, strategy): _seed(case, strategy, id_map, source_map['source_map_id'])
                for case in cases for strategy in STRATEGIES}
        # 在任何收费阶段前核验全部计划，不能悄悄覆盖旧完成记录或续跑。
        manifest = await self.store.get(self.run_id)
        if set(map(tuple, manifest['case_keys'])) != set(rows) or await self.store.records(self.run_id):
            raise ValueError('evaluation plan is not a fresh matching run')
        for case in cases:
            validate_category(case.category)
        await self.store.put_source_map(self.run_id, source_map)
        for row in rows.values():
            await self.store.put_case(self.run_id, row)
        if cancel_event.is_set():
            return 'cancelled'
        sufficiency = SufficiencyService(model_with_output_budget(self.resources.model, self.settings,
            self.settings.sufficiency_max_output_tokens), input_budget=self.settings.tool_input_token_budget,
            timeout=self.settings.sufficiency_timeout_seconds, minimum_rerank_score=self.settings.rerank_min_score,
            mode='content_ablation')
        judge = GenerationJudge(self.resources.judge_model, self.settings.faith_judge_input_token_budget,
                                timeout=self.settings.llm_timeout_seconds)
        semaphore = asyncio.Semaphore(2)
        tasks = [asyncio.create_task(self._query(case, rows, semaphore, sufficiency, judge, cancel_event))
                 for case in cases]
        completion = asyncio.gather(*tasks)
        cancellation = asyncio.create_task(cancel_event.wait())
        cancelled = False
        try:
            done, _ = await asyncio.wait((completion, cancellation), return_when=asyncio.FIRST_COMPLETED)
            cancelled = cancellation in done and cancel_event.is_set()
            if cancelled:
                for task in tasks:
                    task.cancel()
            await completion
        except asyncio.CancelledError:
            cancelled = True
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        finally:
            cancellation.cancel()
            await asyncio.gather(cancellation, return_exceptions=True)
            # 磁盘故障也必须收回所有任务，不能留下继续收费的后台工作。
            for task in tasks:
                if not task.done():
                    task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
        if cancelled or cancel_event.is_set():
            return 'cancelled'
        return 'completed' if all(row['status'] == 'completed' for row in rows.values()) else 'completed_with_errors'

    async def _query(self, case: EvalCase, rows: dict, semaphore: asyncio.Semaphore,
                     sufficiency: SufficiencyService, judge: GenerationJudge,
                     cancel_event: asyncio.Event) -> None:
        """dense先进入共享改写；成功后各路按顺序进入，未进入路线始终未执行。"""
        async with semaphore:
            self._active(cancel_event)
            row = rows[(case.eval_id, 'dense')]
            row.update(status='running', stage='rewrite')
            rewrite_start = asyncio.get_running_loop().time()
            try:
                await self._publish(row)
                # 阶段期限与借用服务同时开始；已发布检查点之后才作最后出站前复查。
                rewrite_deadline = min(
                    asyncio.get_running_loop().time() + self.settings.query_timeout_seconds,
                    rewrite_start + self.settings.faq_timeout_seconds,
                    rewrite_start + self.settings.chat_timeout_seconds)
                self._active(cancel_event, rewrite_deadline)
                with self.resources.requests.stage('rewrite'):
                    plan = await self.resources.planner.plan(case.query)
                # 内层 timeout 可能吞取消并 uncancel；保留的绝对期限仍可拒绝迟到结果。
                self._active(cancel_event, rewrite_deadline)
            except StoreError:
                # 检查点故障属于运行级失败，不能伪造四条模型错误后继续收费。
                raise
            except asyncio.CancelledError:
                row.update(status='cancelled', elapsed_ms=(asyncio.get_running_loop().time() - rewrite_start) * 1000)
                await self._publish(row)
                raise
            except Exception as exc:
                storage_error = _storage_failure(exc)
                if storage_error is not None:
                    raise storage_error from exc
                try:
                    self._active(cancel_event)
                except asyncio.CancelledError:
                    row.update(status='cancelled',
                        elapsed_ms=(asyncio.get_running_loop().time() - rewrite_start) * 1000)
                    await self._publish(row)
                    raise
                elapsed = (asyncio.get_running_loop().time() - rewrite_start) * 1000
                for strategy in STRATEGIES:
                    failed = rows[(case.eval_id, strategy)]
                    failed.update(status='rewrite_error', error=_failure(exc, 'rewrite'), elapsed_ms=elapsed)
                    await self._publish(failed)
                return
            rewrite_elapsed = asyncio.get_running_loop().time() - rewrite_start
            for strategy in STRATEGIES:
                self._active(cancel_event)
                row = rows[(case.eval_id, strategy)]
                row.update(status='running', stage='retrieval', query_plan=plan.model_dump())
                await self._route(case, row, plan, rewrite_elapsed, sufficiency, judge, cancel_event)

    async def _route(self, case: EvalCase, row: dict, plan, rewrite_elapsed: float,
                     sufficiency: SufficiencyService, judge: GenerationJudge,
                     cancel_event: asyncio.Event) -> None:
        """每路独立扣共享改写耗时，沿用线上证据、自评、最终流与联合裁判。"""
        loop = asyncio.get_running_loop()
        start = loop.time()
        deadline = start + max(0., self.settings.chat_timeout_seconds - rewrite_elapsed)
        faq_deadline = start + max(0., self.settings.faq_timeout_seconds - rewrite_elapsed)
        publish_final = True
        try:
            await self._publish(row)
            async with asyncio.timeout_at(deadline):
                self._active(cancel_event, deadline)
                async with asyncio.timeout_at(faq_deadline):
                    self._active(cancel_event, faq_deadline)
                    bundle = await self.retrieval.retrieve(case.query, category=case.category,
                        strategy=row['strategy'], query_plan=plan)
                    self._active(cancel_event, min(deadline, faq_deadline))
                request = AIMessage('', tool_calls=[{'name': 'query_faq',
                    'args': {'keyword': case.query[:128]}, 'id': 'eval-faq'}])
                packet = build_evidence(system=SystemMessage(build_grounded_answer_system_prompt()), turns=[],
                    current=HumanMessage(case.query), request=request, payload=faq_payload(bundle),
                    budget=self.settings.tool_input_token_budget)
                row.update(candidate_ids=[hit.id for hit in bundle.candidates],
                    final_ids=[item.chunk.id for item in bundle.matches],
                    prompt_citations=[asdict(citation) for citation in packet.citations], stage='self_check')
                candidate_kind = {'dense': 'cosine', 'bm25': 'bm25', 'hybrid': 'rrf', 'hybrid_rerank': 'rrf'}[row['strategy']]
                row['audit'].update(candidate_ranking=[dict(chunk_id=hit.id, score=hit.score,
                    score_kind=candidate_kind) for hit in bundle.candidates],
                    final_ranking=[dict(chunk_id=item.chunk.id, score=item.score, score_kind=item.score_kind)
                        for item in bundle.matches])
                await self._publish(row)
                self_check_deadline = min(deadline, loop.time() + self.settings.sufficiency_timeout_seconds)
                self._active(cancel_event, self_check_deadline)
                with self.resources.requests.stage('self_check'):
                    decision = await sufficiency.check(case.query, packet)
                self._active(cancel_event, self_check_deadline)
                row.update(decision=decision.model_dump(), stage='answer')
                await self._publish(row)
                self._active(cancel_event, deadline)
                if decision.useful:
                    stream = FinalAnswerStream()
                    with self.resources.requests.stage('answer'):
                        upstream = self.resources.model.astream(packet.messages)
                        try:
                            async for chunk in upstream:
                                self._active(cancel_event, deadline)
                                stream.accept(chunk)
                            text, reasons = stream.complete(deadline), stream.reasons
                        finally:
                            await close_answer_stream(upstream)
                else:
                    text, reasons = REFUSAL_TEXT, {'stop'}
                self._active(cancel_event, deadline)
                validate_answer(text, reasons, packet, decision)
                row.update(answer=text, refused=not decision.useful, stage='judgment')
                await self._publish(row)
                judge_deadline = min(deadline, loop.time() + self.settings.llm_timeout_seconds)
                self._active(cancel_event, judge_deadline)
                with self.resources.requests.stage('judge'):
                    judgment = await judge.judge(case.query, text, packet.citations, case.points)
                self._active(cancel_event, judge_deadline)
                unsupported = [asdict(claim) for claim in judgment.claims if not claim.supported]
                if unsupported:
                    reason = json.dumps({'prompt_version': judgment.prompt_version, 'claims': unsupported},
                                        ensure_ascii=False, allow_nan=False)
                    await self.resources.quality.record_fabrication(FaithCaseInput(case.ledger_eval_id,
                        case.bucket, case.query, row['strategy'], text, reason, row['prompt_citations'],
                        self.settings.llm_model))
                    self._active(cancel_event, deadline)
                row.update(status='completed', stage='complete',
                    point_verdicts=[asdict(point) for point in judgment.points],
                    claim_verdicts=[asdict(claim) for claim in judgment.claims],
                    judge_snapshot={'prompt_version': judgment.prompt_version,
                        'finish_reason': judgment.finish_reason, 'raw_response': judgment.raw_response})
        except StoreError:
            publish_final = False
            raise
        except asyncio.CancelledError:
            row['status'] = 'cancelled'
            raise
        except Exception as exc:
            storage_error = _storage_failure(exc)
            if storage_error is not None:
                publish_final = False
                raise storage_error from exc
            try:
                self._active(cancel_event)
            except asyncio.CancelledError:
                row['status'] = 'cancelled'
                raise
            row.update(status={'retrieval': 'retrieval_error', 'self_check': 'self_check_error',
                'answer': 'answer_error', 'judgment': 'judge_error'}[row['stage']],
                error=_failure(exc, row['stage']))
            if isinstance(exc, JudgeError):
                row['judge_snapshot'] = {'prompt_version': exc.prompt_version,
                    'finish_reason': exc.finish_reason, 'raw_response': exc.raw_response}
        finally:
            row['elapsed_ms'] = (loop.time() - start + rewrite_elapsed) * 1000
            if publish_final:
                await self._publish(row)
