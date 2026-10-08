"""Real owned-child interruption against test MySQL and a UUID Milvus collection.

No fault controls are added to the application. Only these harness-created
Popen handles are terminated; rows and collections have an explicit owner.
"""

import argparse
import asyncio
from contextlib import AsyncExitStack
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import sysconfig
from tempfile import TemporaryDirectory
from time import monotonic
from uuid import uuid4

from sqlalchemy import delete, select

from app.config import load_settings
from app.db.models import KnowledgeChunk
from app.db.session import Database
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.knowledge.types import ChunkDraft
from app.knowledge.vectorization import PendingVectorizer
from app.knowledge.vectors import MilvusIndex
from app.repositories.knowledge import KnowledgeRepository, _record


def timestamp():
    return datetime.now(timezone.utc).isoformat()


async def attempt_cleanup(errors, action, callback):
    """One failed owned cleanup must not prevent the remaining attempts/report."""
    try:
        await callback()
    except Exception as exc:
        errors.append({'action': action, 'error_type': type(exc).__name__})


def test_settings():
    return load_settings().model_copy(update={'mysql_host': '127.0.0.1', 'mysql_port': 3308,
        'mysql_database': 'customer_service_test', 'mysql_user': 'customer_service'})


class OwnedRepository(KnowledgeRepository):
    """Harness-only pending scope; never consume another job's pending rows."""

    def __init__(self, database, ids):
        super().__init__(database)
        self.ids = ids

    async def pending(self, limit=20):
        async with self.database.session() as session:
            rows = (await session.scalars(select(KnowledgeChunk).where(
                KnowledgeChunk.id.in_(self.ids), KnowledgeChunk.vectorize_status == 'pending')
                .order_by(KnowledgeChunk.id).limit(limit))).all()
            return [_record(row) for row in rows]


def write_checkpoint(path, data):
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    temporary.replace(path)


async def pause_at(path, data):
    write_checkpoint(path, {**data, 'checkpoint_at': timestamp()})
    await asyncio.Event().wait()


async def snapshot(database, index, ids):
    async with database.session() as session:
        rows = (await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.id.in_(ids))
            .order_by(KnowledgeChunk.id))).all()
        records = [{'id': r.id, 'status': r.vectorize_status, 'vector_id': r.vector_id,
            'body_sha256': sha256(r.answer.encode('utf-8')).hexdigest()} for r in rows]
    vectors = await index._client.query(index.collection, filter='id >= 0', output_fields=['id'],
        consistency_level='Strong', timeout=index.timeout)
    vector_ids = sorted(r['id'] for r in vectors)
    return {'rows': records, 'vector_ids': vector_ids, 'vector_row_count': len(vector_ids),
            'unique_vector_count': len(set(vector_ids))}


def recovery_passed(before, after, ids):
    original = {r['id']: r['body_sha256'] for r in before['rows']}
    return (set(original) == set(ids) and len(after['rows']) == len(ids)
        and {r['id'] for r in after['rows']} == set(ids)
        and all(r['status'] == 'done' and r['vector_id'] == str(r['id'])
                and r['body_sha256'] == original[r['id']] for r in after['rows'])
        and sorted(after['vector_ids']) == sorted(ids)
        and after['vector_row_count'] == after['unique_vector_count'] == len(ids))


async def child(args):
    settings = test_settings()
    database = Database(settings.database_url)
    try:
        async with AsyncExitStack() as resources:
            index = MilvusIndex(str(settings.milvus_uri), collection=args.collection,
                                timeout=settings.milvus_timeout_seconds)
            resources.push_async_callback(index.aclose)
            embedder = SiliconFlowEmbedder(settings)
            resources.push_async_callback(embedder.aclose)
            repository = KnowledgeRepository(database)
            if args.mode == 'after_pending':
                # add_chunks returns only after its short MySQL transaction commits.
                ids = await repository.add_chunks([
                    ChunkDraft(args.marker, '配送费用', '合成演示标准配送8元，满99元包邮。'),
                    ChunkDraft(args.marker, '售后申请', '合成演示售后申请需等待客服确认。')])
                await pause_at(args.checkpoint, {'phase': args.mode, 'owned_pid': __import__('os').getpid(),
                    'ids': ids, 'pending_committed': True})
            else:
                ids = json.loads(args.ids)
                repository = OwnedRepository(database, ids)
                if args.mode == 'after_upsert':
                    class PausingIndex:
                        async def upsert(self, rows):
                            acknowledged = await index.upsert(rows)
                            await pause_at(args.checkpoint, {'phase': args.mode,
                                'owned_pid': __import__('os').getpid(), 'ids': ids,
                                'acknowledged_ids': acknowledged, 'upsert_returned': True})
                            return acknowledged

                    await PendingVectorizer(repository, embedder, PausingIndex()).run()
                else:
                    count = await PendingVectorizer(repository, embedder, index).run()
                    replay_count = await PendingVectorizer(repository, embedder, index).run()
                    write_checkpoint(args.checkpoint, {'phase': 'restarted', 'owned_pid': __import__('os').getpid(),
                        'ids': ids, 'recovered': count, 'replay_count': replay_count, 'completed_at': timestamp()})
    finally:
        await database.dispose()


def spawn_owned(mode, checkpoint, collection, marker, ids):
    # Never use a shell, attach to an existing PID, or kill a process group.
    # Windows venv python.exe redirects to a second PID. Run the actual interpreter
    # with this venv's installed packages so Popen.pid is the executing worker.
    environment = os.environ.copy()
    environment['PYTHONPATH'] = os.pathsep.join(filter(None, [sysconfig.get_path('purelib'),
                                                            environment.get('PYTHONPATH')]))
    return subprocess.Popen([getattr(sys, '_base_executable', sys.executable), '-m', 'evals.knowledge_recovery', '--child',
        '--mode', mode, '--checkpoint', str(checkpoint), '--collection', collection,
        '--marker', marker, '--ids', json.dumps(ids)], stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL, env=environment,
        creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))


async def wait_checkpoint(process, path, timeout=90):
    deadline = monotonic() + timeout
    while monotonic() < deadline:
        if path.exists():
            result = json.loads(path.read_text(encoding='utf-8'))
            if result.get('owned_pid') != process.pid:
                raise ValueError('checkpoint does not belong to owned child')
            return result
        if process.poll() is not None:
            raise RuntimeError('owned child exited before checkpoint')
        await asyncio.sleep(.1)
    raise TimeoutError('owned child checkpoint timeout')


async def terminate_owned(process):
    if process.poll() is None:
        process.kill()
    return await asyncio.to_thread(process.wait, timeout=10)


async def evaluate_recovery():
    database = None
    report = {'kind': 'actual_owned_process_recovery', 'started_at': timestamp(),
        'database': '127.0.0.1:3308/customer_service_test', 'attempted': 0, 'not_attempted': 2,
        'cases': [], 'passed': False, 'cleanup': 'pending', 'cleanup_errors': []}
    try:
        settings = test_settings()
        database = Database(settings.database_url)
        for phase in ('after_pending', 'after_upsert'):
            marker = 'recovery_' + uuid4().hex
            collection = 'knowledge_test_' + uuid4().hex
            index = None
            processes, ids = [], []
            case = {'phase': phase, 'collection': collection, 'passed': False,
                    'owned_children': [], 'cleanup_errors': []}
            report['cases'].append(case)
            report['attempted'] += 1
            report['not_attempted'] -= 1
            try:
                index = MilvusIndex(str(settings.milvus_uri), collection=collection,
                                    timeout=settings.milvus_timeout_seconds)
                await index.ensure_collection()
                with TemporaryDirectory(prefix='knowledge-recovery-') as directory:
                    checkpoint = Path(directory) / 'interrupted.json'
                    if phase == 'after_upsert':
                        ids = await KnowledgeRepository(database).add_chunks([
                            ChunkDraft(marker, '配送费用', '合成演示标准配送8元，满99元包邮。'),
                            ChunkDraft(marker, '售后申请', '合成演示售后申请需等待客服确认。')])
                    process = spawn_owned(phase, checkpoint, collection, marker, ids)
                    processes.append(process)
                    interrupted = await wait_checkpoint(process, checkpoint)
                    ids = interrupted['ids']
                    case.update(checkpoint=interrupted, expected_ids=ids,
                        before=await snapshot(database, index, ids))
                    killed = await terminate_owned(process)
                    case['owned_children'].append({'pid': process.pid, 'created_by_harness': True,
                        'action': 'kill', 'returncode': killed, 'terminated_at': timestamp()})
                    # A new OS process runs the unmodified PendingVectorizer normally.
                    restarted_path = Path(directory) / 'restarted.json'
                    restarted = spawn_owned('normal', restarted_path, collection, marker, ids)
                    processes.append(restarted)
                    restart_result = await wait_checkpoint(restarted, restarted_path)
                    returncode = await asyncio.to_thread(restarted.wait, timeout=10)
                    case['owned_children'].append({'pid': restarted.pid, 'created_by_harness': True,
                        'action': 'normal_restart', 'returncode': returncode})
                    case.update(restart=restart_result, after=await snapshot(database, index, ids))
                    expected_before_vectors = [] if phase == 'after_pending' else sorted(ids)
                    case['passed'] = (all(r['status'] == 'pending' and r['vector_id'] is None
                        for r in case['before']['rows'])
                        and case['before']['vector_ids'] == expected_before_vectors
                        and returncode == 0 and restart_result['recovered'] == len(ids)
                        and restart_result['replay_count'] == 0
                        and recovery_passed(case['before'], case['after'], ids))
            except Exception as exc:
                case.update(error_type=type(exc).__name__)
            finally:
                for process in processes:
                    await attempt_cleanup(case['cleanup_errors'], f'owned_process:{process.pid}',
                        lambda process=process: terminate_owned(process))
                # Recovery rows carry an unguessable marker even if checkpoint writing failed.
                async def clean_rows():
                    async with database.session() as session, session.begin():
                        await session.execute(delete(KnowledgeChunk).where(KnowledgeChunk.category == marker))
                await attempt_cleanup(case['cleanup_errors'], 'mysql_rows', clean_rows)
                if index is not None:
                    async def clean_collection():
                        if await index._client.has_collection(collection, timeout=index.timeout):
                            await index._client.drop_collection(collection, timeout=index.timeout)
                    await attempt_cleanup(case['cleanup_errors'], 'milvus_collection', clean_collection)
                    await attempt_cleanup(case['cleanup_errors'], 'index_close', index.aclose)
                case['cleanup'] = 'failed' if case['cleanup_errors'] else 'owned_rows_and_collection_removed'
                if case['cleanup_errors']:
                    case['passed'] = False
                report['cleanup_errors'].extend(case['cleanup_errors'])
            if not case['passed']:
                break
        report['passed'] = len(report['cases']) == 2 and all(c['passed'] for c in report['cases'])
    except Exception as exc:
        report.update(error_type=type(exc).__name__, passed=False)
    finally:
        if database is not None:
            await attempt_cleanup(report['cleanup_errors'], 'database_dispose', database.dispose)
        report['cleanup'] = 'failed' if report['cleanup_errors'] else 'owned_rows_and_collections_removed'
        if report['cleanup_errors']:
            report['passed'] = False
        report['finished_at'] = timestamp()
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('.cache/knowledge-recovery.json'))
    parser.add_argument('--child', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--mode', choices=['after_pending', 'after_upsert', 'normal'], help=argparse.SUPPRESS)
    parser.add_argument('--checkpoint', type=Path, help=argparse.SUPPRESS)
    parser.add_argument('--collection', help=argparse.SUPPRESS)
    parser.add_argument('--marker', help=argparse.SUPPRESS)
    parser.add_argument('--ids', default='[]', help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    try:
        if args.child:
            if not args.collection or not args.collection.startswith('knowledge_test_') or not args.marker.startswith('recovery_'):
                raise ValueError('child ownership scope required')
            asyncio.run(child(args))
            return 0
        report = asyncio.run(evaluate_recovery())
        args.output.parent.mkdir(parents=True, exist_ok=True)
        write_checkpoint(args.output, report)
        print(json.dumps({'attempted': report['attempted'], 'not_attempted': report['not_attempted'],
                          'passed': report['passed']}))
        return 0 if report['passed'] else 1
    except Exception as exc:
        print(f'Recovery harness failed ({type(exc).__name__})')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
