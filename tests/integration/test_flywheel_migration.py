from sqlalchemy import text
import pytest


async def test_ch09_extension_is_exactly_verified(flywheel_base):
    from pathlib import Path
    spec = Path('docs/superpowers/specs/2026-10-19-observability-flywheel-design.md').read_text(encoding='utf-8')
    original = spec.split('```sql')[-1].split('```')[0].strip()
    assert Path('sql/ch09-ddl.sql').read_text(encoding='utf-8').strip() == original
    from app.flywheel.migration import migrate_flywheel, verify_flywheel
    from app.quality.migration import verify_quality
    async with flywheel_base.session() as session, session.begin():
        await session.execute(text("INSERT INTO low_confidence_questions(raw_question,source) VALUES('旧问题必须保留','self_check')"))
    await migrate_flywheel(flywheel_base)
    await migrate_flywheel(flywheel_base)
    await verify_flywheel(flywheel_base)
    await verify_quality(flywheel_base)
    async with flywheel_base.session() as session:
        assert await session.scalar(text('SELECT raw_question FROM low_confidence_questions')) == '旧问题必须保留'
        assert await session.scalar(text('SELECT processing FROM low_confidence_questions')) is None
        tables = set((await session.scalars(text("SELECT TABLE_NAME FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE()"))).all())
        assert {'review_queue', 'eval_runs'} <= tables


@pytest.mark.parametrize('alter', [
    'ALTER TABLE low_confidence_questions ADD stray TEXT NULL',
    'ALTER TABLE low_confidence_questions ADD INDEX unexpected_idx(reason(10))',
    'ALTER TABLE low_confidence_questions DROP FOREIGN KEY fk_lcq_review',
    "ALTER TABLE review_queue MODIFY review_status ENUM('待审','通过','错误') NOT NULL DEFAULT '待审' COMMENT '人工审核状态'",
    'ALTER TABLE eval_runs DROP INDEX uk_eval_run_key',
])
async def test_unknown_or_corrupt_flywheel_schema_is_refused(flywheel_base, alter):
    from app.flywheel.migration import migrate_flywheel, verify_flywheel
    await migrate_flywheel(flywheel_base)
    async with flywheel_base.engine.begin() as connection:
        await connection.exec_driver_sql(alter)
    with pytest.raises(RuntimeError, match='schema'):
        await verify_flywheel(flywheel_base)
    with pytest.raises(RuntimeError, match='schema'):
        await migrate_flywheel(flywheel_base)


async def test_quality_verifier_does_not_ignore_unknown_ch09_extensions(flywheel_base):
    from app.flywheel.migration import migrate_flywheel
    from app.quality.migration import verify_quality
    await migrate_flywheel(flywheel_base)
    async with flywheel_base.engine.begin() as connection:
        await connection.exec_driver_sql('ALTER TABLE low_confidence_questions ADD stray TEXT NULL')
    with pytest.raises(RuntimeError, match='schema'):
        await verify_quality(flywheel_base)


async def test_base_ch09_can_be_completed_but_partial_tables_are_refused(flywheel_base):
    from pathlib import Path
    from app.flywheel.migration import migrate_flywheel
    from app.quality.migration import _statements
    async with flywheel_base.engine.begin() as connection:
        for statement in _statements(Path('sql/ch09-ddl.sql').read_text(encoding='utf-8')):
            await connection.exec_driver_sql(statement)
    await migrate_flywheel(flywheel_base)
    async with flywheel_base.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM information_schema.COLUMNS WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='eval_runs' AND COLUMN_NAME='run_key'")) == 1


async def test_partial_tables_never_get_automatically_recreated(flywheel_base):
    from app.flywheel.migration import migrate_flywheel
    await migrate_flywheel(flywheel_base)
    async with flywheel_base.engine.begin() as connection:
        await connection.exec_driver_sql('DROP TABLE eval_runs')
    with pytest.raises(RuntimeError, match='partial'):
        await migrate_flywheel(flywheel_base)
    async with flywheel_base.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM information_schema.TABLES WHERE TABLE_SCHEMA=DATABASE() AND TABLE_NAME='eval_runs'")) == 0
