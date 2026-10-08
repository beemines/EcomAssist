from collections import Counter

import pytest


def chunk(text, **kwargs):
    try:
        from app.knowledge.chunking import chunk_markdown
    except ImportError:
        pytest.fail("Markdown chunker is missing")
    return chunk_markdown(text, document_name=kwargs.pop("document_name", "政策"),
                          content_type=kwargs.pop("content_type", "policy"), **kwargs)


def test_atx_stack_preserves_paths_and_parent_categories():
    rows = chunk("# 售后\n## 退货\n七天内可申请。\n#### 例外 ###\n特殊说明。\n## 换货\n可以换货。")
    assert [(r.category, r.questions, r.answer, r.section_path) for r in rows] == [
        ("售后", "退货", "七天内可申请。", "售后/退货"),
        ("售后/退货", "例外", "特殊说明。", "售后/退货/例外"),
        ("售后", "换货", "可以换货。", "售后/换货")]
    assert all(r.content_type == "policy" for r in rows)


@pytest.mark.parametrize("fence", ["```", "~~~~"])
def test_fenced_hashes_are_body_not_headings(fence):
    text = f"# 示例\n{fence}python\n# 保留注释\nQ: 代码内容\n{fence}\n完成。"
    rows = chunk(text, content_type="faq")
    assert len(rows) == 1
    assert rows[0].answer == f"{fence}python\n# 保留注释\nQ: 代码内容\n{fence}\n\n完成。"
    assert rows[0].questions == "示例"


def test_no_heading_uses_document_name_and_important_is_explicit():
    rows = chunk("普通重要条款。\n\n> [!IMPORTANT]\n> 演示关键条款。", document_name="说明", target_chars=18, overlap_chars=0)
    assert [(r.category, r.questions, r.section_path) for r in rows] == [("说明", "说明", "说明")] * 2
    assert [r.is_key_clause for r in rows] == [False, True]


def test_important_marker_inside_fence_is_literal_code():
    rows = chunk("```markdown\n> [!IMPORTANT]\n> 仅显示代码。\n```", content_type="manual")
    assert rows[0].is_key_clause is False


def test_faq_explicit_alternative_questions_and_multiple_groups():
    rows = chunk("# 配送\nQ: 邮费是多少？\n问：快递费用怎么收？\nA: 标准配送 8 元。\n满 99 元包邮。\n\nQ: 几天送达？\n答：演示范围三天。", content_type="faq")
    assert [(r.questions, r.answer) for r in rows] == [
        ("邮费是多少？\n快递费用怎么收？", "标准配送 8 元。\n满 99 元包邮。"),
        ("几天送达？", "演示范围三天。")]
    assert all(r.section_path == "配送" for r in rows)


@pytest.mark.parametrize("body,want", [
    ('他说：“可以退货。”然后完成！', ['他说：“可以退货。”', '然后完成！']),
    ('She said "Yes!" Next sentence.', ['She said "Yes!"', 'Next sentence.']),
    ('价格为 8.50 元。次日送达。', ['价格为 8.50 元。', '次日送达。']),
])
def test_complete_sentences_keep_closing_quotes_and_decimal(body, want):
    assert [r.answer for r in chunk(body, target_chars=10, overlap_chars=0)] == want


def test_overlap_uses_only_complete_suffix_sentences_and_covers_body():
    rows = chunk("甲甲。乙乙。丙丙。丁丁。戊戊。", target_chars=9, overlap_chars=3)
    assert [r.answer for r in rows] == ["甲甲。乙乙。丙丙。", "丙丙。丁丁。戊戊。"]
    assert rows[0].answer + rows[1].answer[3:] == "甲甲。乙乙。丙丙。丁丁。戊戊。"


def test_overlap_never_cuts_an_overlong_sentence():
    assert [r.answer for r in chunk("很长很长很长的完整一句。下一句。", target_chars=6, overlap_chars=3)] == ["很长很长很长的完整一句。", "下一句。"]


def test_default_overlap_repeats_only_prose_after_fenced_code():
    code = "```\n" + "x" * 130 + "!\n```"
    long_sentence = "B" * 1100 + "."
    rows = chunk(code + "\n\nA.\n\n" + long_sentence)
    assert [r.answer for r in rows] == [code + "\n\nA.", "A.\n\n" + long_sentence]
    assert rows[1].answer.count("```") == 0


@pytest.mark.parametrize("following", ["", "\nQ: supplied second question?\nA: valid answer."])
def test_faq_rejects_empty_answer_regardless_of_group_position(following):
    with pytest.raises(ValueError, match="政策.*章节.*配送"):
        chunk("# 配送\nQ: supplied first question?\nA:   " + following, content_type="faq")


@pytest.mark.parametrize("following", ["", "\nQ: supplied second question?\nA: valid answer."])
def test_faq_rejects_empty_explicit_question_regardless_of_group_position(following):
    with pytest.raises(ValueError, match="政策.*章节.*配送"):
        chunk("# 配送\nQ:   \nA: supplied answer." + following, content_type="faq")


def test_paragraphs_are_packed_before_sentence_recursion():
    assert [r.answer for r in chunk("第一段。\n\n第二段。\n\n第三段。", target_chars=10, overlap_chars=0)] == ["第一段。\n\n第二段。", "第三段。"]


@pytest.mark.parametrize("body", ["", "   \n\n", "# 售后\n## 空白\n\n"])
def test_empty_body_is_rejected(body):
    with pytest.raises(ValueError, match="政策"):
        chunk(body)


def test_large_tables_repeat_headers_without_duplicate_data_rows():
    header = "| 项目 | 内容 |\n| --- | --- |"
    data = ["| A | 转义\\|竖线 |", "| B | `代码|竖线` |", "| C | ``双`代码|竖线`` |", "| D | 最后行 |"]
    rows = chunk(header + "\n" + "\n".join(data), target_chars=55)
    assert len(rows) == 4
    assert all(r.answer.startswith(header + "\n") for r in rows)
    counts = Counter(line for r in rows for line in r.answer.splitlines()[2:])
    assert counts == Counter({line: 1 for line in data})


def test_header_only_table_does_not_create_knowledge():
    with pytest.raises(ValueError, match="政策"):
        chunk("| 项目 | 内容 |\n| --- | --- |")


@pytest.mark.parametrize("text", ["# " + "标题" * 130 + "\n## 条款\n正文。", "# " + "甲" * 200 + "\n## " + "乙" * 200 + "\n### " + "丙" * 200 + "\n正文。", "# 超长\n" + "汉" * 22000 + "。", "# 超长\n| 项目 | 内容 |\n| --- | --- |\n| A | " + "汉" * 22000 + " |"], ids=["category", "path", "sentence", "table-row"])
def test_mysql_overflow_reports_document_and_section(text):
    with pytest.raises(ValueError, match="政策.*章节"):
        chunk(text)


@pytest.mark.parametrize("kwargs", [{"content_type": "unknown"}, {"target_chars": 0}, {"overlap_chars": -1}, {"target_chars": True}])
def test_invalid_chunk_options_are_rejected(kwargs):
    with pytest.raises(ValueError):
        chunk("正文。", **kwargs)
