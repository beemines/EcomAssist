from dataclasses import replace
from types import SimpleNamespace
import json
from langchain_core.messages import ToolMessage
from app.tools.results import normalize_result
from tests.tool_system_fakes import make_registration


def test_mcp_structured_artifact_projection_preserves_mock_and_translates_enum():
    definition = replace(make_registration('read').definition,
        output_fields=('status', 'order_id'), status_map={'moving': '运输中'})
    raw = ToolMessage(content=[{'type': 'text', 'text': 'internal'}], tool_call_id='call',
        artifact=SimpleNamespace(structured_content={'status': 'moving', 'order_id': '1001', 'secret': 'private', 'mock': True}))
    result = normalize_result(raw, definition)
    assert result.content == {'status': '运输中', 'order_id': '1001', 'mock': True}
    assert '运输中' in json.dumps(result.content, ensure_ascii=False)


def test_error_toolmessage_cannot_become_success_even_with_structured_artifact():
    raw = ToolMessage(content='failed', tool_call_id='call', status='error',
        artifact=SimpleNamespace(structured_content={'ok': True}))
    result = normalize_result(raw, make_registration('read').definition)
    assert result.status == 'error' and 'error' in result.content


def test_text_blocks_json_and_malformed_content_are_classified():
    definition = make_registration('read').definition
    assert normalize_result(ToolMessage(content=[{'type': 'text', 'text': '{"answer":"中文"}'}], tool_call_id='call'), definition).content == {'answer': '中文'}
    assert normalize_result(ToolMessage(content='not json', tool_call_id='call'), definition).status == 'error'


def test_empty_faq_keeps_retrieval_contract_for_low_confidence_gate():
    definition = make_registration('query_faq').definition
    payload = {'found': False, 'matches': [], 'retrieval': {'strategy': 'hybrid_rerank'}}
    result = normalize_result(payload, definition)
    assert result.status == 'error' and result.content['error']['code'] == 'not_found'
    assert result.content['matches'] == []
    assert result.content['retrieval']['strategy'] == 'hybrid_rerank'
