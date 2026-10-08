from argparse import Namespace
from contextlib import asynccontextmanager

import pytest
from sqlalchemy import event, text


# 加载文档导入入口，缺失实现时以明确断言失败报告。
def importer():
    try:
        from app.knowledge.ingestion import import_document
    except ImportError:
        pytest.fail("pending document importer is missing")
    return import_document


# 加载知识命令行模块，供真实参数解析与资源清理测试使用。
def cli():
    try:
        from app.knowledge import cli as module
    except ImportError:
        pytest.fail("knowledge CLI is missing")
    return module


# 验证文档任一章节非法时整份导入在仓储写入前失败。
async def test_invalid_document_never_reaches_repository(tmp_path):
    class NoWrites:
        # 若非法文档仍提交分块便令测试失败，证明整体预校验有效。
        async def add_chunks(self, *args, **kwargs):
            pytest.fail("invalid document reached storage")
    path = tmp_path / "invalid.md"
    path.write_text("# 正常\n合法。\n# " + "长" * 600 + "\n非法。", encoding="utf-8")
    with pytest.raises(ValueError):
        await importer()(path, "manual", NoWrites())


# 验证前一组 FAQ 空答案不会因后续合法答案被忽略，整份文档必须先拒绝。
async def test_empty_earlier_faq_answer_rejects_document_before_storage(tmp_path):
    class NoWrites:
        # 阻止不完整 FAQ 写入仓储，确认解析错误先于持久化。
        async def add_chunks(self, *args, **kwargs):
            pytest.fail("incomplete FAQ document reached storage")
    path = tmp_path / "invalid-faq.md"
    path.write_text("# 配送\nQ: supplied first question?\nA:\nQ: supplied second question?\nA: valid answer.", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid-faq.*章节.*配送"):
        await importer()(path, "faq", NoWrites())


# 验证文件不存在时传播读取错误，且无需任何仓储操作。
async def test_read_error_never_reaches_repository(tmp_path):
    with pytest.raises(FileNotFoundError):
        await importer()(tmp_path / "absent.md", "policy", None)


# 验证每次导入提交待向量化分块，邻接指针仅连接本次文档内的条目。
async def test_import_commits_pending_neighbors_isolated_per_document(knowledge_rows, tmp_path):
    from app.repositories.knowledge import KnowledgeRepository
    path = tmp_path / (knowledge_rows.token + ".md")
    path.write_text("## 第一节\n第一答案。\n## 第二节\n第二答案。", encoding="utf-8")
    repo = KnowledgeRepository(knowledge_rows.database)
    first = await importer()(path, "policy", repo)
    second = await importer()(path, "manual", repo)
    async with knowledge_rows.database.session() as session:
        rows = (await session.execute(text("SELECT id,prev_chunk_id,next_chunk_id,vectorize_status,vector_id,content_type,answer FROM knowledge_chunks WHERE category=:token ORDER BY id"), {"token": knowledge_rows.token})).all()
    assert [tuple(r) for r in rows] == [
        (first[0], None, first[1], "pending", None, "policy", "第一答案。"),
        (first[1], first[0], None, "pending", None, "policy", "第二答案。"),
        (second[0], None, second[1], "pending", None, "manual", "第一答案。"),
        (second[1], second[0], None, "pending", None, "manual", "第二答案。")]


# 验证邻接指针更新失败会回滚整份文档的所有新增分块。
async def test_import_pointer_write_failure_rolls_back_all_chunks(knowledge_rows, tmp_path):
    from app.repositories.knowledge import KnowledgeRepository
    path = tmp_path / (knowledge_rows.token + ".md")
    path.write_text("## 第一节\n第一答案。\n## 第二节\n第二答案。", encoding="utf-8")
    # 在知识分块更新语句前抛错，模拟新增记录后建立邻接关系失败。
    def fail_pointers(conn, cursor, statement, parameters, context, executemany):
        if statement.lstrip().upper().startswith("UPDATE KNOWLEDGE_CHUNKS"):
            raise RuntimeError("injected pointer failure")
    engine = knowledge_rows.database.engine.sync_engine
    event.listen(engine, "before_cursor_execute", fail_pointers)
    try:
        with pytest.raises(RuntimeError, match="injected pointer"):
            await importer()(path, "policy", KnowledgeRepository(knowledge_rows.database))
    finally:
        event.remove(engine, "before_cursor_execute", fail_pointers)
    async with knowledge_rows.database.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM knowledge_chunks WHERE category=:token"), {"token": knowledge_rows.token}) == 0


# 验证迁移与文档导入在共享任务锁内执行，成功或异常都释放锁及数据库。
@pytest.mark.parametrize("command", ["migrate", "import-document"])
@pytest.mark.parametrize("failure", [False, True])
async def test_cli_holds_shared_lock_and_disposes_on_success_or_failure(monkeypatch, tmp_path, command, failure):
    module = cli()
    state = {"locked": False, "disposed": False}
    class Database:
        # 接受数据库参数而不建连接，隔离命令行资源生命周期测试。
        def __init__(self, url):
            pass
        # 记录数据库释放状态，核对命令结束后的兜底清理。
        async def dispose(self):
            state["disposed"] = True
    # 标记共享锁的进入与退出，使操作替身能够检查写入锁边界。
    @asynccontextmanager
    async def lock(database):
        state["locked"] = True
        try:
            yield
        finally:
            state["locked"] = False
    # 断言变更发生于锁内，并可注入故障检验异常清理。
    async def operation(*args):
        assert state["locked"], "mutation happened outside shared job lock"
        if failure:
            raise RuntimeError("synthetic failure")
        return [123]
    monkeypatch.setattr(module, "Database", Database)
    monkeypatch.setattr(module, "load_settings", lambda: Namespace(database_url="synthetic"))
    monkeypatch.setattr(module, "job_lock", lock)
    monkeypatch.setattr(module, "migrate", operation)
    monkeypatch.setattr(module, "import_document", operation)
    args = module.parser().parse_args([command] if command == "migrate" else [command, "--path", str(tmp_path / "demo.md"), "--type", "policy"])
    if failure:
        with pytest.raises(RuntimeError):
            await module.run(args)
    else:
        await module.run(args)
    assert state == {"locked": False, "disposed": True}


# 验证 CLI 故障返回非零退出码且隐藏异常中的凭据信息。
def test_cli_failure_has_nonzero_exit_and_redacts_exception(monkeypatch, capsys):
    module = cli()
    # 抛出含私密凭据文本的作业故障，核对命令行错误脱敏。
    async def fail(args):
        raise RuntimeError("secret credential must not escape")
    monkeypatch.setattr(module, "run", fail)
    assert module.main(["migrate"]) == 1
    assert "secret credential" not in capsys.readouterr().err


# 验证分块容量错误在 CLI 中保留安全的文档与章节定位信息。
def test_cli_chunk_error_identifies_document_and_section(monkeypatch, capsys):
    from app.knowledge.chunking import chunk_markdown
    module = cli()
    # 通过真实分块器触发超长正文错误，生成带文档章节上下文的失败。
    async def fail(args):
        chunk_markdown("# 超长\n" + "汉" * 22000 + "。", document_name="demo", content_type="policy")
    monkeypatch.setattr(module, "run", fail)
    assert module.main(["migrate"]) == 1
    error = capsys.readouterr().err
    assert "demo" in error and "章节 '超长'" in error


# 验证命令参数中的非法文档类型在数据库访问前被解析器拒绝。
def test_cli_rejects_invalid_type_before_database_access():
    with pytest.raises(SystemExit) as error:
        cli().parser().parse_args(["import-document", "--path", "demo.md", "--type", "other"])
    assert error.value.code == 2
