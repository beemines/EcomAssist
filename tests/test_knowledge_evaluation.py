"""Report correctness, fail-closed gates and recovery assertions; no cloud quality claims."""

import importlib

import pytest


def implementation(name='evaluate_knowledge'):
    try:
        return importlib.import_module('evals.' + name)
    except ModuleNotFoundError:
        pytest.fail('knowledge acceptance harness is missing')


CASES = [
    {'id': 'shipping', 'query': '邮费是多少', 'expected_sections': ['政策/配送']},
    {'id': 'outside', 'query': '火星天气', 'expected_sections': []},
]


class ExternalFAQ:
    async def search(self, query):
        if query == '邮费是多少':
            return [{'id': 7, 'question': '配送费用', 'answer': '演示8元', 'category': '政策'}]
        return []


async def test_report_records_actual_ids_and_does_not_call_quality_human_review_passed():
    report = await implementation().evaluate_retrieval(ExternalFAQ(), CASES, {7: '政策/配送'})
    assert (report['attempted'], report['not_attempted'], report['passed']) == (2, 0, 2)
    assert report['cases'][0]['expected_hit_ids'] == [7]
    assert report['cases'][0]['actual_hit_ids'] == [7]
    assert report['cases'][0]['tool_result']['found'] is True
    assert report['cases'][0]['answer_review'] == 'not_applicable_retrieval_only'
    assert report['cases'][0]['latency_seconds'] >= 0


async def test_external_failure_stops_remaining_requests_and_omits_exception_contents():
    class Broken:
        async def search(self, query):
            raise RuntimeError('PRIVATE KEY OR DOCUMENT')

    report = await implementation().evaluate_retrieval(Broken(), CASES, {7: '政策/配送'})
    assert (report['attempted'], report['not_attempted'], report['passed']) == (1, 1, 0)
    assert report['cases'][0]['error_type'] == 'RuntimeError'
    assert report['cases'][1]['error_code'] == 'not_attempted'
    assert 'PRIVATE' not in str(report)


async def test_unknown_chapter_fails_closed_before_external_requests():
    report = await implementation().evaluate_retrieval(ExternalFAQ(), CASES, {7: '错误章节'})
    assert (report['attempted'], report['not_attempted']) == (0, 2)
    assert report['error_code'] == 'missing_gold_section'


async def test_dense_domain_leakage_is_a_reported_failure_not_fabricated_empty_result():
    class DenseFAQ(ExternalFAQ):
        async def search(self, query):
            return await super().search('邮费是多少')

    report = await implementation().evaluate_retrieval(DenseFAQ(), CASES, {7: '政策/配送'})
    assert report['attempted'] == 2
    assert report['passed'] == 1
    assert report['cases'][1]['actual_hit_ids'] == [7]
    assert report['cases'][1]['passed'] is False


async def test_app_audit_rejects_wrong_knowledge_even_with_good_sse_and_persisted_answer(monkeypatch):
    from langchain_core.messages import AIMessage, AIMessageChunk
    from tests.fakes import ConversationStore, StreamingModel, fake_settings
    from app.main import create_app
    module = implementation()
    repository = ConversationStore()
    model = StreamingModel([AIMessageChunk(content='合成演示8元'),
        AIMessageChunk(content='', response_metadata={'finish_reason': 'stop'})])
    model.selected = AIMessage('', tool_calls=[{'id': 'shipping-1', 'name': 'query_faq',
        'args': {'keyword': '邮费'}}], response_metadata={'finish_reason': 'tool_calls'})
    class FAQ:
        async def search(self, keyword, limit=3):
            return [{'id': 99, 'question': '配送', 'answer': '8元', 'category': '演示'}]
    faq = FAQ()
    monkeypatch.setattr(module, 'ConversationRepository', lambda database: repository)
    monkeypatch.setattr(module, 'create_app', lambda settings, **kwargs:
        create_app(settings, model=model, repository=repository, faq_repository=faq))
    result = await module.evaluate_app(fake_settings(), None, faq, [7], 'synthetic')
    assert result['passed'] is False
    assert result['persisted_final_answer'] is True
    assert result['actual_hit_ids'] == [99]
    assert result['stream']['done_count'] == 1
    assert result['answer_review'] == 'pending_manual_fact_review'


def snapshot():
    return {'rows': [{'id': 11, 'status': 'done', 'vector_id': '11', 'body_sha256': 'original'}],
            'vector_ids': [11], 'unique_vector_count': 1, 'vector_row_count': 1}


def test_recovery_requires_done_matching_primary_keys_unchanged_bodies_and_no_duplicate_ids():
    module = implementation('knowledge_recovery')
    before = snapshot()
    before['rows'][0]['status'] = 'pending'
    before['rows'][0]['vector_id'] = None
    assert module.recovery_passed(before, snapshot(), [11]) is True


@pytest.mark.parametrize('mutation', ['pending', 'wrong_vector_id', 'lost_body', 'duplicate', 'missing_row'])
def test_recovery_cannot_report_success_for_partial_or_duplicate_recovery(mutation):
    after = snapshot()
    if mutation == 'pending':
        after['rows'][0]['status'] = 'pending'
    elif mutation == 'wrong_vector_id':
        after['rows'][0]['vector_id'] = '99'
    elif mutation == 'lost_body':
        after['rows'][0]['body_sha256'] = 'changed'
    elif mutation == 'duplicate':
        after.update(vector_ids=[11, 11], vector_row_count=2)
    else:
        after['rows'] = []
    assert implementation('knowledge_recovery').recovery_passed(snapshot(), after, [11]) is False


async def test_spawned_process_handle_is_the_python_process_writing_checkpoint(monkeypatch, tmp_path):
    """Windows venv python.exe is a redirector; killing its PID is not the boundary proof."""
    import json
    import subprocess
    module = implementation('knowledge_recovery')
    original_popen = subprocess.Popen
    checkpoint = tmp_path / 'pid.json'
    def launch_probe(command, **kwargs):
        # Replace only slow DB/cloud workload with a harmless real OS child.
        source = ('import os,json,time; from pathlib import Path; '
            f'Path({str(checkpoint)!r}).write_text(json.dumps({{"owned_pid":os.getpid()}})); time.sleep(.4)')
        return original_popen([command[0], '-c', source], **kwargs)
    monkeypatch.setattr(subprocess, 'Popen', launch_probe)
    process = module.spawn_owned('normal', checkpoint, 'knowledge_test_probe', 'recovery_probe', [])
    try:
        observed = await module.wait_checkpoint(process, checkpoint, timeout=5)
        assert observed['owned_pid'] == process.pid
    finally:
        process.wait(timeout=5)
