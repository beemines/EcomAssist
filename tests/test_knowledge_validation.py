import pytest


def types():
    try:
        from app.knowledge.types import ChunkDraft, ExtractedQA, embedding_text
    except ImportError:
        pytest.fail("knowledge types and validation are missing")
    return ChunkDraft, ExtractedQA, embedding_text


@pytest.mark.parametrize("field,value", [("category", "中" * 256), ("section_path", "中" * 513), ("questions", "中" * 21846), ("answer", "😀" * 16384), ("content_type", "x" * 33)], ids=["category", "section-path", "questions-bytes", "answer-bytes", "content-type"])
def test_chunk_rejects_mysql_overflow_without_truncation(field, value):
    Draft, _, _ = types()
    values = {"category": "退货", "questions": "怎么退", "answer": "联系客服", field: value}
    with pytest.raises(ValueError, match=field):
        Draft(**values)


def test_exact_mysql_character_and_utf8_byte_boundaries_are_preserved():
    Draft, _, _ = types()
    draft = Draft(category="中" * 255, questions="中" * 21845, answer="a" * 65535, section_path="中" * 512)
    assert len(draft.category) == 255 and len(draft.section_path) == 512
    assert len(draft.questions.encode("utf-8")) == 65535 and len(draft.answer) == 65535


def test_embedding_text_excludes_metadata():
    Draft, _, embedding_text = types()
    assert embedding_text(Draft("退货", "怎么退", "联系客服", section_path="秘密", content_type="faq", is_key_clause=True)) == "category: 退货\nquestions: 怎么退\nanswer: 联系客服"


@pytest.mark.parametrize("field,value", [("source_ref", "x" * 256), ("question", "中" * 21846), ("answer", "😀" * 16384)], ids=["source", "question-bytes", "answer-bytes"])
def test_staging_rejects_overflow(field, value):
    _, QA, _ = types()
    with pytest.raises(ValueError, match=field):
        QA(**{"source_ref": "test", "question": "问", "answer": "答", field: value})


def test_optional_embedding_secret_loads_without_exposing_value(tmp_path):
    from app.config import load_settings
    path = tmp_path / ".env"
    path.write_text("LLM_BASE_URL=https://example.com/v1/\nLLM_MODEL=test\nLLM_API_KEY=test\nSILICONFLOW_API_KEY=embedding-test-secret\n", encoding="utf-8")
    settings = load_settings(path)
    from pydantic import SecretStr
    assert settings.siliconflow_api_key == SecretStr("embedding-test-secret")
    assert "embedding-test-secret" not in repr(settings)
    assert "embedding-test-secret" not in settings.model_dump_json()
