"""Short MySQL transactions for original questions and deduplicated gaps."""
import json
import hashlib
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.flywheel.types import (
    NormalizedDraft, PoolInput, PoolReceipt, ProcessingState, ReviewAssignment,
    ReviewChanged, database_id,
    ReviewCandidate, TaskError,
)


def row_dict(row):
    result = dict(row)
    for key, value in list(result.items()):
        if value is not None and (key == 'id' or key.endswith('_id')):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif key in ('retrieved_chunks', 'processing', 'publication', 'metrics') and isinstance(value, str):
            result[key] = json.loads(value)
    return result


def _page(offset, limit):
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('Invalid pagination bounds')


def _state(value):
    if value is None:
        raise ValueError('Historical row requires explicit processing initialization')
    return ProcessingState.model_validate_json(value if isinstance(value, str) else json.dumps(value))


class FlywheelRepository:
    def __init__(self, database):
        self.database = database

    def processing_lease(self):
        from app.flywheel.leases import processing_lease
        return processing_lease(self.database)

    async def next_pending_id(self, now):
        after = 0
        while True:
            async with self.database.session() as session:
                rows = (await session.execute(text('SELECT id,processing FROM low_confidence_questions '
                    'WHERE matched_review_id IS NULL AND processing IS NOT NULL AND id>:after '
                    "AND JSON_UNQUOTE(JSON_EXTRACT(processing,'$.status')) IN ('pending','retry_wait') "
                    'ORDER BY id LIMIT 100'), {'after': after})).mappings().all()
            for row in rows:
                current = _state(row['processing'])
                if current.status == 'pending' or current.next_attempt_at is not None and current.next_attempt_at <= now:
                    return str(row['id'])
            if len(rows) < 100:
                return None
            after = rows[-1]['id']

    async def claim_processing(self, lease, pool_id, now):
        from app.flywheel.prompts import NORMALIZE_VERSION, DEDUP_VERSION
        from app.flywheel.types import ProcessingState
        async with lease.transaction() as session:
            row = (await session.execute(text('SELECT * FROM low_confidence_questions WHERE id=:id FOR UPDATE'),
                {'id': int(database_id(pool_id))})).mappings().one_or_none()
            if row is None or row['processing'] is None or row['matched_review_id'] is not None:
                return None
            current = _state(row['processing'])
            if current.status not in ('pending', 'retry_wait'):
                return None
            if current.next_attempt_at is not None and current.next_attempt_at > now:
                return None
            if current.attempt_count >= 3:
                current.status, current.next_attempt_at = 'failed', None
                current.last_error = TaskError(code='attempt_limit', stage='processing', message='已达到三次处理上限。')
                await self._write_processing(session, pool_id, current)
                return None
            versions = {'normalize': NORMALIZE_VERSION, 'dedup': DEDUP_VERSION}
            if current.prompt_versions != versions:
                current.normalized_draft = current.dedup_cursor = current.candidate_fingerprint = None
            current.prompt_versions = versions
            current.attempt_count += 1
            current.status, current.next_attempt_at, current.last_error = 'running', None, None
            await self._write_processing(session, pool_id, current)
            result = row_dict(row)
            result['processing'] = current.model_dump(mode='json')
            return result, current

    @staticmethod
    async def _write_processing(session, pool_id, current):
        await session.execute(text('UPDATE low_confidence_questions SET processing=:state WHERE id=:id'),
            {'id': int(database_id(pool_id)), 'state': current.model_dump_json()})

    async def save_processing(self, lease, pool_id, current):
        from app.flywheel.leases import LeaseLost
        async with lease.transaction() as session:
            row = (await session.execute(text('SELECT processing,matched_review_id FROM low_confidence_questions '
                'WHERE id=:id FOR UPDATE'), {'id': int(database_id(pool_id))})).one()
            stored = _state(row.processing)
            if (row.matched_review_id is not None or stored.status != 'running'
                    or stored.attempt_count != current.attempt_count):
                raise LeaseLost('Processing task changed before state commit')
            await self._write_processing(session, pool_id, current)

    @staticmethod
    async def _candidate_snapshot(session):
        rows = (await session.execute(text("SELECT id,normalized_question FROM review_queue WHERE review_status='待审' ORDER BY id"))).all()
        candidates = [ReviewCandidate(id=str(row.id), normalized_question=row.normalized_question) for row in rows]
        fingerprint = hashlib.sha256(json.dumps([row.model_dump() for row in candidates],
            ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
        return candidates, fingerprint

    async def candidate_snapshot(self, lease):
        async with lease.transaction() as session:
            return await self._candidate_snapshot(session)

    async def finish_processing(self, lease, pool_id, *, current, matched_review_id, fingerprint):
        async with lease.transaction() as session:
            _, latest = await self._candidate_snapshot(session)
            if fingerprint != latest:
                raise ReviewChanged('Pending candidate queue changed during model call')
            return await self.assign_in_session(session, pool_id, matched_review_id=matched_review_id,
                                                 draft=current.normalized_draft)

    async def recover_processing(self, lease, now):
        from datetime import timedelta
        async with lease.transaction() as session:
            rows = (await session.execute(text('SELECT id,processing FROM low_confidence_questions '
                'WHERE matched_review_id IS NULL AND processing IS NOT NULL '
                "AND JSON_UNQUOTE(JSON_EXTRACT(processing,'$.status'))='running' FOR UPDATE"))).all()
            for row in rows:
                current = _state(row.processing)
                current.last_error = TaskError(code='interrupted', stage='processing', message='后台任务曾中断，等待受管恢复。')
                current.status = 'failed' if current.attempt_count >= 3 else 'retry_wait'
                current.next_attempt_at = None if current.status == 'failed' else now + timedelta(seconds=5 if current.attempt_count == 1 else 30)
                await self._write_processing(session, str(row.id), current)
            return len(rows)

    async def manage_processing(self, pool_id, *, action, now):
        from datetime import timedelta
        if action not in ('initialize', 'retry', 'recover'):
            raise ValueError('Unknown selected-ID management action')
        async with self.processing_lease() as lease:
            if lease is None:
                raise ValueError('Processing worker is active; try selected-ID management later')
            async with lease.transaction() as session:
                row = (await session.execute(text('SELECT * FROM low_confidence_questions WHERE id=:id FOR UPDATE'),
                    {'id': int(database_id(pool_id))})).mappings().one_or_none()
                if row is None or row['matched_review_id'] is not None:
                    raise ValueError('Selected question is missing or already matched')
                if action == 'initialize':
                    if row['processing'] is not None:
                        raise ValueError('Selected question already has processing metadata')
                    current = ProcessingState()
                    if row['retrieved_chunks'] is None:
                        from app.flywheel.snapshots import _unavailable
                        snapshot = _unavailable()
                        await session.execute(text('UPDATE low_confidence_questions SET snapshot_status=:status,'
                            'retrieved_chunks=:payload WHERE id=:id'), {'id': int(pool_id),
                            'status': snapshot.status, 'payload': snapshot.payload.model_dump_json()})
                else:
                    current = _state(row['processing'])
                    if current.attempt_count >= 3:
                        raise ValueError('Three-attempt limit cannot be reset')
                    if action == 'recover':
                        if current.status != 'running':
                            raise ValueError('Selected question is not interrupted/running')
                        current.status = 'retry_wait'
                        current.next_attempt_at = now + timedelta(seconds=5 if current.attempt_count == 1 else 30)
                        current.last_error = TaskError(code='interrupted', stage='processing', message='按指定ID恢复中断任务。')
                    else:
                        if current.status not in ('failed', 'retry_wait'):
                            raise ValueError('Selected question is not retryable')
                        current.status, current.next_attempt_at, current.last_error = 'pending', None, None
                await self._write_processing(session, pool_id, current)
                return {'id': pool_id, 'processing': current.model_dump(mode='json')}

    async def enqueue(self, item):
        async with self.database.session() as session, session.begin():
            receipt = await self.enqueue_in_session(session, item)
        return receipt

    async def enqueue_in_session(self, session, item: PoolInput) -> PoolReceipt:
        if not isinstance(item, PoolInput):
            raise ValueError('PoolInput with trusted identities is required')
        parameters = {name: int(getattr(item, name)) if getattr(item, name) is not None else None
                      for name in ('conversation_id', 'user_message_id', 'assistant_message_id')}
        parameters.update(raw_question=item.raw_question, source=item.source, reason=item.reason,
            retrieved_chunks=item.snapshot.payload.model_dump_json() if item.snapshot.payload else None,
            snapshot_status=item.snapshot.status, processing=ProcessingState().model_dump_json())
        try:
            # MySQL duplicate errors roll back only this savepoint, not the caller's
            # final assistant message or any other work in its outer transaction.
            async with session.begin_nested():
                result = await session.execute(text(
                    'INSERT INTO low_confidence_questions(conversation_id,user_message_id,assistant_message_id,'
                    'raw_question,source,reason,retrieved_chunks,snapshot_status,processing) '
                    'VALUES(:conversation_id,:user_message_id,:assistant_message_id,:raw_question,:source,'
                    ':reason,:retrieved_chunks,:snapshot_status,:processing)'), parameters)
                identifier = database_id(str(result.lastrowid))
            return PoolReceipt(id=identifier, created=True)
        except IntegrityError:
            if item.assistant_message_id is None:
                raise
            row = (await session.execute(text('SELECT * FROM low_confidence_questions '
                'WHERE assistant_message_id=:assistant AND source=:source'),
                {'assistant': int(item.assistant_message_id), 'source': item.source})).mappings().one_or_none()
            if row is None:
                raise
            for key in ('conversation_id', 'user_message_id'):
                stored = str(row[key]) if row[key] is not None else None
                if stored != getattr(item, key):
                    raise ValueError('Conflicting original turn for an existing feedback receipt') from None
            if row['raw_question'] != item.raw_question:
                raise ValueError('Conflicting original question for an existing feedback receipt') from None
            return PoolReceipt(id=str(row['id']), created=False)

    async def assign(self, pool_id: str, *, matched_review_id: str | None, draft: NormalizedDraft) -> ReviewAssignment:
        async with self.database.session() as session, session.begin():
            return await self.assign_in_session(session, pool_id, matched_review_id=matched_review_id, draft=draft)

    async def assign_in_session(self, session, pool_id: str, *, matched_review_id: str | None, draft: NormalizedDraft) -> ReviewAssignment:
        pool_id = database_id(pool_id)
        if matched_review_id is not None:
            matched_review_id = database_id(matched_review_id)
        if not isinstance(draft, NormalizedDraft):
            raise ValueError('A validated normalized draft is required')
        pool = (await session.execute(text('SELECT * FROM low_confidence_questions '
            'WHERE id=:id FOR UPDATE'), {'id': int(pool_id)})).mappings().one_or_none()
        if pool is None:
            raise ValueError('Original pool question does not exist')
        state = _state(pool['processing'])
        if pool['matched_review_id'] is not None:
            review_id = str(pool['matched_review_id'])
            if matched_review_id not in (None, review_id):
                raise ValueError('Pool question already has a different deduplication target')
            review = await self._review(session, review_id, lock=True)
            return ReviewAssignment(pool_id=pool_id, review_id=review_id,
                occurrence_count=review['occurrence_count'], created=False)
        created = matched_review_id is None
        if created:
            result = await session.execute(text('INSERT INTO review_queue '
                '(normalized_question,ai_suggested_answer) VALUES(:question,:answer)'),
                {'question': draft.normalized_question, 'answer': draft.ai_suggested_answer})
            review_id, count = database_id(str(result.lastrowid)), 1
        else:
            review_id = matched_review_id
            review = await self._review(session, review_id, lock=True)
            if review['review_status'] != '待审':
                raise ReviewChanged('Deduplication target is no longer pending')
            counted = False
            if pool['conversation_id'] is not None and pool['user_message_id'] is not None:
                counted = await session.scalar(text('SELECT id FROM low_confidence_questions '
                    'WHERE conversation_id=:conversation AND user_message_id=:message '
                    'AND matched_review_id=:review AND id<>:pool LIMIT 1'),
                    {'conversation': pool['conversation_id'], 'message': pool['user_message_id'],
                     'review': int(review_id), 'pool': int(pool_id)}) is not None
            count = int(review['occurrence_count']) + (not counted)
            if count >= 2**32:
                raise ValueError('Review occurrence count has reached storage capacity')
            if not counted:
                await session.execute(text('UPDATE review_queue SET occurrence_count=:count WHERE id=:id'),
                                      {'count': count, 'id': int(review_id)})
        updated = state.model_dump(mode='json')
        updated.update(status='matched', next_attempt_at=None, last_error=None,
                       normalized_draft=draft.model_dump(mode='json'))
        updated_state = ProcessingState.model_validate_json(json.dumps(updated, ensure_ascii=False))
        await session.execute(text('UPDATE low_confidence_questions '
            'SET matched_review_id=:review,processing=:processing WHERE id=:id'),
            {'review': int(review_id), 'processing': updated_state.model_dump_json(), 'id': int(pool_id)})
        receipt = ReviewAssignment(pool_id=pool_id, review_id=review_id,
                                   occurrence_count=count, created=created)
        return receipt

    async def _review(self, session, review_id, *, lock=False):
        row = (await session.execute(text('SELECT * FROM review_queue WHERE id=:id' +
            (' FOR UPDATE' if lock else '')), {'id': int(database_id(review_id))})).mappings().one_or_none()
        if row is None:
            raise ReviewChanged('Review gap no longer exists')
        return row_dict(row)

    async def get_review(self, review_id: str) -> dict:
        async with self.database.session() as session:
            return await self._review(session, review_id)

    async def list_reviews(self, *, status: str, offset: int = 0, limit: int = 20) -> dict:
        _page(offset, limit)
        if status not in ('待审', '通过', '驳回'):
            raise ValueError('Invalid review status')
        async with self.database.session() as session:
            count = await session.scalar(text('SELECT COUNT(*) FROM review_queue WHERE review_status=:status'),
                                         {'status': status})
            rows = (await session.execute(text('SELECT * FROM review_queue WHERE review_status=:status '
                'ORDER BY occurrence_count DESC,id DESC LIMIT :limit OFFSET :offset'),
                {'status': status, 'limit': limit, 'offset': offset})).mappings()
            return {'items': [row_dict(row) for row in rows], 'total': int(count)}

    async def review_details(self, review_id: str, *, offset: int = 0, limit: int = 50) -> dict:
        _page(offset, limit)
        async with self.database.session() as session:
            review = await self._review(session, review_id)
            args = {'id': int(database_id(review_id)), 'limit': limit, 'offset': offset}
            count = await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions '
                                               'WHERE matched_review_id=:id'), args)
            rows = (await session.execute(text('SELECT * FROM low_confidence_questions '
                'WHERE matched_review_id=:id ORDER BY id ASC LIMIT :limit OFFSET :offset'), args)).mappings()
            return {'review': review, 'raw_questions': [row_dict(row) for row in rows], 'total': int(count)}

    async def approve_review(self, review_id, *, approved_answer, normalized_question=None):
        from app.core.errors import ServiceError
        from app.flywheel.publication import publication_receipt
        from app.flywheel.types import PublicationState
        from app.repositories.knowledge import KnowledgeRepository
        from app.knowledge.types import ChunkDraft
        async with self.database.session() as session, session.begin():
            row = await self._review(session, review_id, lock=True)
            question = normalized_question if normalized_question is not None else row['normalized_question']
            if row['review_status'] == '通过' and row['publication'] is not None:
                if row['approved_answer'] == approved_answer and row['normalized_question'] == question:
                    return publication_receipt(row)
            elif row['review_status'] == '待审':
                ids = await KnowledgeRepository(self.database).add_chunks_in_session(session, [
                    ChunkDraft('人工审核', question, approved_answer,
                        section_path='飞轮审核/' + review_id, content_type='faq')])
                state = PublicationState()
                await session.execute(text("UPDATE review_queue SET review_status='通过',"
                    'normalized_question=:q,approved_answer=:a,knowledge_chunk_id=:k,publication=:p WHERE id=:id'),
                    {'q': question, 'a': approved_answer, 'k': ids[0], 'p': state.model_dump_json(), 'id': int(review_id)})
                row.update(knowledge_chunk_id=str(ids[0]), publication=state.model_dump(mode='json'))
                return publication_receipt(row)
            raise ServiceError('review_conflict', '审核状态或核准内容与已有记录冲突。', 409)

    async def reject_review(self, review_id, *, reason):
        from app.core.errors import ServiceError
        from app.flywheel.types import PublicationState, TaskError
        async with self.database.session() as session, session.begin():
            row = await self._review(session, review_id, lock=True)
            if (row['review_status'] == '驳回' and row['publication'] is not None
                    and row['publication'].get('last_error', {}).get('message') == reason):
                return
            if row['review_status'] != '待审':
                raise ServiceError('review_conflict', '审核状态已经改变。', 409)
            state = PublicationState(status='failed', last_error=TaskError(code='review_rejected',
                stage='human_review', message=reason))
            await session.execute(text("UPDATE review_queue SET review_status='驳回',publication=:p WHERE id=:id"),
                {'p': state.model_dump_json(), 'id': int(review_id)})

    def publication_lease(self):
        from app.flywheel.leases import processing_lease
        return processing_lease(self.database, prefix='ch03:')

    async def claim_publication(self, lease, review_id, now):
        from app.flywheel.publication import publication_state
        async with lease.transaction() as session:
            row = await self._review(session, review_id, lock=True)
            state = publication_state(row)
            if (row['review_status'] != '通过' or state.status != 'pending' or state.attempt_count >= 2**32-1
                    or state.next_attempt_at is not None and state.next_attempt_at > now):
                return None
            state.status, state.attempt_count, state.next_attempt_at = 'running', state.attempt_count + 1, None
            await self._write_publication(session, review_id, state)
            return row, state

    async def _write_publication(self, session, review_id, state):
        # Roundtrip strict validation before committing mutable metadata.
        from app.flywheel.types import PublicationState
        state = PublicationState.model_validate_json(state.model_dump_json())
        await session.execute(text('UPDATE review_queue SET publication=:p WHERE id=:id'),
            {'p': state.model_dump_json(), 'id': int(database_id(review_id))})

    async def save_publication(self, lease, review_id, state):
        async with lease.transaction() as session:
            row = await self._review(session, review_id, lock=True)
            if row['review_status'] != '通过':
                raise ValueError('Publication no longer approved')
            if state.status == 'ready':
                committed = (await session.execute(text('SELECT vectorize_status,vector_id FROM knowledge_chunks '
                    'WHERE id=:id FOR UPDATE'), {'id': int(row['knowledge_chunk_id'])})).one_or_none()
                if committed is None or committed[0] != 'done' or committed[1] != row['knowledge_chunk_id']:
                    raise ValueError('Publication knowledge is not durably ready')
            await self._write_publication(session, review_id, state)

    async def next_publication_id(self, now):
        from app.flywheel.publication import publication_state
        after = 0
        while True:
            async with self.database.session() as session:
                rows = (await session.execute(text("SELECT * FROM review_queue WHERE review_status='通过' "
                    "AND publication IS NOT NULL AND JSON_UNQUOTE(JSON_EXTRACT(publication,'$.status'))='pending' "
                    'AND id>:after ORDER BY id LIMIT 100'), {'after': after})).mappings().all()
            for row in rows:
                state = publication_state(row)
                if state.next_attempt_at is None or state.next_attempt_at <= now:
                    return str(row['id'])
            if len(rows) < 100:
                return None
            after = rows[-1]['id']

    async def recover_publications(self, lease):
        from app.flywheel.publication import publication_state
        from app.flywheel.types import TaskError
        async with lease.transaction() as session:
            rows = (await session.execute(text("SELECT * FROM review_queue WHERE review_status='通过' "
                "AND publication IS NOT NULL AND JSON_UNQUOTE(JSON_EXTRACT(publication,'$.status'))='running' "
                'ORDER BY id FOR UPDATE'))).mappings().all()
            for row in rows:
                state = publication_state(row)
                state.status = 'pending' if state.attempt_count < 3 else 'failed'
                state.next_attempt_at = None
                state.last_error = TaskError(code='interrupted', stage='publication',
                    message='上次发布被中断，保留原知识ID。')
                await self._write_publication(session, str(row['id']), state)

    async def retry_publication(self, review_id):
        from app.core.errors import ServiceError
        from app.flywheel.publication import publication_state, publication_receipt
        async with self.database.session() as session, session.begin():
            row = await self._review(session, review_id, lock=True)
            state = publication_state(row)
            if row['review_status'] != '通过' or state.status == 'running':
                raise ServiceError('review_conflict', '当前审核状态不允许重试。', 409)
            if state.status in ('ready', 'pending'):
                return publication_receipt(row)
            if state.attempt_count >= 2**32-1:
                raise ServiceError('review_conflict', '累计发布次数达到存储上限，保留失败记录。', 409)
            state.status, state.next_attempt_at, state.last_error = 'pending', None, None
            await self._write_publication(session, review_id, state)
            row['publication'] = state.model_dump(mode='json')
            return publication_receipt(row)
