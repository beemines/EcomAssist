import json
from contextlib import asynccontextmanager
from uuid import uuid4
import pytest
from sqlalchemy import text
from langchain_core.messages import AIMessage
from app.core.errors import ServiceError
from app.repositories.conversations import ConversationRepository
from app.workflow.persistence import open_checkpointer, checkpoint_config


def snapshot(answer='旧知识原文', score=.91):
    return {'status': 'captured', 'payload': {'schema_version': 1, 'strategy': 'hybrid_rerank',
        'retrieved_at': '2026-10-19T08:00:00Z', 'versions': {}, 'reason': None, 'chunks': [
        {'chunk_id': '9007199254740993', 'question': '运费标准', 'answer': answer,
         'section_path': '运费', 'score': score, 'score_kind': 'rerank', 'rank': 1, 'in_prompt': True}]}}


async def seed(database):
    async with database.session() as session, session.begin():
        await session.execute(text("UPDATE conversations SET user_id='demo-user' WHERE id=1"))
        await session.execute(text("INSERT INTO conversations(id,user_id) VALUES(2,'another-user')"))
        await session.execute(text("INSERT INTO messages(id,conversation_id,role,content) VALUES "
            "(10,1,'user','运费怎么算'),(20,1,'assistant','旧答'),"
            "(30,1,'user','运费怎么算'),(40,1,'assistant','新答')"))


async def root(saver, *, assistant='20', user='10', answer='旧答', **changes):
    from langgraph.checkpoint.base import empty_checkpoint
    cp = empty_checkpoint()
    cp['id'] = str(uuid4())
    cp['channel_values'] = {'conversation_id': '1', 'turn_status': 'completed',
        'user_message_id': user, 'raw_question': '运费怎么算', 'final_message_id': assistant,
        'final_answer': answer, 'tool_trace': [], 'retrieval_performed': True,
        'retrieval_snapshot': snapshot(), 'evidence_payload': {}}
    cp['channel_values'].update(changes)
    config = await saver.aput(checkpoint_config('1'), cp, {'source': 'loop', 'step': 1, 'parents': {}}, {})
    return config['configurable']['checkpoint_id']


@asynccontextmanager
async def service(database, tmp_path):
    from app.flywheel.feedback import FeedbackService
    from app.flywheel.repository import FlywheelRepository
    async with open_checkpointer(tmp_path / 'feedback.sqlite') as saver:
        yield FeedbackService(saver, ConversationRepository(database), FlywheelRepository(database)), saver


async def test_feedback_reads_original_turn(flywheel_database, tmp_path):
    await seed(flywheel_database)
    async with service(flywheel_database, tmp_path) as (feedback, saver):
        old = await root(saver)
        await root(saver, assistant='40', user='30', answer='新答', retrieval_snapshot=snapshot('新证据', .98))
        first = await feedback.submit('1', user_id='demo-user', assistant_message_id='20', checkpoint_id=old)
        again = await feedback.submit('1', user_id='demo-user', assistant_message_id='20')
        assert first.created and not again.created and first.id == again.id
        async with flywheel_database.session() as session:
            rows = (await session.execute(text('SELECT raw_question,user_message_id,assistant_message_id,'
                'retrieved_chunks,source FROM low_confidence_questions'))).mappings().all()
        assert len(rows) == 1 and rows[0]['raw_question'] == '运费怎么算'
        assert (rows[0]['user_message_id'], rows[0]['assistant_message_id'], rows[0]['source']) == (10, 20, 'user_feedback')
        saved = json.loads(rows[0]['retrieved_chunks'])
        assert saved['chunks'][0]['answer'] == '旧知识原文' and saved['chunks'][0]['score'] == .91


@pytest.mark.parametrize('changes,status', [
    ({'retrieval_performed': False, 'retrieval_snapshot': None}, 'not_retrieved'),
    ({'retrieval_performed': True, 'retrieval_snapshot': None, 'evidence_payload': {
        'matches': [], 'retrieval': {'strategy': 'hybrid_rerank'}}}, 'captured'),
    ({'retrieval_performed': True, 'retrieval_snapshot': None}, 'unavailable'),
])
async def test_feedback_stores_distinct_retrieval_states(flywheel_database, tmp_path, changes, status):
    await seed(flywheel_database)
    async with service(flywheel_database, tmp_path) as (feedback, saver):
        await root(saver, **changes)
        await feedback.submit('1', user_id='demo-user', assistant_message_id='20')
    async with flywheel_database.session() as session:
        row = (await session.execute(text('SELECT snapshot_status,retrieved_chunks FROM low_confidence_questions'))).one()
    assert row.snapshot_status == status
    assert (row.retrieved_chunks is None) == (status == 'not_retrieved')
    if status != 'not_retrieved':
        assert json.loads(row.retrieved_chunks)['chunks'] == []


async def test_main_routes_and_history_bind_feedback_to_original_sql_id(flywheel_database, tmp_path):
    from types import SimpleNamespace
    import httpx
    from app.main import create_app
    from app.flywheel.repository import FlywheelRepository
    from tests.fakes import fake_settings, StreamingModel, FAQStub
    await seed(flywheel_database)
    async with open_checkpointer(tmp_path / 'http-feedback.sqlite') as saver:
        identifier = await root(saver)
        app = create_app(fake_settings(), model=StreamingModel(), repository=ConversationRepository(flywheel_database),
            faq_repository=FAQStub(), chat_service=SimpleNamespace(), checkpointer=saver,
            flywheel_repository=FlywheelRepository(flywheel_database))
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://127.0.0.1:8006') as client:
            page = (await client.get('/api/conversations/1/messages')).json()
            assert page['turn_metadata']['20']['feedback'] == {
                'assistant_message_id': '20', 'checkpoint_id': identifier}
            response = await client.post('/api/conversations/1/feedback', json=page['turn_metadata']['20']['feedback'])
            assert response.status_code == 200 and response.json()['created']


@pytest.mark.parametrize('damage,code', [('missing', 409), ('checkpoint', 409), ('owner', 404),
    ('unfinished', 409), ('question', 409), ('body', 409), ('intervening_user', 409), ('assistant', 409)])
async def test_feedback_rejects_unverifiable_original_turn(flywheel_database, tmp_path, damage, code):
    await seed(flywheel_database)
    async with service(flywheel_database, tmp_path) as (feedback, saver):
        changes = {'turn_status': 'running'} if damage == 'unfinished' else {'raw_question': '伪造原话'} if damage == 'question' else {}
        checkpoint = None if damage == 'missing' else await root(saver, **changes)
        if damage in ('body', 'intervening_user'):
            async with flywheel_database.session() as session, session.begin():
                await session.execute(text("UPDATE messages SET content='不同正文' WHERE id=20") if damage == 'body'
                    else text("INSERT INTO messages(id,conversation_id,role,content) VALUES(15,1,'user','插入另一轮')"))
        with pytest.raises(ServiceError) as result:
            await feedback.submit('1', user_id='another-user' if damage == 'owner' else 'demo-user',
                assistant_message_id='40' if damage == 'assistant' else '20',
                checkpoint_id=str(uuid4()) if damage == 'checkpoint' else checkpoint)
        assert result.value.status_code == code
        async with flywheel_database.session() as session:
            assert await session.scalar(text('SELECT COUNT(*) FROM low_confidence_questions')) == 0


@pytest.mark.parametrize('source', ['retrieval_low_conf', 'self_check'])
async def test_refusal_snapshot_and_assistant_commit_atomically(flywheel_database, source):
    from app.quality.repository import QualityRepository
    from app.flywheel.types import RetrievalSnapshot
    await seed(flywheel_database)
    snap = RetrievalSnapshot.model_validate_json(json.dumps(snapshot()))
    repository = QualityRepository(flywheel_database)
    identifier = await repository.commit_refusal('1', AIMessage('证据不足'), raw_question='运费怎么算',
        source=source, reason='缺少政策', user_message_id='30', snapshot=snap)
    async with flywheel_database.session() as session:
        row = (await session.execute(text('SELECT assistant_message_id,user_message_id,processing,snapshot_status '
            'FROM low_confidence_questions'))).one()
        assert row.assistant_message_id == identifier and row.user_message_id == 30
        assert row.snapshot_status == 'captured' and json.loads(row.processing)['status'] == 'pending'
    async with flywheel_database.engine.begin() as connection:
        await connection.exec_driver_sql("CREATE TRIGGER reject_feedback BEFORE INSERT ON low_confidence_questions "
            "FOR EACH ROW SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT='feedback-rollback-test'")
    with pytest.raises(Exception, match='feedback-rollback-test'):
        await repository.commit_refusal('1', AIMessage('不能留半条答复'), raw_question='运费怎么算',
            source=source, reason='缺少政策', user_message_id='30', snapshot=snap)
    async with flywheel_database.session() as session:
        assert await session.scalar(text("SELECT COUNT(*) FROM messages WHERE content='不能留半条答复'")) == 0
