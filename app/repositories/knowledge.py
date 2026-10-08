from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import KnowledgeChunk, QAExtractionStaging
from app.db.session import Database
from app.knowledge.types import ChunkDraft, ChunkRecord, ExtractedQA, StagedQA, validate_id, validate_text


def _ids(values: list[int]) -> None:
    for value in values:
        validate_id(value)
    if len(set(values)) != len(values):
        raise ValueError("duplicate knowledge ids")


def _record(row: KnowledgeChunk) -> ChunkRecord:
    return ChunkRecord(category=row.category, questions=row.questions, answer=row.answer,
                       section_path=row.section_path, content_type=row.content_type,
                       is_key_clause=bool(row.is_key_clause), id=row.id,
                       prev_chunk_id=row.prev_chunk_id, next_chunk_id=row.next_chunk_id,
                       vector_id=row.vector_id, vectorize_status=row.vectorize_status)


async def _insert(session: AsyncSession, drafts: list[ChunkDraft], link_neighbors: bool = False) -> list[int]:
    rows = [KnowledgeChunk(**asdict(draft)) for draft in drafts]
    session.add_all(rows)
    await session.flush()
    for row in rows:
        validate_id(row.id)
    if link_neighbors:
        for index, row in enumerate(rows):
            row.prev_chunk_id = rows[index - 1].id if index else None
            row.next_chunk_id = rows[index + 1].id if index + 1 < len(rows) else None
        await session.flush()
    return [row.id for row in rows]


class KnowledgeRepository:
    """MySQL owns text and status; each call finishes its own short transaction."""

    def __init__(self, database: Database):
        self.database = database

    async def add_chunks(self, drafts: list[ChunkDraft], link_neighbors: bool = False) -> list[int]:
        async with self.database.session() as session, session.begin():
            return await _insert(session, drafts, link_neighbors)

    async def pending(self, limit: int = 20) -> list[ChunkRecord]:
        if type(limit) is not int or limit < 1:
            raise ValueError("pending limit must be a positive integer")
        async with self.database.session() as session, session.begin():
            rows = (await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.vectorize_status == "pending").order_by(KnowledgeChunk.id).limit(limit))).all()
            return [_record(row) for row in rows]

    async def mark_done(self, ids: list[int]) -> None:
        _ids(ids)
        if not ids:
            return
        async with self.database.session() as session, session.begin():
            rows = (await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.id.in_(ids)).with_for_update())).all()
            if len(rows) != len(ids):
                raise ValueError("cannot mark missing knowledge chunks done")
            for row in rows:
                row.vector_id = str(row.id)
                row.vectorize_status = "done"

    async def get_done(self, ids: list[int]) -> list[ChunkRecord]:
        _ids(ids)
        if not ids:
            return []
        async with self.database.session() as session, session.begin():
            rows = (await session.scalars(select(KnowledgeChunk).where(KnowledgeChunk.id.in_(ids), KnowledgeChunk.vectorize_status == "done"))).all()
            by_id = {row.id: row for row in rows}
            return [_record(by_id[identifier]) for identifier in ids if identifier in by_id]

    async def stage(self, batch_no: str, items: list[ExtractedQA]) -> int:
        validate_text("batch_no", batch_no, 64)
        async with self.database.session() as session, session.begin():
            # Include decided rows: a replay must not restage kept/discarded QA.
            rows = (await session.execute(select(QAExtractionStaging.source_ref,
                QAExtractionStaging.question, QAExtractionStaging.answer)
                .where(QAExtractionStaging.batch_no == batch_no))).all()
            seen = {tuple(row) for row in rows}
            added = []
            for item in items:
                key = (item.source_ref, item.question, item.answer)
                if key not in seen:
                    added.append(QAExtractionStaging(batch_no=batch_no, **asdict(item)))
                    seen.add(key)
            session.add_all(added)
            return len(added)

    async def extracted(self) -> list[StagedQA]:
        async with self.database.session() as session, session.begin():
            rows = (await session.scalars(select(QAExtractionStaging).where(QAExtractionStaging.status == "extracted").order_by(QAExtractionStaging.id))).all()
            return [StagedQA(source_ref=row.source_ref, question=row.question, answer=row.answer, id=row.id, batch_no=row.batch_no, status=row.status) for row in rows]

    async def qa_pairs(self) -> list[tuple[str, str]]:
        async with self.database.session() as session, session.begin():
            return [tuple(row) for row in (await session.execute(select(KnowledgeChunk.questions, KnowledgeChunk.answer).order_by(KnowledgeChunk.id))).all()]

    async def promote(self, kept_ids: list[int], discarded_ids: list[int]) -> list[int]:
        _ids(kept_ids)
        _ids(discarded_ids)
        if set(kept_ids) & set(discarded_ids):
            raise ValueError("kept and discarded ids overlap")
        ids = kept_ids + discarded_ids
        if not ids:
            return []
        async with self.database.session() as session, session.begin():
            rows = (await session.scalars(select(QAExtractionStaging).where(QAExtractionStaging.id.in_(ids)).order_by(QAExtractionStaging.id).with_for_update())).all()
            by_id = {row.id: row for row in rows}
            if len(rows) != len(ids):
                raise ValueError("cannot promote missing staged QA")
            for identifier in ids:
                target = "kept" if identifier in kept_ids else "discarded"
                if by_id[identifier].status not in ("extracted", target):
                    raise ValueError("staged QA decision conflicts with existing status")
            new_kept = [by_id[identifier] for identifier in kept_ids if by_id[identifier].status == "extracted"]
            new_ids = await _insert(session, [ChunkDraft("历史客服", row.question, row.answer, content_type="faq") for row in new_kept])
            for identifier in ids:
                by_id[identifier].status = "kept" if identifier in kept_ids else "discarded"
            return new_ids
