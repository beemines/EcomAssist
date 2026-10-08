import json
from pathlib import Path

import pytest

from app.knowledge.extraction import QAResult
from evals.evaluate_qa import evaluate, score


def paraphrases_case():
    return next(json.loads(line) for line in Path('evals/qa_extraction_cases.jsonl').read_text(encoding='utf-8').splitlines()
        if json.loads(line)['id'] == 'distinct_phrasings')


@pytest.mark.parametrize('mutation', ['missing', 'rewritten', 'wrong_source', 'swapped_source', 'wrong_answer'])
def test_distinct_source_phrasings_requires_both_exact_normalized_questions_and_paired_sources(mutation):
    case = paraphrases_case()
    output = [dict(item) for item in case['controlled_output']]
    if mutation == 'missing': output.pop()
    elif mutation == 'rewritten': output[1]['question'] = '快递费用应当怎么收？'
    elif mutation == 'wrong_source': output[1]['source_ref'] = 'conversation:999:message:999'
    elif mutation == 'swapped_source': output[1]['source_ref'] = output[0]['source_ref']
    else: output[1]['answer'] = '标准配送费为12元。'
    assert score(case, QAResult.model_validate({'qas': output}).qas) is False


async def test_controlled_nine_labels_preserves_original_eight_and_accepts_normalized_source_phrasings():
    case = paraphrases_case()
    output = [dict(item) for item in case['controlled_output']]
    output[0]['question'] = '　邮费是多少?\n'
    assert score(case, QAResult.model_validate({'qas': output}).qas) is True
    report = await evaluate(Path('evals/qa_extraction_cases.jsonl'), controlled=True)
    assert (report['passed'], report['total']) == (9, 9)
    assert [r['case'] for r in report['cases']] == ['generic', 'duplicate', 'conflict', 'unanswered',
        'case_identifiers', 'refund_promise', 'mock_tool', 'injection', 'distinct_phrasings']
