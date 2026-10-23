"""Local CPU sidecar. No database, teacher client or real-time chat dependency."""
import asyncio
from contextlib import asynccontextmanager
from pathlib import Path
import numpy as np
from fastapi import FastAPI,HTTPException
from app.topics.cleaning import clean_question
from app.topics.manifest import read_manifest,verify_manifest,verify_release
from app.topics.types import ClassifyItem,ClassifyRequest,ClassifyResponse,Prediction
from ml.topic_classifier.artifacts import CPUClassifier
from ml.topic_classifier.evaluation import ThresholdSet,decode_logits


class Predictor:
    def __init__(self,bundle):
        bundle=Path(bundle);manifest=read_manifest(bundle)
        self.identity=verify_manifest(bundle)
        self.thresholds=ThresholdSet.model_validate_json((bundle/'thresholds.json').read_text(encoding='utf-8'))
        self.classifier=CPUClassifier(bundle,weights_hash=manifest.core.files['model.safetensors'].sha256)
        self.labels=manifest.core.labels

    def predict(self,items):
        valid=[];errors={}
        for item in items:
            cleaned=clean_question(item.text,sample_id=item.id)
            if cleaned.quarantine_reasons:errors[item.id]='invalid_input'
            elif len(self.classifier.tokenizer(cleaned.text,truncation=False,add_special_tokens=True)['input_ids'])>128:
                errors[item.id]='input_too_long'
            else:valid.append(ClassifyItem(id=item.id,text=cleaned.text))
        predictions={}
        if valid:
            logits=self.classifier.predict(valid)
            selected=decode_logits(logits,self.thresholds.thresholds)
            # Stable sigmoid; never calculate exp of an unbounded positive input.
            exp=np.exp(-np.abs(logits));probabilities=np.where(logits>=0,1/(1+exp),exp/(1+exp))
            for i,item in enumerate(valid):
                labels=tuple(label for label,present in zip(self.labels,selected[i],strict=True) if present)
                predictions[item.id]=Prediction(id=item.id,labels=labels,probabilities=probabilities[i].tolist(),
                    status='classified' if labels else 'needs_review',model_version=self.identity.model_version,
                    taxonomy_version=self.identity.taxonomy_version)
        return [predictions[item.id] if item.id in predictions else Prediction(id=item.id,labels=[],probabilities=None,
            status=errors[item.id],model_version=self.identity.model_version,taxonomy_version=self.identity.taxonomy_version)
            for item in items]

    def close(self):self.classifier.close()


def load_predictor(bundle):return Predictor(bundle)


def create_app(bundle:Path,*,predictor=None)->FastAPI:
    identity=verify_release(bundle)
    @asynccontextmanager
    async def lifespan(app):
        app.state.predictor=predictor if predictor is not None else await asyncio.to_thread(load_predictor,bundle)
        app.state.lock=asyncio.Lock();app.state.admitted=0
        try:yield
        finally:
            async with app.state.lock:
                if predictor is None:await asyncio.to_thread(app.state.predictor.close)
    app=FastAPI(lifespan=lifespan,docs_url=None,redoc_url=None,openapi_url=None)

    @app.get('/health')
    async def health():return identity.model_dump(mode='json')

    @app.post('/classify',response_model=ClassifyResponse)
    async def classify(request:ClassifyRequest):
        if app.state.admitted>=3:raise HTTPException(503,detail='busy')
        app.state.admitted+=1;acquired=False
        try:
            try:
                await asyncio.wait_for(app.state.lock.acquire(),timeout=2.)
                acquired=True
            except TimeoutError:raise HTTPException(503,detail='busy') from None
            task=asyncio.create_task(asyncio.to_thread(app.state.predictor.predict,request.items))
            try:rows=await asyncio.shield(task)
            except asyncio.CancelledError:
                # The CPU thread cannot be cancelled. Retain its lease until it really exits.
                try:await task
                finally:raise
            result=ClassifyResponse(request_id=request.request_id,identity=identity,items=rows)
            if [row.id for row in result.items]!=[row.id for row in request.items]:
                raise ValueError('Prediction membership/order changed')
            return result
        finally:
            if acquired:app.state.lock.release()
            app.state.admitted-=1
    return app
