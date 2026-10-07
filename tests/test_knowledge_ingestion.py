from argparse import Namespace
from contextlib import asynccontextmanager

import pytest
from sqlalchemy import event, text


def importer():
    try:
        from app.knowledge.ingestion import import_document
    except ImportError:
        pytest.fail("pending document importer is missing")
    return import_document


def cli():
    try:
        from app.knowledge import cli as module
    except ImportError:
        pytest.fail("knowledge CLI is missing")
    return module


async def test_invalid_document_never_reaches_repository(tmp_path):
    class NoWrites:
        async def add_chunks(self, *args, **kwargs):
            pytest.fail("invalid document reached storage")
    path = tmp_path / "invalid.md"
    path.write_text("# 正常\n合法。\n# " + "长" * 600 + "\n非法。", encoding="utf-8")
    with pytest.raises(ValueError):
        await importer()(path, "manual", NoWrites())


async def test_read_error_never_reaches_repository(tmp_path):
    with pytest.raises(FileNotFoundError):
        await importer()(tmp_path / "absent.md", "policy", None)


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


async def test_import_pointer_write_failure_rolls_back_all_chunks(knowledge_rows, tmp_path):
    from app.repositories.knowledge import KnowledgeRepository
    path = tmp_path / (knowledge_rows.token + ".md")
    path.write_text("## 第一节\n第一答案。\n## 第二节\n第二答案。", encoding="utf-8")
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


@pytest.mark.parametrize("command", ["migrate", "import-document"])
@pytest.mark.parametrize("failure", [False, True])
async def test_cli_holds_shared_lock_and_disposes_on_success_or_failure(monkeypatch, tmp_path, command, failure):
    module = cli()
    state = {"locked": False, "disposed": False}
    class Database:
        def __init__(self, url):
            pass
        async def dispose(self):
            state["disposed"] = True
    @asynccontextmanager
    async def lock(database):
        state["locked"] = True
        try:
            yield
        finally:
            state["locked"] = False
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


def test_cli_failure_has_nonzero_exit_and_redacts_exception(monkeypatch, capsys):
    module = cli()
    async def fail(args):
        raise RuntimeError("secret credential must not escape")
    monkeypatch.setattr(module, "run", fail)
    assert module.main(["migrate"]) == 1
    assert "secret credential" not in capsys.readouterr().err


def test_cli_chunk_error_identifies_document_and_section(monkeypatch, capsys):
    from app.knowledge.chunking import chunk_markdown
    module = cli()
    async def fail(args):
        chunk_markdown("# 超长\n" + "汉" * 22000 + "。", document_name="demo", content_type="policy")
    monkeypatch.setattr(module, "run", fail)
    assert module.main(["migrate"]) == 1
    error = capsys.readouterr().err
    assert "demo" in error and "章节 '超长'" in error


def test_cli_rejects_invalid_type_before_database_access():
    with pytest.raises(SystemExit) as error:
        cli().parser().parse_args(["import-document", "--path", "demo.md", "--type", "other"])
    assert error.value.code == 2
