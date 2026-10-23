"""Contract fixtures, never real model-accuracy evidence."""
import asyncio
import httpx
import pytest
from app.topics.types import Prediction
from tests.test_topic_manifest import model_files

@pytest.mark.parametrize('kind',['ok','empty','duplicate','too_many','blank'])
def test_http_service_binds_identity_and_validates_inputs(tmp_path,kind,monkeypatch):
    from ml.topic_classifier.service import create_app
    from fastapi.testclient import TestClient
    from app.topics.manifest import verify_manifest
    model_files(tmp_path);identity=verify_manifest(tmp_path)
    # Explicit contract-only injection; production must possess completed human evidence.
    monkeypatch.setattr('ml.topic_classifier.service.verify_release',verify_manifest)
    class Fixture:
        def predict(self,items):
            return [Prediction(id=x.id,labels=['物流'],probabilities=[.6]*17,status='classified',
                model_version=identity.model_version,taxonomy_version=identity.taxonomy_version) for x in items]
    app=create_app(tmp_path,predictor=Fixture())
    items=[dict(id='q',text='物流在哪里')]
    if kind=='empty':items=[]
    if kind=='duplicate':items*=2
    if kind=='too_many':items=[dict(id=str(i),text='物流') for i in range(65)]
    if kind=='blank':items[0]['text']=' '
    with TestClient(app) as client:
        assert client.get('/health').json()==identity.model_dump(mode='json')
        response=client.post('/classify',json=dict(request_id='r',items=items))
        assert response.status_code==(200 if kind=='ok' else 422)
        if kind=='ok':
            assert response.json()['request_id']=='r'
            assert response.json()['items'][0]['id']=='q'

def test_service_refuses_unknown_or_modified_core_before_loading(tmp_path):
    from ml.topic_classifier.service import create_app
    model_files(tmp_path);(tmp_path/'model.safetensors').write_bytes(b'changed')
    with pytest.raises(ValueError):create_app(tmp_path,predictor=object())

def test_production_service_rejects_a_core_without_actual_review_release(tmp_path):
    from ml.topic_classifier.service import create_app
    model_files(tmp_path)
    with pytest.raises(ValueError):create_app(tmp_path)

def test_predictor_reports_long_input_and_empty_output_without_fallback(tmp_path):
    import numpy as np
    from types import SimpleNamespace
    from ml.topic_classifier.service import Predictor
    from app.topics.manifest import verify_manifest
    from app.topics.types import ClassifyItem
    model_files(tmp_path)
    predictor=object.__new__(Predictor);predictor.identity=verify_manifest(tmp_path)
    predictor.thresholds=SimpleNamespace(thresholds=[.5]*17)
    predictor.labels=tuple(__import__('app.topics.taxonomy',fromlist=['default_taxonomy']).default_taxonomy().ordered_names)
    class Classifier:
        def tokenizer(self,text,**kwargs):
            assert kwargs.get('truncation') is False
            return dict(input_ids=list(range(len(text)+2)))
        def predict(self,items):return np.full((len(items),17),-1000.)
    predictor.classifier=Classifier()
    result=predictor.predict([ClassifyItem(id='ok',text='物流在哪'),ClassifyItem(id='long',text='猫'*140)])
    assert result[0].status=='needs_review' and result[0].labels==()
    assert result[1].status=='input_too_long' and result[1].probabilities is None
    assert all(value==0. for value in result[0].probabilities)

def test_single_cpu_execution_has_a_bounded_waiting_queue(tmp_path,monkeypatch):
    import threading
    from app.topics.manifest import verify_manifest
    from ml.topic_classifier.service import create_app
    model_files(tmp_path);identity=verify_manifest(tmp_path)
    monkeypatch.setattr('ml.topic_classifier.service.verify_release',verify_manifest)
    started=threading.Event();release=threading.Event();active=0;peak=0
    class Fixture:
        def predict(self,items):
            nonlocal active,peak
            active+=1;peak=max(peak,active);started.set()
            assert release.wait(3)
            active-=1
            return [Prediction(id=x.id,labels=['物流'],probabilities=[.6]*17,status='classified',
                model_version=identity.model_version,taxonomy_version=identity.taxonomy_version) for x in items]
    app=create_app(tmp_path,predictor=Fixture())
    async def check():
        async with app.router.lifespan_context(app):
            async with httpx.AsyncClient(transport=httpx.ASGITransport(app),base_url='http://local') as client:
                def send(i):return client.post('/classify',json=dict(request_id=str(i),items=[dict(id='q',text='物流')]))
                jobs=[asyncio.create_task(send(i)) for i in range(3)]
                try:
                    for _ in range(100):
                        if app.state.admitted==3 and started.is_set():break
                        await asyncio.sleep(.01)
                    assert app.state.admitted==3
                    rejected=await send(4);assert rejected.status_code==503
                finally:release.set()
                results=await asyncio.gather(*jobs)
                assert all(result.status_code==200 for result in results)
                assert peak==1 and app.state.admitted==0
    asyncio.run(check())
