from datetime import datetime, timezone
from contextlib import asynccontextmanager

import pytest

from app.knowledge import cli


# 验证挖掘命令将 ISO 日期解析为窗口边界，并采用默认批次数量。
def test_mining_arguments_parse_iso_windows_and_default_batch():
    args = cli.parser().parse_args(['mine-conversations', '--start', '2026-10-06', '--end', '2026-10-07'])
    assert args.start == datetime(2026, 10, 6) and args.end == datetime(2026, 10, 7)
    assert args.batch_size == 20


# 验证每日任务在 UTC 跨日时仍选择前一个北京时间自然日。
def test_daily_uses_previous_beijing_day_including_utc_boundary():
    assert hasattr(cli, 'previous_day'), 'Beijing daily window is missing'
    assert cli.previous_day(datetime(2026, 10, 6, 17, tzinfo=timezone.utc)) == (datetime(2026, 10, 6), datetime(2026, 10, 7))


# 验证暂存去重与每日任务命令均可被命令行解析器识别。
@pytest.mark.parametrize('command', ['deduplicate-staging', 'run-daily'])
def test_new_entry_commands_are_available(command):
    assert cli.parser().parse_args([command]).command == command


# 验证任务失败返回非零退出码，且错误输出不泄露上游细节。
def test_job_failure_is_nonzero_and_hides_upstream_details(monkeypatch, capsys):
    # 抛出带敏感内容的任务故障，用于检验命令行错误脱敏。
    async def fail(args):
        raise RuntimeError('SECRET synthetic data')
    monkeypatch.setattr(cli, 'run', fail)
    assert cli.main(['run-daily']) == 1
    assert 'SECRET' not in capsys.readouterr().err


# 验证真实 CLI 的预算或模型失败报告安全窗口、批次和来源标识，同时隐藏正文及凭据。
@pytest.mark.parametrize('failure', ['oversized', 'provider'])
def test_actual_cli_failed_batch_has_safe_window_and_source_identity(monkeypatch, capsys, failure):
    from tests.fakes import fake_settings
    from tests.test_knowledge_extraction import Model
    from tests.test_knowledge_mining import Repository
    from app.knowledge.types import ConversationTranscript
    from app.repositories.records import MessageRecord
    class Database:
        # 提供无连接的数据库替身，隔离 CLI 故障报告测试的外部依赖。
        def __init__(self, url): pass
        # 满足数据库清理接口，使测试聚焦批次失败报告。
        async def dispose(self): pass
    # 提供无需数据库的任务锁上下文，让真实命令行流程离线执行。
    @asynccontextmanager
    async def lock(database): yield
    class History:
        # 接受数据库参数而不执行查询，供会话历史替身注入。
        def __init__(self, db): pass
        # 返回带固定会话及消息编号的敏感正文，用于核对安全来源标识。
        async def completed(self, *args):
            return [ConversationTranscript(4321, 9876, [
                MessageRecord(9876, 'user', 'PRIVATE synthetic body SECRET', None, None)])]
    class SyncClient:
        # 提供同步模型客户端关闭接口，避免故障报告测试访问真实资源。
        def close(self): pass
    class AsyncClient:
        # 提供异步模型客户端关闭接口，配合真实 CLI 清理流程。
        async def close(self): pass
    model = Model(fault=RuntimeError('PRIVATE provider operands SECRET'))
    model.root_client, model.root_async_client = SyncClient(), AsyncClient()
    monkeypatch.setattr(cli, 'load_settings', lambda: fake_settings(mysql_password='fake-only',
        input_token_budget=1 if failure == 'oversized' else 10000))
    for name, value in [('Database', Database), ('job_lock', lock), ('KnowledgeHistory', History),
        ('KnowledgeRepository', lambda db: Repository()), ('create_model', lambda settings: model)]:
        monkeypatch.setattr(cli, name, value)
    assert cli.main(['mine-conversations', '--start', '2026-10-06', '--end', '2026-10-07']) == 1
    captured = capsys.readouterr()
    assert 'batch_no=a19c1306f00a3e5398f9bbd2a49fae7c27bf261cf1134f1adb758f069da22284' in captured.err
    assert 'conversation:4321:message:9876' in captured.err
    assert '2026-10-06T00:00:00' in captured.err and '2026-10-07T00:00:00' in captured.err
    assert ('InputTooLong' if failure == 'oversized' else 'ServiceError') in captured.err
    assert not any(word in captured.out + captured.err for word in ['PRIVATE', 'SECRET', 'synthetic body', 'provider operands'])


# 验证每日任务从抽取到向量化只持一把锁，各故障阶段仍清理所有已创建资源。
@pytest.mark.parametrize('failure', [None, 'extract', 'vector', 'model_close'])
async def test_daily_holds_one_lock_and_closes_owned_resources(monkeypatch, failure, capsys):
    from tests.fakes import fake_settings
    from tests.test_knowledge_extraction import Model, conversation
    from tests.test_knowledge_mining import Repository
    events = []
    class Database:
        # 提供数据库构造替身，让测试只记录锁与资源的生命周期。
        def __init__(self, url): pass
        # 记录数据库释放，验证它发生在任务锁释放之后。
        async def dispose(self): events.append('database_closed')
    # 记录单次加锁和最终释放，检查整个每日作业共享同一锁。
    @asynccontextmanager
    async def lock(database):
        assert 'lock_acquired' not in events
        events.append('lock_acquired')
        try:
            yield
        finally:
            events.append('lock_released')
    class History:
        # 接受数据库依赖，准备离线历史分页接口。
        def __init__(self, db): pass
        # 仅第一页返回会话，并检查抽取期间锁尚未释放及窗口合法。
        async def completed(self, start, end, after_id=0, limit=20):
            assert start < end
            assert 'lock_released' not in events
            return [conversation()] if after_id == 0 else []
    class Client:
        # 记录同步模型客户端关闭次数与顺序。
        def close(self): events.append('sync_model_closed')
    class AsyncClient:
        # 记录异步模型关闭，并可注入关闭故障以验证后续清理仍执行。
        async def close(self):
            events.append('async_model_closed')
            if failure == 'model_close': raise RuntimeError('controlled close')
    class Index:
        # 接受 Milvus 索引配置而不连接服务。
        def __init__(self, *a, **kw): pass
        # 记录索引已准备，供向量化阶段的顺序断言使用。
        async def ensure_collection(self): events.append('index_ready')
        # 记录索引关闭，核对作业失败时的资源清理。
        async def aclose(self): events.append('index_closed')
    class Embedder:
        # 接受嵌入配置而不创建云请求。
        def __init__(self, settings): pass
        # 记录嵌入客户端关闭，核对它与索引均被释放。
        async def aclose(self): events.append('embedder_closed')
    class Vectorizer:
        # 接受真实作业编排注入的依赖，替换外部向量化工作。
        def __init__(self, *a): pass
        # 确认向量化时仍持锁，按场景返回零处理数或注入向量化故障。
        async def run(self, batch):
            assert 'lock_released' not in events
            if failure == 'vector': raise RuntimeError('controlled vector')
            events.append('vectorized')
            return 0
    model = Model(fault=RuntimeError('controlled extraction') if failure == 'extract' else None)
    model.root_client, model.root_async_client = Client(), AsyncClient()
    online_settings = fake_settings(mysql_password='fake-only', input_token_budget=10000, max_output_tokens=512)
    monkeypatch.setattr(cli, 'load_settings', lambda: online_settings)
    monkeypatch.setattr(cli, 'previous_day', lambda: (datetime(2026, 10, 6), datetime(2026, 10, 7)))
    # 核对离线抽取提高输出预算但沿用上游配置，并返回预设模型。
    def model_factory(settings):
        assert settings.max_output_tokens == 2048
        assert settings.llm_model == online_settings.llm_model
        assert settings.llm_base_url == online_settings.llm_base_url
        assert settings.llm_api_key == online_settings.llm_api_key
        return model
    for name, value in [('Database', Database), ('job_lock', lock), ('KnowledgeHistory', History), ('KnowledgeRepository', lambda db: Repository()), ('create_model', model_factory), ('MilvusIndex', Index), ('SiliconFlowEmbedder', Embedder), ('PendingVectorizer', Vectorizer)]:
        monkeypatch.setattr(cli, name, value)
    if failure:
        with pytest.raises(Exception):
            await cli.run(cli.parser().parse_args(['run-daily']))
    else:
        await cli.run(cli.parser().parse_args(['run-daily']))
        assert 'vectorized' in events
        output = capsys.readouterr().out
        assert '2026-10-06' in output and '2026-10-07' in output
    assert events[-2:] == ['lock_released', 'database_closed']
    assert online_settings.max_output_tokens == 512
    assert events.count('lock_acquired') == 1
    assert events.count('async_model_closed') == events.count('sync_model_closed') == 1
    if failure != 'extract':
        assert events.count('embedder_closed') == events.count('index_closed') == 1


# 验证真实 PowerShell 启动器固定项目目录与 uv 参数，并保留子进程退出码。
def test_powershell_launcher_fixes_directory_and_preserves_child_exit_code():
    import json
    from pathlib import Path
    import shutil
    import subprocess
    shell = shutil.which('pwsh') or shutil.which('powershell')
    if shell is None:
        pytest.skip('PowerShell launcher requires a Windows shell')
    script = Path(__file__).resolve().parents[1] / 'scripts/run-knowledge-daily.ps1'
    # Shadow only the external uv boundary; execute the actual launcher.
    code = "function uv { @{cwd=(Get-Location).Path; argv=$args} | ConvertTo-Json -Compress; $global:LASTEXITCODE=23 }; & '" + str(script).replace("'", "''") + "'; exit $LASTEXITCODE"
    result = subprocess.run([shell, '-NoProfile', '-Command', code], capture_output=True, text=True)
    assert result.returncode == 23
    invocation = json.loads(result.stdout)
    assert invocation['cwd'] == 'D:\\shixi\\ecommerce-customer-service'
    assert invocation['argv'] == ['--directory', 'D:\\shixi\\ecommerce-customer-service', 'run', 'python', '-m', 'app.knowledge.cli', 'run-daily']


# 验证启动器将原生子进程的标准输出与错误写入忽略日志，同时保留失败退出码。
def test_actual_launcher_captures_native_stdout_stderr_in_ignored_log_and_retains_exit():
    from pathlib import Path
    import shutil
    import subprocess
    import sys
    from uuid import uuid4
    shell = shutil.which('pwsh') or shutil.which('powershell')
    if shell is None: pytest.skip('PowerShell launcher requires a Windows shell')
    script = Path(__file__).resolve().parents[1] / 'scripts/run-knowledge-daily.ps1'
    token = 'synthetic_' + uuid4().hex
    child = f"import sys; print('{token} batch_no=abc conversation:4321:message:9876'); sys.stderr.write('{token} InputTooLong\\n'); sys.exit(23)"
    code = ("function uv { & '" + sys.executable.replace("'", "''") + "' -c '" + child.replace("'", "''") +
        "'; $global:LASTEXITCODE=$LASTEXITCODE }; & '" + str(script).replace("'", "''") + "'; exit $LASTEXITCODE")
    result = subprocess.run([shell, '-NoProfile', '-Command', code], capture_output=True, text=True)
    assert result.returncode == 23
    log = Path('D:/shixi/ecommerce-customer-service/.cache/knowledge-daily.log')
    assert log.exists()
    # Tee-Object uses UTF-16LE on Windows PowerShell 5.1 and UTF-8 on pwsh.
    data = log.read_bytes()
    captured = data.decode('utf-16') if data.startswith(b'\xff\xfe') else data.decode('utf-8-sig')
    assert f'{token} batch_no=abc conversation:4321:message:9876' in captured
    assert f'{token} InputTooLong' in captured
