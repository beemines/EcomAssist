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


def failing_cleanup_io(monkeypatch, module):
    """Only substitute remote/process I/O; execute the real harness/report/CLI."""
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    trace = []
    class Session:
        @asynccontextmanager
        async def begin(self):
            yield self
        async def scalars(self, statement):
            return SimpleNamespace(all=lambda: [])
        async def execute(self, statement):
            trace.append('mysql_delete')
    class Database:
        def __init__(self, url): pass
        @asynccontextmanager
        async def session(self):
            trace.append('mysql_cleanup')
            raise ConnectionError('PRIVATE mysql operands')
            yield Session()
        async def dispose(self):
            trace.append('database_dispose')
            raise OSError('PRIVATE credentials')
    class Index:
        def __init__(self, uri, collection, timeout):
            self._client, self.collection, self.timeout = self, collection, timeout
        async def ensure_collection(self): trace.append('ensure_collection')
        async def describe_collection(self, *args, **kwargs):
            return {'auto_id': False, 'consistency_level': 0, 'fields': []}
        async def has_collection(self, *args, **kwargs): return True
        async def drop_collection(self, *args, **kwargs):
            trace.append('milvus_drop')
            raise TimeoutError('PRIVATE endpoint')
        async def aclose(self):
            trace.append('index_close')
            raise RuntimeError('PRIVATE client')
    class Embedder:
        def __init__(self, settings): pass
        async def embed(self, texts): return [[0.0] * 1024]
        async def aclose(self):
            trace.append('embedder_close')
            raise ArithmeticError('PRIVATE client')
    monkeypatch.setattr(module, 'test_settings', lambda: SimpleNamespace(database_url='synthetic',
        milvus_uri='http://127.0.0.1:19530', milvus_timeout_seconds=5,
        embedding_model='BAAI/bge-m3', llm_model='synthetic', max_output_tokens=512))
    monkeypatch.setattr(module, 'Database', Database)
    monkeypatch.setattr(module, 'MilvusIndex', Index)
    monkeypatch.setattr(module, 'SiliconFlowEmbedder', Embedder)
    return trace


@pytest.mark.parametrize('primary_failure', [True, False])
def test_dense_cli_always_writes_failed_report_and_attempts_every_cleanup(monkeypatch, tmp_path, capsys, primary_failure):
    import json
    from types import SimpleNamespace
    module = implementation()
    trace = failing_cleanup_io(monkeypatch, module)
    async def import_document(*args):
        if primary_failure:
            raise ValueError('PRIVATE document')
        return [7]
    class Repository:
        def __init__(self, database): pass
        async def get_done(self, ids): return [SimpleNamespace(id=7, section_path='政策/配送')]
    class Worker:
        def __init__(self, *args): pass
        async def run(self): return 1
    async def app(*args): return {'attempted': 1, 'not_attempted': 0, 'passed': True}
    monkeypatch.setattr(module, 'import_document', import_document)
    monkeypatch.setattr(module, 'KnowledgeRepository', Repository)
    monkeypatch.setattr(module, 'PendingVectorizer', Worker)
    monkeypatch.setattr(module, 'FAQRepository', lambda *args: ExternalFAQ())
    monkeypatch.setattr(module, 'evaluate_app', app)
    cases_path, output = tmp_path / 'cases.jsonl', tmp_path / 'report.json'
    cases_path.write_text('\n'.join(json.dumps(case) for case in CASES), encoding='utf-8')
    assert module.main(['--cases', str(cases_path), '--output', str(output)]) == 1
    assert output.exists(), 'cleanup exceptions must not bypass the JSON writer'
    report = json.loads(output.read_text(encoding='utf-8'))
    assert report['acceptance_passed'] is False
    assert report['cleanup'] == 'failed'
    assert report['finished_at']
    assert set(trace) >= {'mysql_cleanup', 'milvus_drop', 'index_close', 'embedder_close', 'database_dispose'}
    assert {error['error_type'] for error in report['cleanup_errors']} == {
        'ConnectionError', 'TimeoutError', 'RuntimeError', 'ArithmeticError', 'OSError'}
    if primary_failure:
        assert report['error_type'] == 'ValueError'
        assert (report['retrieval']['attempted'], report['retrieval']['not_attempted']) == (0, 2)
        assert (report['app']['attempted'], report['app']['not_attempted']) == (0, 1)
    else:
        assert (report['retrieval']['attempted'], report['retrieval']['not_attempted']) == (2, 0)
        assert (report['app']['attempted'], report['app']['not_attempted']) == (1, 0)
    assert 'PRIVATE' not in output.read_text(encoding='utf-8') + capsys.readouterr().out


def test_recovery_cli_preserves_primary_failure_through_process_mysql_milvus_and_close_failures(monkeypatch, tmp_path, capsys):
    import json
    from types import SimpleNamespace
    module = implementation('knowledge_recovery')
    trace = failing_cleanup_io(monkeypatch, module)
    monkeypatch.setattr(module, 'spawn_owned', lambda *args: SimpleNamespace(pid=54321))
    async def failed_checkpoint(*args): raise LookupError('PRIVATE process context')
    async def failed_wait(process):
        trace.append('process_wait')
        raise ChildProcessError('PRIVATE process context')
    monkeypatch.setattr(module, 'wait_checkpoint', failed_checkpoint)
    monkeypatch.setattr(module, 'terminate_owned', failed_wait)
    output = tmp_path / 'recovery.json'
    assert module.main(['--output', str(output)]) == 1
    assert output.exists(), 'cleanup exceptions must not bypass the JSON writer'
    report = json.loads(output.read_text(encoding='utf-8'))
    assert (report['attempted'], report['not_attempted'], report['passed']) == (1, 1, False)
    assert report['cases'][0]['error_type'] == 'LookupError'
    assert report['cleanup'] == report['cases'][0]['cleanup'] == 'failed'
    assert set(trace) >= {'process_wait', 'mysql_cleanup', 'milvus_drop', 'index_close', 'database_dispose'}
    assert {error['error_type'] for error in report['cleanup_errors']} == {
        'ChildProcessError', 'ConnectionError', 'TimeoutError', 'RuntimeError', 'OSError'}
    assert 'PRIVATE' not in output.read_text(encoding='utf-8') + capsys.readouterr().out


async def test_app_keeps_route_timeout_when_http_client_exit_also_fails(monkeypatch):
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    from tests.fakes import fake_settings
    module = implementation()
    @asynccontextmanager
    async def lifespan(app): yield
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): raise OSError('PRIVATE client credentials')
    async def failed_create(*args): return {'conversation_id': None, 'error_code': 'timeout'}
    monkeypatch.setattr(module, 'create_app', lambda *args, **kwargs:
        SimpleNamespace(router=SimpleNamespace(lifespan_context=lifespan)))
    monkeypatch.setattr(module.httpx, 'AsyncClient', Client)
    monkeypatch.setattr(module, 'create_conversation', failed_create)
    result = await module.evaluate_app(fake_settings(), None, None, [7], 'synthetic')
    assert result['error_code'] == 'timeout'
    assert (result['attempted'], result['not_attempted'], result['passed']) == (1, 0, False)
    assert result['cleanup_errors'] == [{'action': 'http_client_exit', 'error_type': 'OSError'}]
    assert 'PRIVATE' not in str(result)


async def test_app_preserves_audit_failure_type_when_client_exit_also_fails(monkeypatch):
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    from tests.fakes import fake_settings
    module = implementation()
    @asynccontextmanager
    async def lifespan(app): yield
    class Client:
        def __init__(self, **kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self, *args): raise OSError('PRIVATE close operands')
    async def create(*args): return {'conversation_id': '1', 'error_code': None}
    async def stream(*args, **kwargs): return {'text': '合成正文', 'error_code': None}
    async def load(*args): raise LookupError('PRIVATE audit operands')
    monkeypatch.setattr(module, 'create_app', lambda *args, **kwargs:
        SimpleNamespace(router=SimpleNamespace(lifespan_context=lifespan)))
    monkeypatch.setattr(module.httpx, 'AsyncClient', Client)
    monkeypatch.setattr(module, 'create_conversation', create)
    monkeypatch.setattr(module, 'chat_round', stream)
    monkeypatch.setattr(module, 'ConversationRepository', lambda *args: SimpleNamespace(load_messages=load))
    result = await module.evaluate_app(fake_settings(), None, None, [7], 'synthetic')
    assert result['error_type'] == 'LookupError'
    assert result['cleanup_errors'] == [{'action': 'http_client_exit', 'error_type': 'OSError'}]
    assert result['passed'] is False
    assert 'PRIVATE' not in str(result)
