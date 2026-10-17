"""Owned, read-only history: real SQL queries and durable SQLite roots."""
from contextlib import asynccontextmanager
from types import SimpleNamespace
from uuid import uuid4

import httpx
import pytest
import pytest_asyncio
from langgraph.types import Send
from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.main import create_app
from app.repositories.conversations import ConversationRepository
from app.workflow.persistence import checkpoint_config, open_checkpointer
from tests.fakes import FAQStub, StreamingModel, fake_settings


@pytest_asyncio.fixture
async def history_database(tmp_path):
    engine = create_async_engine('sqlite+aiosqlite:///' + str(tmp_path / 'history.sqlite'))
    async with engine.begin() as conn:
        await conn.execute(text('CREATE TABLE conversations (id INTEGER PRIMARY KEY, user_id TEXT, status TEXT DEFAULT "进行中", summary TEXT, summary_upto_msg_id INTEGER, layer1_from_msg_id INTEGER, created_at DATETIME DEFAULT CURRENT_TIMESTAMP, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)'))
        await conn.execute(text('CREATE TABLE messages (id INTEGER PRIMARY KEY, conversation_id INTEGER, role TEXT, content TEXT, tool_calls JSON, tool_call_id TEXT, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)'))
        await conn.execute(text("INSERT INTO conversations (id,user_id) VALUES (1,'demo-user'),(2,'someone-else')"))
    try:
        yield SimpleNamespace(engine=engine, session=async_sessionmaker(engine, expire_on_commit=False))
    finally:
        await engine.dispose()


@asynccontextmanager
async def history_client(database, tmp_path):
    model, faq = StreamingModel(), FAQStub()
    async with open_checkpointer(tmp_path / 'roots.sqlite') as saver:
        app = create_app(fake_settings(), model=model, repository=ConversationRepository(database),
                         faq_repository=faq, chat_service=SimpleNamespace(), checkpointer=saver)
        # If a GET enters business/context execution this object fails immediately.
        app.state.context_coordinator = object()
        async with httpx.AsyncClient(transport=httpx.ASGITransport(app), base_url='http://test') as client:
            yield app, client, saver, model, faq


async def seed_messages(database, count=405):
    async with database.engine.begin() as conn:
        await conn.execute(text('INSERT INTO messages (id,conversation_id,role,content) VALUES (:id,1,:role,:content)'),
                           [{'id': i, 'role': 'user' if i % 2 else 'assistant', 'content': f'原文{i}🙂'} for i in range(1, count + 1)])


async def put_root(saver, *, final_id='2', answer='旧答[1]', chunk='old-chunk', **changes):
    from langgraph.checkpoint.base import empty_checkpoint
    checkpoint = empty_checkpoint()
    checkpoint['id'] = str(uuid4())
    checkpoint['channel_values'] = {'state_version': 2, 'conversation_id': '1', 'turn_status': 'completed',
        'user_message_id': '1', 'final_message_id': final_id, 'final_answer': answer,
        'citations': [{'n': 1, 'chunk_id': chunk, 'section_path': '原政策', 'question': '原问题', 'answer': '原证据'}],
        'suggested_actions': ['create_ticket'], 'refund_offer': None, 'tool_trace': []}
    checkpoint['channel_values'].update(changes)
    config = await saver.aput(checkpoint_config('1'), checkpoint, {'source': 'loop', 'step': 1, 'parents': {}}, {})
    return config['configurable']['checkpoint_id']


async def test_message_pages_freeze_bound_and_keep_every_original(history_database, tmp_path):
    await seed_messages(history_database)
    async with history_client(history_database, tmp_path) as (_, client, _, model, faq):
        first = await client.get('/api/conversations/1/messages')
        assert first.status_code == 200
        page = first.json()
        assert len(page['messages']) == 200 and page['upto_id'] == '405'
        assert page['next_after_id'] == '200'
        async with history_database.engine.begin() as conn:
            await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (500,1,'user','新到消息')"))
        ids = [row['id'] for row in page['messages']]
        while page['next_after_id']:
            page = (await client.get('/api/conversations/1/messages', params={
                'after_id': page['next_after_id'], 'upto_id': page['upto_id']})).json()
            ids.extend(row['id'] for row in page['messages'])
        assert ids == [str(i) for i in range(1, 406)]
        assert page['messages'][-1]['content'] == '原文405🙂'
        assert model.requests == 0 and model.calls == [] and faq.keywords == []


async def test_list_pages_use_created_id_and_first_user_not_summary_update(history_database, tmp_path):
    async with history_database.engine.begin() as conn:
        await conn.execute(text("INSERT INTO conversations (id,user_id) VALUES (:id,'demo-user')"), [{'id': i} for i in range(3, 105)])
        await conn.execute(text("UPDATE conversations SET summary='后台刚完成',updated_at='2099-01-01' WHERE id=1"))
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (1,1,'assistant','开场'),(2,1,'user','第一问🙂'),(3,1,'user','第二问')"))
    async with history_client(history_database, tmp_path) as (_, client, _, _, _):
        page = (await client.get('/api/conversations')).json()
        assert len(page['items']) == 50
        assert page['items'][0]['id'] == '104' and page['items'][0]['first_question_preview'] == '新对话'
        ids = [row['id'] for row in page['items']]
        while page['next_before_id']:
            page = (await client.get('/api/conversations', params={'before_id': page['next_before_id']})).json()
            ids.extend(row['id'] for row in page['items'])
        assert ids == [str(i) for i in range(104, 2, -1)] + ['1']
        assert page['items'][-1]['first_question_preview'] == '第一问🙂'
        assert page['items'][-1]['has_summary'] is True


async def test_bigint_null_and_tool_fields_are_lossless(history_database, tmp_path):
    async with history_database.engine.begin() as conn:
        await conn.execute(text('INSERT INTO messages (id,conversation_id,role,content,tool_calls,tool_call_id) VALUES (9007199254740993,1,\'assistant\',NULL,:calls,NULL),(9007199254740994,1,\'tool\',\'原始结果\',NULL,\'call-1\')'),
            {'calls': '[{"id":"call-1","type":"function","function":{"name":"query_order","arguments":"{}"}}]'})
    async with history_client(history_database, tmp_path) as (_, client, _, _, _):
        response = await client.get('/api/conversations/1/messages')
        assert response.status_code == 200
        rows = response.json()['messages']
        assert rows[0]['id'] == '9007199254740993'
        assert rows[0]['content'] is None and rows[0]['tool_calls'][0]['function']['name'] == 'query_order'
        assert rows[1]['tool_call_id'] == 'call-1' and rows[1]['content'] == '原始结果'


async def test_original_roots_restore_distinct_citations_once_and_do_not_write(history_database, tmp_path):
    async with history_database.engine.begin() as conn:
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (1,1,'user','旧问'),(2,1,'assistant','旧答[1]'),(3,1,'user','新问'),(4,1,'assistant','新答[1]')"))
    async with history_client(history_database, tmp_path) as (_, client, saver, model, faq):
        old = await put_root(saver)
        new = await put_root(saver, final_id='4', answer='新答[1]', chunk='new-chunk', user_message_id='3')
        scans = []
        original = saver.alist
        async def counted(config, **kwargs):
            scans.append(config)
            async for root in original(config, **kwargs):
                yield root
        saver.alist = counted
        sql = []
        def capture(conn, cursor, statement, params, context, many):
            sql.append(statement.lstrip().upper())
        event.listen(history_database.engine.sync_engine, 'before_cursor_execute', capture)
        roots_before = list([root async for root in original(checkpoint_config('1'))])
        try:
            page = (await client.get('/api/conversations/1/messages')).json()
            await client.get('/api/conversations')
        finally:
            event.remove(history_database.engine.sync_engine, 'before_cursor_execute', capture)
        metadata = page['turn_metadata']
        assert metadata['2']['citations'][0]['chunk_id'] == 'old-chunk'
        assert metadata['4']['citations'][0]['chunk_id'] == 'new-chunk'
        assert metadata['2']['actions']['checkpoint_id'] == old
        assert metadata['4']['actions']['checkpoint_id'] == new
        assert metadata['2']['actions']['assistant_message_id'] == '2'
        assert len(scans) == 1
        assert len(sql) <= 5 and all(statement.startswith('SELECT') for statement in sql)
        assert [root async for root in original(checkpoint_config('1'))] == roots_before
        assert model.requests == 0 and model.calls == [] and faq.keywords == []


@pytest.mark.parametrize('mutation', [None, {'turn_status': 'running'}, {'conversation_id': '2'},
    {'final_message_id': '5'}, {'final_answer': '篡改正文'}, {'branch:to:agent': None},
    {'__pregel_tasks': [Send('agent', {})]}])
async def test_missing_invalid_or_nonterminal_root_never_fabricates_sources(history_database, tmp_path, mutation):
    async with history_database.engine.begin() as conn:
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (2,1,'assistant','旧答[1]')"))
    async with history_client(history_database, tmp_path) as (_, client, saver, model, faq):
        if mutation is not None:
            await put_root(saver, **mutation)
        page = (await client.get('/api/conversations/1/messages')).json()
        assert page['messages'][0]['content'] == '旧答[1]'
        assert page['turn_metadata'] == {}
        assert model.requests == 0 and faq.keywords == []


@pytest.mark.parametrize('path', ['/api/conversations/2/messages', '/api/conversations/999/messages',
    '/api/conversations/2/messages?user_id=someone-else'])
async def test_owner_is_server_scoped_and_unauthorized_is_404(history_database, tmp_path, path):
    async with history_client(history_database, tmp_path) as (_, client, _, _, _):
        assert (await client.get(path)).status_code == 404
        assert [row['id'] for row in (await client.get('/api/conversations?user_id=someone-else')).json()['items']] == ['1']


@pytest.mark.parametrize('query', ['limit=0', 'limit=201', 'after_id=01', 'upto_id=-1', 'after_id=5&upto_id=2'])
async def test_invalid_message_cursor_or_limit_is_rejected(history_database, tmp_path, query):
    async with history_client(history_database, tmp_path) as (_, client, _, _, _):
        assert (await client.get('/api/conversations/1/messages?' + query)).status_code == 422


async def test_empty_ended_conversation_has_stable_empty_bound(history_database, tmp_path):
    async with history_database.engine.begin() as conn:
        await conn.execute(text("UPDATE conversations SET status='已结束' WHERE id=1"))
    async with history_client(history_database, tmp_path) as (_, client, _, _, _):
        response = await client.get('/api/conversations/1/messages')
        assert response.status_code == 200
        assert response.json() == {'messages': [], 'upto_id': None, 'next_after_id': None, 'turn_metadata': {}}


async def test_real_graph_terminal_root_and_pending_projection_keep_original_metadata(history_database, tmp_path):
    from app.workflow.agent import build_agent_graph
    from app.workflow.graph import build_workflow_graph
    async with history_database.engine.begin() as conn:
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (1,1,'user','旧问'),(2,1,'assistant','旧答[1]')"))
    async with history_client(history_database, tmp_path) as (_, client, saver, _, _):
        graph = build_workflow_graph(build_agent_graph(), checkpointer=saver)
        state = {'state_version': 2, 'conversation_id': '1', 'user_message_id': '1', 'raw_question': '旧问',
            'turn_status': 'completed', 'final_message_id': '2', 'final_answer': '旧答[1]',
            'citations': [{'n': 1, 'chunk_id': 'original', 'section_path': None, 'question': '问', 'answer': '答'}],
            'tool_trace': [{'node': 'tool_node', 'origin': 'agent', 'name': 'query_order', 'tool_call_id': 'call',
                'status': 'success', 'attempts': 1, 'elapsed_seconds': .1}],
            'suggested_actions': [], 'refund_offer': {'assistant_message_id': '2', 'offer_id': str(uuid4()),
                'order_snapshot': {'private': 'not public'}, 'policy_snapshot': {'private': 'not public'}}}
        config = await graph.aupdate_state(checkpoint_config('1'), state, as_node='log_response')
        assert (await graph.aget_state(config)).next == ()
        # Simulate the next invocation's pending projection on an immutable completed root.
        await saver.aput_writes(config, [('citations', []), ('turn_status', 'running')], '00000000-0000-0000-0000-000000000000')
        response = await client.get('/api/conversations/1/messages')
        assert response.status_code == 200
        item = response.json()['turn_metadata']['2']
        assert item['citations'][0]['chunk_id'] == 'original'
        assert item['tool_badges'] == [{'name': 'query_order', 'tool_call_id': 'call', 'status': 'success'}]
        assert item['refund_offer'] == {'assistant_message_id': '2', 'checkpoint_id': config['configurable']['checkpoint_id'],
            'offer_id': state['refund_offer']['offer_id']}
        assert 'private' not in response.text


@pytest.mark.parametrize('changes', [{'citations': [{'n': 1}]}, {'tool_trace': None}])
async def test_malformed_optional_metadata_does_not_hide_original_text(history_database, tmp_path, changes):
    async with history_database.engine.begin() as conn:
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (2,1,'assistant','旧答[1]')"))
    async with history_client(history_database, tmp_path) as (_, client, saver, _, _):
        await put_root(saver, **changes)
        response = await client.get('/api/conversations/1/messages')
        assert response.status_code == 200
        assert response.json()['messages'][0]['content'] == '旧答[1]'
        assert response.json()['turn_metadata']['2']['citations'] == ([] if 'citations' in changes else [
            {'n': 1, 'chunk_id': 'old-chunk', 'section_path': '原政策', 'question': '原问题', 'answer': '原证据'}])


@pytest.mark.parametrize('query', ['before_id=01', 'before_id=18446744073709551616', 'limit=0', 'limit=201'])
async def test_invalid_list_cursor_is_rejected(history_database, tmp_path, query):
    async with history_client(history_database, tmp_path) as (_, client, _, _, _):
        assert (await client.get('/api/conversations?' + query)).status_code == 422


async def test_no_checkpoint_storage_still_returns_original_and_safe_database_error(history_database, tmp_path):
    await seed_messages(history_database, 2)
    async with history_client(history_database, tmp_path) as (app, client, _, _, _):
        app.state.history_reader.checkpointer = None
        response = await client.get('/api/conversations/1/messages')
        assert response.status_code == 200 and response.json()['turn_metadata'] == {}
        assert response.json()['messages'][1]['content'] == '原文2🙂'
        class Broken:
            async def read_page(self, *args, **kwargs):
                raise RuntimeError('SECRET database details')
            async def list_for_user(self, *args, **kwargs):
                raise RuntimeError('SECRET database details')
        app.state.repository = Broken()
        for path in ['/api/conversations', '/api/conversations/1/messages']:
            response = await client.get(path)
            assert response.status_code == 503 and response.json()['code'] == 'database_error'
            assert 'SECRET' not in response.text


async def test_next_input_checkpoint_cannot_replace_original_completed_locator(history_database, tmp_path):
    from app.workflow.agent import build_agent_graph
    from app.workflow.graph import build_workflow_graph
    async with history_database.engine.begin() as conn:
        await conn.execute(text("INSERT INTO messages (id,conversation_id,role,content) VALUES (1,1,'user','旧问'),(2,1,'assistant','旧答[1]'),(3,1,'user','新问')"))
    async with history_client(history_database, tmp_path) as (_, client, saver, model, _):
        graph = build_workflow_graph(build_agent_graph(), checkpointer=saver)
        original = await graph.aupdate_state(checkpoint_config('1'), {'conversation_id': '1', 'turn_status': 'completed',
            'final_message_id': '2', 'final_answer': '旧答[1]', 'citations': [], 'suggested_actions': ['create_ticket']}, as_node='log_response')
        # Stop before any real node/model: the next input root still carries previous completed values.
        await graph.ainvoke({'user_message_id': '3', 'raw_question': '新问', 'turn_status': 'running',
            'final_message_id': None, 'final_answer': None}, checkpoint_config('1'), interrupt_before=['resolve_reference'], durability='sync')
        roots = [root async for root in saver.alist(checkpoint_config('1'))]
        assert any('__start__' in root.checkpoint['channel_values'] and
            root.checkpoint['channel_values'].get('turn_status') == 'completed' for root in roots)
        response = await client.get('/api/conversations/1/messages')
        assert response.status_code == 200
        assert response.json()['turn_metadata']['2']['actions']['checkpoint_id'] == original['configurable']['checkpoint_id']
        assert model.requests == 0


@pytest.mark.parametrize('legacy', [False, True])
@pytest.mark.parametrize('payload,status', [({'found': True, 'matches': []}, 'success'),
                                          ({'error': {'code': 'unavailable'}}, 'error')])
async def test_workflow_produced_root_restores_badge_through_history_api(history_database, tmp_path, legacy, payload, status):
    from langchain_core.messages import HumanMessage, AIMessage
    from langgraph.runtime import Runtime
    from app.workflow.nodes import workflow_tool
    from app.workflow.state import new_turn_state
    from app.workflow.agent import build_agent_graph
    from app.workflow.graph import build_workflow_graph
    repository = ConversationRepository(history_database)
    user = HumanMessage('退换货政策是怎样的？')
    user.id = str(await repository.append_message('1', user))
    state = new_turn_state(conversation_id='1', user_message_id=int(user.id),
                           raw_question=user.content, category=None, messages=[user])
    async def operation():
        return payload
    update = await workflow_tool(state, Runtime(context=SimpleNamespace(repository=repository,
        settings=SimpleNamespace()), stream_writer=lambda event: None),
        'retrieve_knowledge', 'query_faq', {'keyword': user.content}, operation)
    if legacy:
        update['tool_trace'][0].pop('status', None)
    else:
        assert update['tool_trace'][0]['status'] == status
    final = AIMessage('原始政策答复')
    final.id = str(await repository.append_message('1', final))
    state.update(update)
    state.update(messages=[user, *update['messages'], final], final_answer=final.content,
                 final_message_id=final.id, turn_status='completed')
    async with history_client(history_database, tmp_path) as (_, client, saver, _, _):
        graph = build_workflow_graph(build_agent_graph(), checkpointer=saver)
        await graph.aupdate_state(checkpoint_config('1'), state, as_node='log_response')
        response = (await client.get('/api/conversations/1/messages')).json()
        assert response['turn_metadata'][final.id]['tool_badges'] == [{
            'name': 'query_faq', 'tool_call_id': update['tool_trace'][0]['tool_call_id'], 'status': status}]
        assert [row['role'] for row in response['messages']] == ['user', 'assistant', 'tool', 'assistant']


@pytest.mark.parametrize('variant', ['missing_result', 'wrong_id', 'error', 'payload_error', 'wrong_origin', 'bad_node', 'prior_turn'])
async def test_legacy_workflow_trace_never_invents_success(history_database, tmp_path, variant):
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    await seed_messages(history_database, 2)
    trace = {'node': 'retrieve_knowledge', 'origin': 'workflow', 'name': 'query_faq', 'tool_call_id': 'legacy'}
    messages = [HumanMessage('原文1🙂', id='1'), AIMessage('', tool_calls=[{
        'id': 'legacy', 'name': 'query_faq', 'args': {}}]), ToolMessage('{}', tool_call_id='legacy'),
        AIMessage('原文2🙂', id='2')]
    if variant == 'missing_result': messages.pop(2)
    if variant == 'wrong_id': messages[2].tool_call_id = 'other'
    if variant == 'error': messages[2].status = 'error'
    if variant == 'payload_error': messages[2].content = '{"error":{"code":"unavailable"}}'
    if variant == 'wrong_origin': trace['origin'] = 'unknown'
    if variant == 'bad_node': trace['node'] = []
    if variant == 'prior_turn': messages.insert(3, HumanMessage('另一个问题', id='99'))
    async with history_client(history_database, tmp_path) as (_, client, saver, _, _):
        await put_root(saver, answer='原文2🙂', tool_trace=[trace], messages=messages,
                       user_message_id='99' if variant == 'prior_turn' else '1')
        badges = (await client.get('/api/conversations/1/messages')).json()['turn_metadata']['2']['tool_badges']
        assert not any(badge['status'] == 'success' for badge in badges)
