"""Synthetic annotated QA evaluation; never reads persisted customer transcripts."""
import argparse
import asyncio
from contextlib import AsyncExitStack
import json
from pathlib import Path

from app.config import load_settings
from app.core.llm import create_model
from app.knowledge.extraction import QAExtractor, QAResult
from app.knowledge.mining import normalize_qa
from app.knowledge.types import ConversationTranscript
from app.repositories.records import MessageRecord


def transcripts(case):
    return [ConversationTranscript(c['id'], c['messages'][-1]['id'], [
        MessageRecord(m['id'], m['role'], m.get('content'), m.get('tool_calls'), m.get('tool_call_id'))
        for m in c['messages']]) for c in case['conversations']]


def score(case, qas):
    # Evaluate unique QA, as global exact dedup does. Annotations allow natural
    # question paraphrases, but require every answer term and reject extra QA.
    unique = list(dict.fromkeys(normalize_qa(q.question, q.answer) for q in qas))
    unmatched = unique.copy()
    for expected in case['expected']:
        match = next((pair for pair in unmatched if
            all(term in pair[0] for term in expected['question_terms']) and
            all(term in pair[1] for term in expected['answer_terms']) and
            not any(term in pair[0] + pair[1] for term in case.get('forbidden_terms', []))), None)
        if match is None:
            return False
        unmatched.remove(match)
    return not unmatched


async def evaluate(path: Path, *, controlled: bool = False, case_ids: list[str] | None = None):
    cases = [json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    if case_ids:
        if set(case_ids) - {c['id'] for c in cases}:
            raise ValueError('unknown case id')
        cases = [c for c in cases if c['id'] in case_ids]
    results = []
    async with AsyncExitStack() as resources:
        if not controlled:
            settings = load_settings()
            model = create_model(settings.model_copy(update={'max_output_tokens': settings.qa_max_output_tokens}))
            resources.callback(model.root_client.close)
            resources.push_async_callback(model.root_async_client.close)
            extractor = QAExtractor(model, settings.input_token_budget)
        for case in cases:
            try:
                if controlled:
                    # Strict schema + source membership on the annotated fixtures.
                    parsed = QAResult.model_validate_json(json.dumps({'qas': case['controlled_output']}, ensure_ascii=False))
                    sources = {f'conversation:{c.id}:message:{c.last_message_id}' for c in transcripts(case)}
                    passed = all(q.source_ref in sources for q in parsed.qas) and score(case, parsed.qas)
                    count = len(parsed.qas)
                else:
                    qas = await extractor.extract(transcripts(case))
                    passed, count = score(case, qas), len(qas)
                results.append({'case': case['id'], 'class': case['class'], 'passed': passed, 'extracted': count})
            except Exception as exc:
                # Never print validation operands, keys, prompts or response text.
                entry = {'case': case['id'], 'class': case['class'], 'passed': False, 'error_type': type(exc).__name__}
                if hasattr(exc, 'code'):
                    entry['error_code'] = exc.code
                if exc.__cause__ is not None:
                    entry['cause_type'] = type(exc.__cause__).__name__
                    completion = getattr(exc.__cause__, 'completion', None)
                    if completion is not None:
                        entry['finish_reasons'] = [c.finish_reason for c in completion.choices]
                        if completion.usage is not None:
                            entry['completion_tokens'] = completion.usage.completion_tokens
                results.append(entry)
    return {'mode': 'controlled' if controlled else 'live',
        'qa_output_budget': None if controlled else settings.qa_max_output_tokens,
        'passed': sum(r['passed'] for r in results), 'total': len(results), 'cases': results}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', type=Path, default=Path(__file__).with_name('qa_extraction_cases.jsonl'))
    parser.add_argument('--controlled', action='store_true')
    parser.add_argument('--case', action='append', dest='case_ids', help='Run only affected annotated cases')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        report = asyncio.run(evaluate(args.cases, controlled=args.controlled, case_ids=args.case_ids))
        payload = json.dumps(report, ensure_ascii=False, indent=2)
        if args.output:
            args.output.write_text(payload + '\n', encoding='utf-8')
        print(payload)
        return 0 if report['passed'] == report['total'] else 1
    except Exception as exc:
        print(f'QA evaluation failed ({type(exc).__name__})')
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
