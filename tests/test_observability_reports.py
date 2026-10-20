import json
from types import SimpleNamespace
import httpx
import pytest


def test_trend_declines_only_compare_complete_same_config_runs():
    from app.eval_pipeline.trends import compare_runs
    def row(identifier,score,config='a',errors=0,n=10):
        return {'id':str(identifier),'metrics':{'status':'completed' if not errors else 'completed_with_errors',
            'config_fingerprint':config,'errors':errors,
            'scores':{'faithfulness':{'value':score,'valid_n':n}}}}
    result=compare_runs([row(3,.8),row(2,.9),row(1,.7,'other')])
    assert result['latest_id']=='3' and result['previous_id']=='2'
    assert result['metrics']['faithfulness']['delta']==pytest.approx(-.1)
    assert result['declined_count']==1
    for current in (row(3,.8,errors=1),row(3,None),row(3,.8,n=7)):
        comparison=compare_runs([current,row(2,.9)])
        assert comparison['metrics']['faithfulness']['delta'] is None
    assert compare_runs([row(3,.8),row(2,.9,'other')])['previous_id'] is None


async def test_calibration_api_reads_fixed_artifact_and_rejects_cross_origin(tmp_path):
    from fastapi import FastAPI
    from app.api.observability import router
    from tests.flywheel_confidence_fakes import rule
    selected=rule()
    path=tmp_path/'runtime/ch09-evidence/reference-calibration'
    path.mkdir(parents=True)
    path.joinpath('report.json').write_text(json.dumps({'rule':selected.model_dump(mode='json'),
        'calibration':{'n':3},'held_out':{'n':3},'source':{'kind':'fixture'}}),encoding='utf-8')
    app=FastAPI();app.state.chat_action_allowed_origins=[]
    app.state.confidence_report_root=tmp_path;app.state.confidence_rule=selected
    app.include_router(router)
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://127.0.0.1:8006') as client:
        response=await client.get('/api/observability/confidence')
        denied=await client.get('/api/observability/confidence',headers={'origin':'https://evil.invalid'})
        bad=await client.post('/api/observability/confidence/recompute',json={'path':'../../private'})
    assert response.status_code==200 and response.json()['active']['threshold']==selected.threshold
    assert response.json()['calibration']['n']==3
    assert denied.status_code==403 and bad.status_code==422


async def test_reference_admin_pages_have_standalone_routes():
    from app.main import create_app
    from tests.fakes import fake_settings
    app=create_app(fake_settings())
    async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://127.0.0.1:8006') as client:
        for path in ('/review','/observability','/review-queue'):
            response=await client.get(path)
            assert response.status_code==200
            assert response.headers['content-type'].startswith('text/html')
