"""Actual BGE dense retrieval plus one real application/SSE/persistence acceptance.

Only committed synthetic demo documents and a new demo conversation are used.
The configured online model and budget stay unchanged. Never read private history.
"""

import argparse
import asyncio
from contextlib import AsyncExitStack
import json
from pathlib import Path
from time import monotonic
from uuid import uuid4

import httpx
from sqlalchemy import delete, select

from app.db.models import Conversation, KnowledgeChunk, Message, Ticket
from app.db.session import Database
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.knowledge.ingestion import import_document
from app.knowledge.vectorization import PendingVectorizer
from app.knowledge.vectors import MilvusIndex
from app.main import create_app
from app.repositories.conversations import ConversationRepository
from app.repositories.faq import FAQRepository
from app.repositories.knowledge import KnowledgeRepository
from app.repositories.records import decode_tool_calls
from evals.evaluate_tools import audit_messages
from evals.knowledge_recovery import OwnedRepository, attempt_cleanup, test_settings, timestamp, write_checkpoint
from evals.smoke import chat_round, create_conversation


async def evaluate_retrieval(faq, cases, sections_by_id):
    records = [{**case, 'expected_hit_ids': sorted(i for i, section in sections_by_id.items()
        if section in case['expected_sections']), 'actual_hit_ids': [], 'tool_result': None,
        'final_answer': None, 'answer_review': 'not_applicable_retrieval_only',
        'latency_seconds': None, 'passed': False, 'error_code': 'not_attempted'} for case in cases]
    report = {'attempted': 0, 'not_attempted': len(cases), 'passed': 0, 'cases': records}
    if any(c['expected_sections'] and not c['expected_hit_ids'] for c in records):
        report['error_code'] = 'missing_gold_section'
        return report
    for record in records:
        report['attempted'] += 1
        report['not_attempted'] -= 1
        started = monotonic()
        try:
            # Send the literal annotated query; no rewrite, keyword branch or fallback.
            matches = await faq.search(record['query'])
            actual = [match['id'] for match in matches]
            record.update(actual_hit_ids=actual, actual_sections=[sections_by_id.get(i) for i in actual],
                tool_result={'found': bool(matches), 'matches': matches}, error_code=None)
            expected = record['expected_hit_ids']
            record['passed'] = bool(set(expected) & set(actual)) if expected else not actual
            report['passed'] += int(record['passed'])
        except Exception as exc:
            record.update(error_code='retrieval_failed', error_type=type(exc).__name__)
            break
        finally:
            record['latency_seconds'] = monotonic() - started
    return report


async def evaluate_app(settings, database, faq, expected_ids, user_id):
    repository = ConversationRepository(database)
    app = create_app(settings, database=database, repository=repository, faq_repository=faq)
    result = {'attempted': 0, 'not_attempted': 1, 'passed': False, 'query': '邮费是多少',
        'expected_hit_ids': expected_ids, 'actual_hit_ids': [], 'tool_result': None,
        'final_answer': None, 'answer_review': 'pending_manual_fact_review',
        'transport': 'HTTPX ASGITransport (buffered SSE); actual app lifespan/model/MySQL/Milvus',
        'latency_seconds': None, 'http_request_count': 0, 'model_request_count': None}
    started = monotonic()
    lifespan_entered = False
    try:
        async with app.router.lifespan_context(app):
            lifespan_entered = True
            client_entered = False
            try:
                async with httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://acceptance') as client:
                    client_entered = True
                    try:
                        result.update(attempted=1, not_attempted=0, http_request_count=1)
                        created = await create_conversation(client, 'http://acceptance', user_id)
                        result.update(conversation_id=created['conversation_id'], error_code=created['error_code'])
                        if created['error_code']:
                            return result
                        result['http_request_count'] += 1
                        stream = await chat_round(client, 'http://acceptance', created['conversation_id'], result['query'], min_deltas=1)
                        result.update(stream=stream, final_answer=stream['text'], error_code=stream['error_code'])
                        rows = await repository.load_messages(created['conversation_id'])
                        calls = [decode_tool_calls(row.tool_calls)[0] for row in rows if row.tool_calls is not None]
                        keyword = calls[0]['args'].get('keyword') if len(calls) == 1 else None
                        original_argument = isinstance(keyword, str) and bool(keyword) and keyword in result['query']
                        audit = audit_messages(rows, {'message': result['query'], 'expected_tool': 'query_faq',
                            'expected_args': {'keyword': keyword}, 'expected_found': True}, stream)
                        result.update(audit)
                        matches = audit['matches'] or []
                        result.update(actual_hit_ids=[m['id'] for m in matches], original_argument=original_argument,
                            persisted_final_answer=bool(rows and rows[-1].role == 'assistant'
                                and rows[-1].tool_calls is None and rows[-1].content == stream['text']))
                        result['passed'] = bool(audit['passed'] and original_argument
                            and set(expected_ids) & set(result['actual_hit_ids']) and result['persisted_final_answer'])
                    except Exception as exc:
                        result.update(error_code='app_acceptance_failed', error_type=type(exc).__name__, passed=False)
            except Exception as exc:
                if client_entered:
                    result.setdefault('cleanup_errors', []).append({'action': 'http_client_exit',
                                                                   'error_type': type(exc).__name__})
                    result['passed'] = False
                else:
                    result.update(error_code='app_acceptance_failed', error_type=type(exc).__name__, passed=False)
    except Exception as exc:
        if lifespan_entered:
            result.setdefault('cleanup_errors', []).append({'action': 'app_context_exit',
                                                           'error_type': type(exc).__name__})
            result['passed'] = False
        else:
            result.update(error_code='app_acceptance_failed', error_type=type(exc).__name__, passed=False)
    finally:
        result['latency_seconds'] = monotonic() - started
    return result


async def evaluate(cases):
    database = None
    collection = 'knowledge_test_' + uuid4().hex
    user_id = 'dense-acceptance-' + uuid4().hex
    ids = []
    report = {'kind': 'actual_dense_knowledge_acceptance', 'started_at': timestamp(),
        'database': '127.0.0.1:3308/customer_service_test', 'collection': collection,
        'cleanup': 'pending', 'cleanup_errors': [],
        'retrieval': {'attempted': 0, 'not_attempted': len(cases), 'passed': 0,
            'cases': [{**case, 'error_code': 'not_attempted'} for case in cases]},
        'app': {'attempted': 0, 'not_attempted': 1, 'passed': False}, 'acceptance_passed': False}
    try:
        settings = test_settings()
        database = Database(settings.database_url)
        report.update(embedding_model=settings.embedding_model, online_model=settings.llm_model,
                      online_output_budget=settings.max_output_tokens)
        async with AsyncExitStack() as resources:
            embedder = SiliconFlowEmbedder(settings)
            resources.push_async_callback(attempt_cleanup, report['cleanup_errors'], 'embedder_close', embedder.aclose)
            index = MilvusIndex(str(settings.milvus_uri), collection=collection, timeout=settings.milvus_timeout_seconds)
            resources.push_async_callback(attempt_cleanup, report['cleanup_errors'], 'index_close', index.aclose)
            try:
                # Actual cloud shape and full schema/index validation precede imports.
                probe = await embedder.embed(['邮费是多少'])
                report['actual_embedding_dimensions'] = len(probe[0])
                await index.ensure_collection()
                report['schema_verified'] = True
                description = await index._client.describe_collection(collection, timeout=index.timeout)
                report['collection_schema'] = {'auto_id': description['auto_id'],
                    'consistency_level': description['consistency_level'],
                    'fields': [{'name': f['name'], 'type': int(f['type']), 'params': f.get('params', {})}
                               for f in description['fields']]}
                repository = KnowledgeRepository(database)
                for name, kind in [('demo-policy.md', 'policy'), ('demo-faq.md', 'faq'), ('demo-manual.md', 'manual')]:
                    ids.extend(await import_document(Path('knowledge-docs') / name, kind, repository))
                report['imported_ids'] = ids
                report['vectorized_count'] = await PendingVectorizer(OwnedRepository(database, ids), embedder, index).run()
                records = await repository.get_done(ids)
                sections = {record.id: record.section_path for record in records}
                report['sections_by_id'] = sections
                faq = FAQRepository(database, embedder, index)
                retrieval = await evaluate_retrieval(faq, cases, sections)
                report['retrieval'] = retrieval
                if retrieval.get('error_code') or any(c['error_code'] not in (None, 'not_attempted') for c in retrieval['cases']):
                    return report
                shipping_ids = [r.id for r in records if r.section_path in cases[0]['expected_sections']]
                report['app'] = await evaluate_app(settings, database, faq, shipping_ids, user_id)
                required = [c for c in retrieval['cases'] if c.get('required', True)]
                report['acceptance_passed'] = all(c['passed'] for c in required) and report['app']['passed']
                report['answer_review'] = 'pending_manual_fact_review'
            except Exception as exc:
                report.update(error_code='acceptance_failed', error_type=type(exc).__name__)
            finally:
                # Only ids returned from this import and this unguessable demo user are owned.
                async def clean_rows():
                    async with database.session() as session, session.begin():
                        conversation_ids = list((await session.scalars(select(Conversation.id)
                            .where(Conversation.user_id == user_id))).all())
                        for model in (Message, Ticket):
                            await session.execute(delete(model).where(model.conversation_id.in_(conversation_ids)))
                        await session.execute(delete(Conversation).where(Conversation.id.in_(conversation_ids)))
                        await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.id.in_(ids)))
                await attempt_cleanup(report['cleanup_errors'], 'mysql_rows_and_conversation', clean_rows)
                async def clean_collection():
                    if await index._client.has_collection(collection, timeout=index.timeout):
                        await index._client.drop_collection(collection, timeout=index.timeout)
                await attempt_cleanup(report['cleanup_errors'], 'milvus_collection', clean_collection)
    except Exception as exc:
        report.update(error_code='acceptance_failed', error_type=type(exc).__name__, acceptance_passed=False)
    finally:
        if database is not None:
            await attempt_cleanup(report['cleanup_errors'], 'database_dispose', database.dispose)
        report['cleanup'] = 'failed' if report['cleanup_errors'] else 'owned_demo_rows_conversation_and_collection_removed'
        if report['cleanup_errors']:
            report['acceptance_passed'] = False
        report['finished_at'] = timestamp()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, default=Path('evals/knowledge_cases.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('.cache/knowledge-evaluation.json'))
    args = parser.parse_args(argv)
    try:
        cases = [json.loads(line) for line in args.cases.read_text(encoding='utf-8').splitlines() if line.strip()]
        report = asyncio.run(evaluate(cases))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_checkpoint(args.output, report)
        print(json.dumps({'acceptance_passed': report['acceptance_passed'],
                          'retrieval': {k: report.get('retrieval', {}).get(k) for k in ('attempted', 'not_attempted', 'passed')},
                          'app_passed': report['app']['passed']}))
        return 0 if report['acceptance_passed'] else 1
    except Exception as exc:
        print(f'Knowledge evaluation failed ({type(exc).__name__})')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
