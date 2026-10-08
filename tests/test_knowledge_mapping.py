import pytest


def models():
    try:
        from app.db.models import KnowledgeChunk, QAExtractionStaging
    except ImportError:
        pytest.fail("knowledge ORM mappings are missing")
    return KnowledgeChunk, QAExtractionStaging


def test_knowledge_mapping_preserves_authoritative_columns_and_constraints():
    chunk, staging = models()
    assert list(chunk.__table__.c.keys()) == ["id", "category", "questions", "answer", "section_path", "content_type", "is_key_clause", "prev_chunk_id", "next_chunk_id", "vector_id", "vectorize_status", "created_at", "updated_at"]
    assert list(staging.__table__.c.keys()) == ["id", "batch_no", "source_ref", "question", "answer", "status", "created_at"]
    for model in (chunk, staging):
        table = model.__table__
        assert table.c.id.type.unsigned and table.c.id.primary_key and table.c.id.autoincrement is True
        assert table.dialect_options["mysql"]["engine"] == "InnoDB"
        assert table.dialect_options["mysql"]["charset"] == "utf8mb4"
        assert str(table.c.created_at.server_default.arg) == "CURRENT_TIMESTAMP"
    c = chunk.__table__.c
    assert c.category.type.length == 255 and not c.category.nullable
    assert c.section_path.type.length == 512 and c.section_path.nullable
    assert c.content_type.type.length == 32 and c.vector_id.type.length == 64
    assert c.questions.type.__class__.__name__ == c.answer.type.__class__.__name__ == "TEXT"
    assert c.is_key_clause.type.display_width == 1
    assert str(c.is_key_clause.server_default.arg) == "0"
    assert c.vectorize_status.type.enums == ["pending", "done"]
    assert str(c.vectorize_status.server_default.arg) == "'pending'"
    assert str(c.updated_at.server_default.arg) == "CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    assert c.updated_at.server_onupdate is not None
    assert {(fk.name, fk.target_fullname, fk.ondelete) for fk in chunk.__table__.foreign_keys} == {("fk_chunks_prev", "knowledge_chunks.id", "SET NULL"), ("fk_chunks_next", "knowledge_chunks.id", "SET NULL")}
    assert {i.name for i in chunk.__table__.indexes} == {"idx_category", "idx_vectorize_status"}
    s = staging.__table__.c
    assert s.batch_no.type.length == 64 and not s.batch_no.nullable
    assert s.source_ref.type.length == 255 and s.source_ref.nullable
    assert s.status.type.enums == ["extracted", "kept", "discarded"]
    assert str(s.status.server_default.arg) == "'extracted'"
    assert {i.name for i in staging.__table__.indexes} == {"idx_batch_no", "idx_status"}
