"""Labeled material checks by default; exactly one explicit bounded model run."""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime,timezone
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:sys.path.insert(0,str(ROOT))
from app.flywheel.types import NormalizedDraft, ReviewCandidate, SemanticMatch


def load_cases(path):
    cases = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    seen = set()
    for case in cases:
        if not isinstance(case['id'], str) or case['id'] in seen or not case['raw_question'].strip():
            raise ValueError('Invalid or duplicate labeled case')
        seen.add(case['id'])
        draft = NormalizedDraft(normalized_question=case['example_normalized_question'],
                                ai_suggested_answer=case['example_answer'])
        candidates = [ReviewCandidate.model_validate(row) for row in case['candidates']]
        match = SemanticMatch(matched_review_id=case['labels']['matched_review_id'])
        if match.matched_review_id is not None and match.matched_review_id not in {c.id for c in candidates}:
            raise ValueError('Labeled target must belong to its candidate batch')
        for key in ('must_keep', 'must_not'):
            if not isinstance(case['labels'][key], list) or any(not isinstance(v, str) or not v for v in case['labels'][key]):
                raise ValueError('Labels must name semantic facts or prohibited claims')
        if not case['labels']['answer_boundary'].strip() or not isinstance(case['evidence'], list):
            raise ValueError('Missing human answer boundary')
    return cases


async def evaluate_cases(cases,client,output,*,model_name,observability=None):
    from app.observability.tracing import begin_execution,ExecutionIdentity
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    report_path=output/'report.json'
    if report_path.exists():raise ValueError('Prompt evaluation already exists; inspect instead of replaying')
    report={'schema_version':1,'status':'running','model':model_name,'case_ids':[row['id'] for row in cases],
        'records':[],'attempts':[],'created_at':datetime.now(timezone.utc).isoformat(),
        'semantic_review':None,'error':None}
    def save():
        temp=output/'report.json.tmp'
        temp.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(report_path)
    with report_path.open('x',encoding='utf-8') as stream:
        json.dump(report,stream,ensure_ascii=False,indent=2)
    try:
        for case in cases:
            with begin_execution(observability,ExecutionIdentity('prompt-evaluation',case['id'],uuid4().hex,'evaluation')) as trace:
                report['attempts'].append({'case_id':case['id'],'stage':'normalize','status':'started'});save()
                row={'raw_question':case['raw_question'],'snapshot_status':'captured' if case['evidence'] else 'not_retrieved',
                    'retrieved_chunks':{'chunks':case['evidence']}}
                draft=await client.normalize(row)
                report['attempts'][-1].update(status='returned',draft=draft.model_dump());save()
                report['attempts'].append({'case_id':case['id'],'stage':'dedup','status':'started'});save()
                matched=await client.deduplicate(draft,[ReviewCandidate.model_validate(value) for value in case['candidates']])
                report['attempts'][-1].update(status='returned',match=matched.model_dump());save()
                text=draft.normalized_question+'\n'+draft.ai_suggested_answer
                checks={'must_keep_literal':{value:value in draft.normalized_question for value in case['labels']['must_keep']},
                    'must_not_literal':{value:value not in text for value in case['labels']['must_not']},
                    'dedup_exact':matched.matched_review_id==case['labels']['matched_review_id']}
                report['records'].append({'case_id':case['id'],'raw_question':case['raw_question'],
                    'evidence':case['evidence'],'draft':draft.model_dump(),'match':matched.model_dump(),
                    'checks':checks,'answer_boundary':case['labels']['answer_boundary'],
                    'semantic_pass':None})
                trace.finish('success');save()
        report['status']='completed'
    except Exception as exc:
        report.update(status='failed',error={'type':type(exc).__name__,'message':'本轮停止，不修复重试或自动重放。'})
    finally:
        report['finished_at']=datetime.now(timezone.utc).isoformat();save()
    return report


async def actual(cases,output):
    import httpx
    from contextlib import AsyncExitStack
    from app.observability.demo import load_ch09_settings
    from app.observability.runtime import LangfuseRuntime
    from app.core.llm import create_model
    from app.flywheel.processing import PromptClient
    from app.flywheel.acceptance import acceptance_cap,RUN_ID
    from app.context.acceptance import AcceptanceCallCap
    from app.eval_pipeline.resources import UsageCollector
    if (output/'report.json').exists():raise ValueError('Prompt evaluation already exists')
    settings=load_ch09_settings(ROOT)
    global_cap=acceptance_cap(RUN_ID,root=ROOT)
    local_cap=AcceptanceCallCap('ch09-prompt12-v1',{'glm':24,'embedding':0,'rerank':0},output/'call-ledger.sqlite')
    def sync_hook(request):local_cap.reserve('glm');global_cap.reserve('glm')
    async def async_hook(request):sync_hook(request)
    async with AsyncExitStack() as stack:
        sync=stack.enter_context(httpx.Client(event_hooks={'request':[sync_hook]}))
        asynchronous=await stack.enter_async_context(httpx.AsyncClient(event_hooks={'request':[async_hook]}))
        runtime=LangfuseRuntime.from_settings(settings);stack.push_async_callback(runtime.close)
        kwargs={'reasoning_effort':settings.online_reasoning_effort} if settings.online_reasoning_effort else {}
        model=create_model(settings,http_client=sync,http_async_client=asynchronous,**kwargs)
        stack.callback(model.root_client.close);stack.push_async_callback(model.root_async_client.close)
        usage=UsageCollector();model=model.model_copy(update={'callbacks':[usage]},deep=False)
        result=await evaluate_cases(cases,PromptClient(model,callbacks=[runtime.handler] if runtime.handler else None),
            output,model_name=settings.llm_model,observability=runtime)
        result['actual_usage_tokens']=sum(usage.values) if usage.values else None
        result['calls_with_usage']=len(usage.values)
        result['local_attempts']=local_cap.status();result['shared_allowance']=global_cap.status()
        (output/'report.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
        return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='只核验材料结构，不调用模型')
    parser.add_argument('--execute',action='store_true',help='显式执行12组、最多24次模型请求')
    parser.add_argument('--acceptance-run',choices=('ch09-local-20261019',))
    parser.add_argument('--cases',default=str(ROOT/'evals/flywheel_cases.jsonl'))
    parser.add_argument('--output',type=Path,default=ROOT/'runtime/ch09-evidence/prompt-evaluation')
    args = parser.parse_args(argv)
    cases = load_cases(args.cases)
    if not args.execute:
        print(f'{len(cases)}组标注材料结构有效；未执行模型语义验证。');return
    if args.offline or args.acceptance_run is None or len(cases)!=12 or Path(args.cases).resolve()!=(ROOT/'evals/flywheel_cases.jsonl').resolve():
        parser.error('Actual evaluation requires the approved frozen12, --acceptance-run and no --offline')
    try:
        result=asyncio.run(actual(cases,args.output))
        print(json.dumps({'status':result['status'],'completed':len(result['records']),
            'attempts':result['local_attempts'],'report':str(args.output/'report.json')},ensure_ascii=False))
        if result['status']!='completed':parser.exit(1,'Prompt evaluation incomplete; inspect saved report, no automatic replay\n')
    except Exception as exc:parser.exit(1,f'Prompt evaluation stopped ({type(exc).__name__}); no automatic replay\n')


if __name__ == '__main__':
    main()
