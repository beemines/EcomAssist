# 知识评估与恢复报告测试，防止部分恢复、错误来源或清理故障被误报为成功。
"""Report correctness, fail-closed gates and recovery assertions; no cloud quality claims."""

import importlib

import pytest


# 加载指定知识验收或恢复模块，缺失实现时报告明确失败。
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
    # 为配送查询返回固定知识命中，域外查询返回空结果。
    async def search(self, query):
        if query == '邮费是多少':
            return [{'id': 7, 'question': '配送费用', 'answer': '演示8元', 'category': '政策'}]
        return []


# 验证检索报告记录真实命中编号、耗时与结果，检索通过不会冒充人工质量验收。
async def test_report_records_actual_ids_and_does_not_call_quality_human_review_passed():
    report = await implementation().evaluate_retrieval(ExternalFAQ(), CASES, {7: '政策/配送'})
    assert (report['attempted'], report['not_attempted'], report['passed']) == (2, 0, 2)
    assert report['cases'][0]['expected_hit_ids'] == [7]
    assert report['cases'][0]['actual_hit_ids'] == [7]
    assert report['cases'][0]['tool_result']['found'] is True
    assert report['cases'][0]['answer_review'] == 'not_applicable_retrieval_only'
    assert report['cases'][0]['latency_seconds'] >= 0


# 验证外部检索故障停止后续请求，报告只保留错误类型并隐藏异常正文。
async def test_external_failure_stops_remaining_requests_and_omits_exception_contents():
    class Broken:
        # 抛出含私密数据的检索故障，用于检查失败报告脱敏和请求停止。
        async def search(self, query):
            raise RuntimeError('PRIVATE KEY OR DOCUMENT')

    report = await implementation().evaluate_retrieval(Broken(), CASES, {7: '政策/配送'})
    assert (report['attempted'], report['not_attempted'], report['passed']) == (1, 1, 0)
    assert report['cases'][0]['error_type'] == 'RuntimeError'
    assert report['cases'][1]['error_code'] == 'not_attempted'
    assert 'PRIVATE' not in str(report)


# 验证标准章节无法映射时在外部请求前终止验收。
async def test_unknown_chapter_fails_closed_before_external_requests():
    report = await implementation().evaluate_retrieval(ExternalFAQ(), CASES, {7: '错误章节'})
    assert (report['attempted'], report['not_attempted']) == (0, 2)
    assert report['error_code'] == 'missing_gold_section'


# 验证域外查询误命中的知识真实写入报告并判为失败，不能伪造为空结果。
async def test_dense_domain_leakage_is_a_reported_failure_not_fabricated_empty_result():
    class DenseFAQ(ExternalFAQ):
        # 无论查询内容都返回配送知识，模拟稠密检索的域外误命中。
        async def search(self, query):
            return await super().search('邮费是多少')

    report = await implementation().evaluate_retrieval(DenseFAQ(), CASES, {7: '政策/配送'})
    assert report['attempted'] == 2
    assert report['passed'] == 1
    assert report['cases'][1]['actual_hit_ids'] == [7]
    assert report['cases'][1]['passed'] is False


# 验证 SSE 和最终回答均成功时，错误知识编号仍让应用审计失败并等待人工事实复核。
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
        # 返回错误知识主键，构造流正常但知识来源不符的验收场景。
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


# 构造原文摘要、SQL 完成状态和唯一向量主键均一致的恢复快照。
def snapshot():
    return {'rows': [{'id': 11, 'status': 'done', 'vector_id': '11', 'body_sha256': 'original'}],
            'vector_ids': [11], 'unique_vector_count': 1, 'vector_row_count': 1}


# 验证恢复通过要求完成状态、主键匹配、原文未变且无重复向量。
def test_recovery_requires_done_matching_primary_keys_unchanged_bodies_and_no_duplicate_ids():
    module = implementation('knowledge_recovery')
    before = snapshot()
    before['rows'][0]['status'] = 'pending'
    before['rows'][0]['vector_id'] = None
    assert module.recovery_passed(before, snapshot(), [11]) is True


# 验证状态未完成、编号错配、正文改变、重复向量或缺行均不能报告恢复成功。
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


# 验证进程句柄 PID 对应实际写检查点的 Python 子进程，而非虚拟环境重定向器。
async def test_spawned_process_handle_is_the_python_process_writing_checkpoint(monkeypatch, tmp_path):
    """Windows venv python.exe is a redirector; killing its PID is not the boundary proof."""
    import json
    import subprocess
    module = implementation('knowledge_recovery')
    original_popen = subprocess.Popen
    checkpoint = tmp_path / 'pid.json'
    # 保留真实系统子进程但替换远端工作，写实际 PID 检查点以核对进程所有权。
    def launch_probe(command, **kwargs):
        # 只替换耗时的数据库和云端工作，仍用无业务副作用的真实子进程验证进程身份。
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


# 替换远端与资源清理边界，集中注入多种清理故障并返回执行轨迹。
def failing_cleanup_io(monkeypatch, module):
    """Only substitute remote/process I/O; execute the real harness/report/CLI."""
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    trace = []
    class Session:
        # 提供事务上下文接口，保持数据库替身结构与真实清理流程一致。
        @asynccontextmanager
        async def begin(self):
            yield self
        # 返回空查询结果，避免替身清理读取真实数据库行。
        async def scalars(self, statement):
            return SimpleNamespace(all=lambda: [])
        # 记录删除操作，供清理轨迹断言使用。
        async def execute(self, statement):
            trace.append('mysql_delete')
    class Database:
        # 接受数据库 URL 并保持离线，供故障清理测试构造资源。
        def __init__(self, url): pass
        # 在打开清理会话时抛出连接故障，模拟 MySQL 清理失败。
        @asynccontextmanager
        async def session(self):
            trace.append('mysql_cleanup')
            raise ConnectionError('PRIVATE mysql operands')
            yield Session()
        # 记录释放并抛出独立故障，检验数据库关闭失败也会写入报告。
        async def dispose(self):
            trace.append('database_dispose')
            raise OSError('PRIVATE credentials')
    class Index:
        # 把索引自身作为客户端，保存集合与超时供真实验收流程访问。
        def __init__(self, uri, collection, timeout):
            self._client, self.collection, self.timeout = self, collection, timeout
        # 记录集合准备行为，使故障测试可确认验收初始化顺序。
        async def ensure_collection(self): trace.append('ensure_collection')
        # 返回固定集合元数据，避免真实 Milvus 查询。
        async def describe_collection(self, *args, **kwargs):
            return {'auto_id': False, 'consistency_level': 0, 'fields': []}
        # 报告测试集合存在，使清理进入删除集合分支。
        async def has_collection(self, *args, **kwargs): return True
        # 记录集合删除并注入超时，检验 Milvus 清理失败报告。
        async def drop_collection(self, *args, **kwargs):
            trace.append('milvus_drop')
            raise TimeoutError('PRIVATE endpoint')
        # 记录索引关闭并注入异常，检验清理异常不会阻止后续资源释放。
        async def aclose(self):
            trace.append('index_close')
            raise RuntimeError('PRIVATE client')
    class Embedder:
        # 接受嵌入设置而不创建外部客户端。
        def __init__(self, settings): pass
        # 返回固定维度的零向量，供真实验收编排离线运行。
        async def embed(self, texts): return [[0.0] * 1024]
        # 记录嵌入资源关闭并抛错，检验它作为独立清理错误被保留。
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


# 验证验收主流程或清理失败时 CLI 仍写完整失败报告，并尝试全部清理动作。
@pytest.mark.parametrize('primary_failure', [True, False])
def test_dense_cli_always_writes_failed_report_and_attempts_every_cleanup(monkeypatch, tmp_path, capsys, primary_failure):
    import json
    from types import SimpleNamespace
    module = implementation()
    trace = failing_cleanup_io(monkeypatch, module)
    # 按场景返回知识编号或注入文档导入故障，区分主流程与清理失败。
    async def import_document(*args):
        if primary_failure:
            raise ValueError('PRIVATE document')
        return [7]
    class Repository:
        # 接受数据库依赖，构造离线知识仓储替身。
        def __init__(self, database): pass
        # 返回预期知识编号与章节，用于检索标准答案映射。
        async def get_done(self, ids): return [SimpleNamespace(id=7, section_path='政策/配送')]
    class Worker:
        # 接受向量化依赖而不执行外部初始化。
        def __init__(self, *args): pass
        # 报告已向量化一条，允许验收流程进入检索和应用检查。
        async def run(self): return 1
    # 返回应用验收成功结果，使测试单独观察清理故障对整体通过状态的影响。
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


# 验证进程检查点失败后，即使进程、数据库和索引清理继续失败，报告仍保留主错误。
def test_recovery_cli_preserves_primary_failure_through_process_mysql_milvus_and_close_failures(monkeypatch, tmp_path, capsys):
    import json
    from types import SimpleNamespace
    module = implementation('knowledge_recovery')
    trace = failing_cleanup_io(monkeypatch, module)
    monkeypatch.setattr(module, 'spawn_owned', lambda *args: SimpleNamespace(pid=54321))
    # 注入检查点读取故障，作为需要保留的原始恢复失败。
    async def failed_checkpoint(*args): raise LookupError('PRIVATE process context')
    # 记录子进程回收并抛出清理故障，检验它不会覆盖检查点主错误。
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


# 验证创建会话超时后 HTTP 客户端退出再失败，报告保留路由超时并另记清理错误。
async def test_app_keeps_route_timeout_when_http_client_exit_also_fails(monkeypatch):
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    from tests.fakes import fake_settings
    module = implementation()
    # 提供空应用生命周期，隔离真实资源启动与关闭。
    @asynccontextmanager
    async def lifespan(app): yield
    class Client:
        # 接受 HTTP 客户端参数而不连接外部服务。
        def __init__(self, **kwargs): pass
        # 返回客户端替身，让真实评测上下文正常进入。
        async def __aenter__(self): return self
        # 在客户端退出时抛错，模拟路由失败后的二次清理故障。
        async def __aexit__(self, *args): raise OSError('PRIVATE client credentials')
    # 返回创建会话超时结果，构造必须保留的主流程错误。
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


# 验证消息审计失败与客户端关闭失败同时发生时，主错误类型不被清理错误覆盖。
async def test_app_preserves_audit_failure_type_when_client_exit_also_fails(monkeypatch):
    from contextlib import asynccontextmanager
    from types import SimpleNamespace
    from tests.fakes import fake_settings
    module = implementation()
    # 提供空应用生命周期，聚焦审计与客户端清理故障。
    @asynccontextmanager
    async def lifespan(app): yield
    class Client:
        # 接受客户端构造参数，替换真实 HTTP 资源。
        def __init__(self, **kwargs): pass
        # 允许评测进入客户端上下文而不发起连接。
        async def __aenter__(self): return self
        # 注入客户端关闭故障，检验审计主错误仍被保留。
        async def __aexit__(self, *args): raise OSError('PRIVATE close operands')
    # 返回成功会话编号，使评测继续执行聊天与审计。
    async def create(*args): return {'conversation_id': '1', 'error_code': None}
    # 返回成功的合成聊天文本，使失败定位在审计读取阶段。
    async def stream(*args, **kwargs): return {'text': '合成正文', 'error_code': None}
    # 在读取审计消息时抛错，模拟需要保留类型的主流程故障。
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
