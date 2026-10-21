import json
from pathlib import Path
import pytest
from evals.evaluate_flywheel import load_cases
from tests.test_flywheel_processing import JsonModel,raw


async def test_labeled_prompt_runner_persists_attempts_and_never_replays(tmp_path):
    from evals.evaluate_flywheel import evaluate_cases
    from app.flywheel.processing import PromptClient
    case=load_cases('evals/flywheel_cases.jsonl')[0]
    model=JsonModel([raw({'normalized_question':case['example_normalized_question'],
        'ai_suggested_answer':case['example_answer']}),raw({'matched_review_id':case['labels']['matched_review_id']})])
    result=await evaluate_cases([case],PromptClient(model),tmp_path,model_name='scripted')
    assert result['status']=='completed' and len(model.calls)==2
    assert result['records'][0]['checks']['dedup_exact']
    assert (tmp_path/'report.json').is_file()
    with pytest.raises(ValueError,match='already exists'):
        await evaluate_cases([case],PromptClient(model),tmp_path,model_name='scripted')
    assert len(model.calls)==2


async def test_invalid_prompt_response_stops_without_repair_or_next_case(tmp_path):
    from evals.evaluate_flywheel import evaluate_cases
    from app.flywheel.processing import PromptClient
    cases=load_cases('evals/flywheel_cases.jsonl')[:2]
    model=JsonModel([raw({'normalized_question':'wrong','ai_suggested_answer':'draft','status':'通过'})])
    result=await evaluate_cases(cases,PromptClient(model),tmp_path,model_name='scripted')
    assert result['status']=='failed' and len(model.calls)==1 and not result['records']
    assert result['error']['type']=='ServiceError'
