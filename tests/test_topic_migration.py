"""Original step10 DDL is authoritative; additions preserve default FK semantics."""

from pathlib import Path

from app.quality.migration import _statements
from app.topics.migration import contracts


def test_original_ddl_is_preserved_and_nullable_tracking_columns_are_separate():
    base, complete, original, runtime = contracts()
    prompt = Path('docs/prompts/step-10-topic-classifier.md').read_text(encoding='utf-8')
    assert original[0] == runtime[0] == 'SET NAMES utf8mb4'
    assert original[1] in prompt
    assert [column[0] for column in base['columns']] == ['id', 'question_id', 'labels', 'classified_at']
    assert [column[0] for column in complete['columns']][-4:] == [
        'model_version', 'taxonomy_version', 'input_hash', 'batch_id']
    assert all(column[2] == 'YES' and column[3] is None for column in complete['columns'][-4:])
    assert dict((column[0], column[1]) for column in complete['columns'])['input_hash'] == 'char(64)'
    assert dict((column[0], column[1]) for column in complete['columns'])['batch_id'] == 'char(36)'


def test_unique_question_index_serves_restrict_fk_without_an_extra_mysql_index():
    base, complete, _, _ = contracts()
    assert base['foreign_keys'] == {('fk_topic_question', 'question_id', 'low_confidence_questions', 'id', 'RESTRICT', 'RESTRICT')}
    assert {item[0] for item in base['indexes']} == {'PRIMARY', 'uk_question_id'}
    assert ('uk_question_id', 'question_id', 1, 0, None, 'BTREE') in base['indexes']
    assert complete['foreign_keys'] == base['foreign_keys']
