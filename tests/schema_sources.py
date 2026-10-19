"""Locate the archived original chapter DDL independently of Markdown fences."""
from pathlib import Path


def ch04_original_ddl():
    prompt = Path('prompt.md').read_text(encoding='utf-8')
    start = prompt.index('-- =============================================================\n-- ch04 · RAG 进阶')
    end_marker = "COMMENT='ch04 忠实度编造个案台账';"
    end = prompt.index(end_marker, start) + len(end_marker)
    return prompt[start:end]
