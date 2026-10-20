"""Explicit offline UI preview on 8007, owned random MySQL schema on 3308, zero provider clients.

Uses production feedback/review/eval repositories and routes. Conversation text,
normalization, indexing and evaluation models are deliberately scripted fixtures.
This preview is never the 8006 acceptance service and proves no model quality.
"""
import asyncio
import json
import re
import sys
from contextlib import asynccontextmanager
from datetime import datetime,timezone
from pathlib import Path
from uuid import uuid4
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import uvicorn
from fastapi import FastAPI,Request
from fastapi.responses import FileResponse,StreamingResponse,JSONResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from langchain_core.messages import HumanMessage,AIMessage
from langgraph.graph import StateGraph,START,END
from langgraph.checkpoint.memory import InMemorySaver
from app.config import load_settings
from app.db.session import Database
from app.core.errors import ServiceError
from app.repositories.conversations import ConversationRepository
from app.context.history_reader import HistoryReader
from app.workflow.state import WorkflowState,new_turn_state
from app.workflow.persistence import checkpoint_config
from app.flywheel.repository import FlywheelRepository
from app.flywheel.processing import FlywheelProcessor
from app.flywheel.publication import ReviewService,PublicationWorker
from app.flywheel.feedback import FeedbackService
from app.flywheel.types import NormalizedDraft,SemanticMatch,RetrievalSnapshot,SnapshotPayload,RetrievedChunk,PoolInput
from app.flywheel.worker import FlywheelWorker
from app.schemas.chat import ChatRequest


class ScriptedPrompts:
    async def normalize(self,row):
        return NormalizedDraft(normalized_question=row['raw_question'],ai_suggested_answer='【离线草稿】请人工核实后填写，不能作为真实政策。')
    async def deduplicate(self,draft,candidates):
        return SemanticMatch(matched_review_id=next((row.id for row in candidates if row.normalized_question==draft.normalized_question),None))


class ScriptedIndexJobs:
    def __init__(self,database): self.database=database;self.failed=set()
    async def vectorize_ids(self,ids,*,lease=None):
        from app.repositories.knowledge import KnowledgeRepository
        async with self.database.session() as session:
            q=await session.scalar(text('SELECT questions FROM knowledge_chunks WHERE id=:id'),{'id':ids[0]})
        if '失败' in q and ids[0] not in self.failed:
            self.failed.add(ids[0]);raise ValueError('Scripted publication failure')
        if lease is None:await KnowledgeRepository(self.database).mark_done(ids)
        else:
            async with lease.transaction() as session:
                await KnowledgeRepository(self.database).mark_done_in_session(session,ids)


async def run():
    settings=load_settings()
    name='ch09_ui_'+uuid4().hex
    assert re.fullmatch(r'ch09_ui_[0-9a-f]{32}',name)
    admin=Database(settings.database_url.set(host='127.0.0.1',port=3308,database='mysql',
        username='root',password=settings.mysql_root_password.get_secret_value()))
    database=Database(admin.engine.url.set(database=name))
    created=False;workers=[];manager=None
    owner=ROOT/'runtime/ch09-evidence/offline-ui-owner.json'
    try:
        async with admin.engine.begin() as connection:
            await connection.execute(text(f'CREATE DATABASE `{name}` CHARACTER SET utf8mb4'))
        created=True
        owner.parent.mkdir(parents=True,exist_ok=True)
        owner.write_text(json.dumps({'schema':name,'port':3308,'offline':True,'closed':False}),encoding='utf-8')
        from app.quality.migration import _statements,migrate_quality
        from app.knowledge.migration import migrate as migrate_knowledge
        from app.context.migration import migrate_context
        from app.flywheel.migration import migrate_flywheel
        async with database.engine.begin() as connection:
            await connection.exec_driver_sql('SET NAMES utf8mb4')
            for statement in _statements((ROOT/'sql/schema.sql').read_text(encoding='utf-8'))[:2]:
                await connection.exec_driver_sql(statement)
        await migrate_knowledge(database);await migrate_quality(database)
        await migrate_context(database);await migrate_flywheel(database)
        conversations=ConversationRepository(database);pool=FlywheelRepository(database)
        saver=InMemorySaver()
        builder=StateGraph(WorkflowState);builder.add_node('finish',lambda state:state)
        builder.add_edge(START,'finish');builder.add_edge('finish',END);graph=builder.compile(checkpointer=saver)
        snapshot=RetrievalSnapshot(status='captured',payload=SnapshotPayload(strategy='offline-fixture',
            retrieved_at=datetime.now(timezone.utc),chunks=[RetrievedChunk(chunk_id='1',question='【离线片段】航空箱规格',
                answer='原文只说明外形尺寸，未说明托运条件。<script>不得执行</script>',section_path='离线示例',
                score=.2,score_kind='rerank',rank=1,in_prompt=True)]))
        async def pair(cid,question):
            uid=await conversations.append_message(cid,HumanMessage(question))
            answer='【离线预览】暂未找到足够依据，请核对政策。此回答由固定模拟模型生成。'
            aid=await conversations.append_message(cid,AIMessage(answer))
            state=new_turn_state(conversation_id=cid,user_message_id=uid,raw_question=question,category=None,
                messages=[HumanMessage(question,id=str(uid)),AIMessage(answer,id=str(aid))])
            state.update(final_answer=answer,final_message_id=str(aid),turn_status='completed',
                retrieval_performed=True,retrieval_snapshot=snapshot.model_dump(mode='json'),citations=[])
            await graph.ainvoke(state,checkpoint_config(cid))
            return uid,aid,answer
        cid=await conversations.create('demo-user');uid,aid,_=await pair(cid,'【离线预览】航空箱可以托运吗？')
        worker=FlywheelWorker(FlywheelProcessor(pool,ScriptedPrompts()))
        publisher=PublicationWorker(pool,ScriptedIndexJobs(database));workers=[worker,publisher]
        for question in ('【离线预览】航空箱可以托运吗？','【离线预览】模拟入库失败后重试'):
            if '失败' in question: uid,aid,_=await pair(cid,question)
            await pool.enqueue(PoolInput(conversation_id=cid,user_message_id=str(uid),assistant_message_id=str(aid),
                raw_question=question,source='retrieval_low_conf' if '失败' not in question else 'self_check',
                reason='离线预览样例',snapshot=snapshot))
        # Seed two complete CPU runs through the actual pipeline and SQL repository.
        from tests.eval_pipeline_fakes import dataset_and_rule,MockPipelineResources
        from app.eval_pipeline.manager import EvalPipelineManager
        from app.eval_pipeline.store import PipelineStore,EvalRunRepository
        dataset,rule,fake_settings=dataset_and_rule()
        manager=EvalPipelineManager(PipelineStore(ROOT/'runtime/ch09-evidence/offline-eval'/name),
            EvalRunRepository(database),fake_settings,rule,dataset=dataset,resources_factory=MockPipelineResources)
        for _ in range(2):
            await manager.start(run_key=str(uuid4()),scope='smoke_20',triggered_by='手动')
            while manager.tasks: await asyncio.sleep(.02)
        @asynccontextmanager
        async def lifespan(app):
            for value in workers:value.start()
            yield
            for value in workers:await value.close()
            await manager.close()
        app=FastAPI(lifespan=lifespan)
        server=uvicorn.Server(uvicorn.Config(app,host='127.0.0.1',port=8007,log_level='warning'))
        from app.api.review_queue import router as review
        from app.api.feedback import router as feedback
        from app.api.eval_runs import router as evaluations
        from app.api.conversations import router as conversation_routes
        from app.api.observability import router as observability
        app.state.chat_action_allowed_origins=[];app.state.repository=conversations
        app.state.history_reader=HistoryReader(saver,conversations)
        app.state.review_service=ReviewService(pool);app.state.flywheel_repository=pool
        app.state.eval_pipeline_manager=manager
        actual=FeedbackService(saver,conversations,pool)
        class Feedback:
            first=True
            async def submit(self,*args,**kwargs):
                if self.first:
                    self.first=False;raise ServiceError('service_unavailable','离线模拟：第一次保存失败',503)
                return await actual.submit(*args,**kwargs)
        app.state.feedback_service=Feedback()
        class Usage:
            async def read(self,*args):return {'complete':True,'in_progress':0,'rows':[
                {'purpose':'offline_preview','intent':'商品咨询','requests':2,'model_calls':4,'actual_tokens':None,
                    'estimated_tokens':560,'unknown_calls':0,'currency_cost':None}]}
        app.state.intent_usage_reader=Usage()
        for router in (review,feedback,evaluations,conversation_routes,observability):app.include_router(router)
        @app.get('/health')
        async def health():return {'status':'ok','offline':True,'message':'离线预览：固定模型、无真实索引、无外部调用'}
        @app.get('/api/conversations/{conversation_id}/pending-order')
        @app.get('/api/conversations/{conversation_id}/pending-ticket')
        async def pending(conversation_id:str):return {'conversation_id':conversation_id,'pending':None}
        @app.post('/api/offline/stop')
        async def stop(request:Request):
            from app.api.chat_actions import _guard_write
            _guard_write(request)
            server.should_exit=True
            return {'stopping':True}
        @app.get('/')
        async def chat_page():return FileResponse(ROOT/'app/static/index.html')
        @app.get('/review-queue')
        async def review_page():return FileResponse(ROOT/'app/static/review-queue.html')
        @app.post('/api/chat')
        async def chat(payload:ChatRequest):
            _,aid,answer=await pair(payload.conversation_id,payload.message)
            async def events():
                for event,data in (('delta',{'delta':answer}),('done',{'conversation_id':payload.conversation_id,'message_id':str(aid)})):
                    yield f'event: {event}\ndata: {json.dumps(data,ensure_ascii=False)}\n\n'
            return StreamingResponse(events(),media_type='text/event-stream')
        @app.exception_handler(ServiceError)
        async def error(request,exc):return JSONResponse({'code':exc.code,'message':exc.message},status_code=exc.status_code)
        app.mount('/static',StaticFiles(directory=ROOT/'app/static'),name='static')
        print('OFFLINE PREVIEW http://127.0.0.1:8007/review-queue · no external model clients',flush=True)
        await server.serve()
    finally:
        for value in workers:await value.close()
        if manager is not None:await manager.close()
        await database.dispose()
        if created:
            # Exact schema from this invocation, never the configured/shared database.
            assert admin.engine.url.port==3308 and re.fullmatch(r'ch09_ui_[0-9a-f]{32}',name)
            async with admin.engine.begin() as connection:await connection.execute(text(f'DROP DATABASE `{name}`'))
            owner.write_text(json.dumps({'schema':name,'port':3308,'offline':True,'closed':True}),encoding='utf-8')
        await admin.dispose()


if __name__=='__main__':asyncio.run(run())
