"""No seeded anchors: real graph, real SQLite saver and real summary manager."""
import importlib
import pytest


def replay_api():
    try:
        return importlib.import_module('app.context.replay')
    except ImportError:
        pytest.fail('Offline graph replay is missing')


@pytest.mark.parametrize('profile', ['default', 'demo'])
async def test_fixed_trajectory_replays_actual_graph_and_context(profile, tmp_path):
    result = await replay_api().replay(profile, tmp_path)
    assert len(result['turns']) == 21
    assert result['sql_checkpoint_equal']
    assert result['final_recall']['order_id'] == '1001'
    assert result['final_recall']['source_present']
    assert result['final_recall']['unresolved'] and result['final_recall']['no_refund']
    events = set(result['events'])
    expected = {'context_downgrade', 'summary_trigger', 'summary_done'}
    assert (expected <= events) if profile == 'demo' else not (expected & events)
    assert len(result['history_turn_ids']) == 21
    assert all(row['within_budget'] for row in result['calls'])
    assert 'summary_failed' not in events
    assert result['business_turns'] == [1, 4, 10, 16, 21]
    assert result['general_no_expansion_or_selection']
    from app.repositories.records import decode_tool_calls
    requests = [decode_tool_calls(row['tool_calls'])[0] for row in result['original_rows'] if row['tool_calls']]
    business = [(request['name'], request['args']['order_id']) for request in requests if request['name'] != 'query_faq']
    assert business == [('query_logistics','1001'),('query_order','1002'),('query_logistics','1002'),('query_order','1002'),('query_order','1001')]
    assert len([request for request in requests if request['name']=='query_faq']) == 16
    if profile == 'demo':
        assert result['first_order_in_summary']
        assert result['final_recall']['source_kind'] == 'summary'
        assert result['summary_completed_while_final_blocked']
    # Read the actual persisted saver without setup/DDL; raw SQL and checkpoint
    # content/tool JSON/IDs must remain byte-for-byte the same projection.
    import importlib.util
    from pathlib import Path
    script = Path(__file__).parents[1]/'scripts/context-storage-evidence.py'
    spec = importlib.util.spec_from_file_location('context_evidence', script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    checkpoint = Path(result['checkpoint_path'])
    before = checkpoint.read_bytes()
    stored = module.read_checkpoint(checkpoint, '1')
    assert stored['messages'] == result['original_rows']
    assert checkpoint.read_bytes() == before


async def test_long_summary_risk_is_observable_without_fabricated_recall(tmp_path):
    result = await replay_api().replay('demo', tmp_path, summary_chars=200)
    assert result['omitted_summary_seqs']
    assert result['final_recall']['source_present'] is False
    assert result['final_recall']['order_id'] is None
