"""CPU material validation; semantic evaluation is an explicit separate step."""
import argparse
import json
from pathlib import Path
from app.flywheel.types import NormalizedDraft, ReviewCandidate, SemanticMatch


def load_cases(path):
    cases = [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]
    seen = set()
    for case in cases:
        if not isinstance(case['id'], str) or case['id'] in seen or not case['raw_question'].strip():
            raise ValueError('Invalid or duplicate labeled case')
        seen.add(case['id'])
        draft = NormalizedDraft(normalized_question=case['example_normalized_question'],
                                ai_suggested_answer=case['example_answer'])
        candidates = [ReviewCandidate.model_validate(row) for row in case['candidates']]
        match = SemanticMatch(matched_review_id=case['labels']['matched_review_id'])
        if match.matched_review_id is not None and match.matched_review_id not in {c.id for c in candidates}:
            raise ValueError('Labeled target must belong to its candidate batch')
        for key in ('must_keep', 'must_not'):
            if not isinstance(case['labels'][key], list) or any(not isinstance(v, str) or not v for v in case['labels'][key]):
                raise ValueError('Labels must name semantic facts or prohibited claims')
        if not case['labels']['answer_boundary'].strip() or not isinstance(case['evidence'], list):
            raise ValueError('Missing human answer boundary')
    return cases


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--offline', action='store_true', help='只核验材料结构，不调用模型')
    parser.add_argument('--cases', default='evals/flywheel_cases.jsonl')
    args = parser.parse_args(argv)
    cases = load_cases(args.cases)
    print(f'{len(cases)}组标注材料结构有效；未执行模型语义验证。')


if __name__ == '__main__':
    main()
