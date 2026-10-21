from datetime import datetime, timezone
import pytest


def test_snapshot_preserves_full_text_score_order_and_prompt_projection():
    from app.flywheel.snapshots import capture_retrieval_snapshot
    payload = {'matches': [
        {'id': 2, 'question': '低分原问题', 'answer': '完整低分原文', 'section_path': None, 'score': .2, 'score_kind': 'rerank'},
        {'id': 9007199254740993, 'question': '高分原问题', 'answer': '中文完整原文' * 200, 'section_path': '售后/运费', 'score': .9, 'score_kind': 'rerank'},
    ]}
    snapshot = capture_retrieval_snapshot(payload, prompt_ids=['2'], strategy='hybrid_rerank',
        retrieved_at=datetime(2026, 10, 19, tzinfo=timezone.utc))
    payload['matches'][1]['answer'] = '后来改过的知识'
    assert snapshot.status == 'captured'
    assert [(c.chunk_id, c.rank, c.in_prompt, c.score_kind) for c in snapshot.payload.chunks] == [
        ('9007199254740993', 1, False, 'rerank'), ('2', 2, True, 'rerank')]
    assert snapshot.payload.chunks[0].answer == '中文完整原文' * 200
    assert snapshot.payload.chunks[0].score == .9


def test_no_retrieval_is_not_zero_recall():
    from app.flywheel.snapshots import snapshot_from_state
    none = snapshot_from_state({'retrieval_performed': False, 'retrieval_snapshot': None})
    zero = snapshot_from_state({'retrieval_performed': True, 'retrieval_snapshot': None,
        'evidence_payload': {'matches': [], 'retrieval': {'strategy': 'hybrid_rerank'}}})
    assert none.status == 'not_retrieved' and none.payload is None
    assert zero.status == 'captured' and zero.payload.chunks == []


def test_old_query_without_payload_is_explicitly_unavailable():
    from app.flywheel.snapshots import snapshot_from_state
    result = snapshot_from_state({'tool_trace': [{'name': 'query_faq', 'status': 'success'}],
                                  'evidence_payload': {}})
    assert result.status == 'unavailable'
    assert result.payload.reason == 'legacy_payload_missing' and result.payload.chunks == []


@pytest.mark.parametrize('matches', [[{'id': 1, 'answer': '旧版缺少分数和问题字段'}], ['损坏的旧片段']])
def test_incomplete_legacy_payload_keeps_verifiable_turn_but_marks_evidence_unavailable(matches):
    from app.flywheel.snapshots import snapshot_from_state
    result = snapshot_from_state({'retrieval_performed': True, 'evidence_payload': {'matches': matches}})
    assert result.status == 'unavailable' and result.payload.reason == 'legacy_payload_missing'


def test_explicit_nonretrieval_is_authority_after_an_order_could_not_be_selected():
    from app.flywheel.snapshots import snapshot_from_state
    result = snapshot_from_state({'route': 'after_sales', 'retrieval_performed': False,
        'retrieval_snapshot': None, 'tool_trace': [{'name': 'query_order', 'status': 'error'}]})
    assert result.status == 'not_retrieved' and result.payload is None


@pytest.mark.parametrize('metadata', [{}, {'messages': None, 'tool_trace': None, 'evidence_payload': None}])
def test_missing_legacy_retrieval_metadata_is_not_claimed_as_verified_nonretrieval(metadata):
    from app.flywheel.snapshots import snapshot_from_state
    result = snapshot_from_state(metadata)
    assert result.status == 'unavailable' and result.payload.reason == 'legacy_payload_missing'


def test_agent_additional_faqs_merge_complete_original_snapshots():
    from app.flywheel.snapshots import capture_turn_retrieval
    first = capture_turn_retrieval({}, {'matches': [
        {'id': 1, 'question': '旧证据', 'answer': '原文1', 'section_path': None, 'score': .8, 'score_kind': 'rerank'}]}, prompt_ids=['1'])
    second = capture_turn_retrieval({'retrieval_snapshot': first.model_dump(mode='json')}, {'matches': [
        {'id': 2, 'question': '新证据', 'answer': '原文2', 'section_path': None, 'score': .9, 'score_kind': 'rerank'}]}, prompt_ids=['2'])
    assert [(c.chunk_id, c.answer, c.in_prompt) for c in second.payload.chunks] == [
        ('2', '原文2', True), ('1', '原文1', False)]


@pytest.mark.parametrize('bad', [float('nan'), float('inf')])
def test_snapshot_never_sanitizes_invalid_score_into_good_evidence(bad):
    from app.flywheel.snapshots import capture_retrieval_snapshot
    with pytest.raises(ValueError):
        capture_retrieval_snapshot({'matches': [{'id': 1, 'question': 'q', 'answer': 'a',
            'score': bad, 'score_kind': 'rerank'}]}, prompt_ids=[], strategy='hybrid_rerank',
            retrieved_at=datetime.now(timezone.utc))


def test_new_turn_cannot_reuse_a_previous_turn_snapshot():
    from app.workflow.state import new_turn_state
    state = new_turn_state(conversation_id='1', user_message_id=3, raw_question='下一轮',
                           category=None, messages=[])
    assert state['retrieval_performed'] is False and state['retrieval_snapshot'] is None


async def test_forced_knowledge_node_captures_before_budget_projection():
    from tests.test_after_sales_workflow import context, invoke
    from tests.test_evidence import payload
    ctx = context('商品咨询', data=payload(('完整政策原文',)))
    ctx.settings.flywheel_enabled = True
    _, result = await invoke(ctx, '一般退货政策是什么？')
    assert result['retrieval_performed'] is True
    assert result['retrieval_snapshot']['payload']['chunks'][0]['answer'] == '完整政策原文'
    assert result['retrieval_snapshot']['payload']['chunks'][0]['in_prompt'] is True


async def test_agent_faq_tool_also_captures_original_evidence():
    from tests.test_workflow_agent import setup, run, control
    from tests.workflow_fakes import workflow_call
    ctx, state = setup([workflow_call('query_faq', {'keyword': '运费'}), control()],
        intent='其他', question='运费是多少', answer='满99元包邮[1]')
    async def retrieve(keyword, *, raw_question, category=None):
        return {'found': True, 'matches': [{'id': 1, 'question': '运费标准', 'answer': '满99元包邮',
            'section_path': None, 'score': .9, 'score_kind': 'rerank'}],
            'retrieval': {'strategy': 'hybrid_rerank', 'candidate_count': 1, 'match_count': 1}}
    ctx.faq_repository.retrieve = retrieve
    ctx.settings.flywheel_enabled = True
    result, _ = await run(ctx, state)
    assert result['retrieval_performed'] is True
    assert result['retrieval_snapshot']['payload']['chunks']


def test_legacy_agent_faq_recovers_only_the_original_turn_full_tool_result():
    import json
    from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
    from app.flywheel.snapshots import snapshot_from_state
    def pair(call_id, answer):
        return [AIMessage('', tool_calls=[{'id': call_id, 'name': 'query_faq', 'args': {}}]),
            ToolMessage(json.dumps({'matches': [{'id': 1, 'question': '原问题', 'answer': answer,
                'score': .9, 'score_kind': 'rerank'}]}), tool_call_id=call_id)]
    result = snapshot_from_state({'user_message_id': '3', 'messages': [HumanMessage('上一轮', id='1'),
        *pair('previous', '不能取上一轮'), HumanMessage('当前问题', id='3'), *pair('original', '整块原证据')],
        'evidence_payload': {'matches': []}, 'retrieval_performed': True})
    assert result.payload.chunks[0].answer == '整块原证据'
    assert result.payload.chunks[0].in_prompt is False
