"""Short MySQL transactions for original questions and deduplicated gaps."""
import json
from datetime import datetime

from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from app.flywheel.types import (
    NormalizedDraft, PoolInput, PoolReceipt, ProcessingState, ReviewAssignment,
    ReviewChanged, database_id,
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
        pool_id = database_id(pool_id)
        if matched_review_id is not None:
            matched_review_id = database_id(matched_review_id)
        if not isinstance(draft, NormalizedDraft):
            raise ValueError('A validated normalized draft is required')
        async with self.database.session() as session, session.begin():
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
