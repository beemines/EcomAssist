import hashlib
import pytest
from sqlalchemy import text
from tests.integration.test_review_queue_storage import publication_db,pending_review
from tests.integration.test_flywheel_publication_storage import approved


@pytest.mark.parametrize('loss_stage',['embedding','upsert'])
async def test_real_jobs_lost_publication_connection_stops_before_upsert_or_done(publication_db,loss_stage):
    from app.flywheel.publication import PublicationWorker
    from app.flywheel.leases import LeaseLost
    from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
    from app.repositories.knowledge import KnowledgeRepository
    from tests.test_hybrid_jobs import Index
    repo,identifier,receipt=await approved(publication_db)
    lock='ch03:'+hashlib.sha256(publication_db.engine.url.database.encode()).hexdigest()[:48]
    async def lose():
        async with publication_db.engine.begin() as connection:
            owner=await connection.scalar(text('SELECT IS_USED_LOCK(:lock)'),{'lock':lock})
            assert type(owner) is int
            await connection.execute(text(f'KILL CONNECTION {owner}'))
    class Embedder:
        async def embed(self,texts):
            if loss_stage=='embedding':await lose()
            return [[.1]*1024 for _ in texts]
    class DelayedIndex(Index):
        async def upsert(self,rows):
            result=await super().upsert(rows)
            if loss_stage=='upsert':await lose()
            return result
    index=DelayedIndex();jobs=HybridKnowledgeJobs(KnowledgeRepository(publication_db),Embedder(),index)
    with pytest.raises(LeaseLost):await PublicationWorker(repo,jobs).publish(identifier)
    assert index.calls==(0 if loss_stage=='embedding' else 1)
    async with publication_db.session() as session:
        assert await session.scalar(text('SELECT vectorize_status FROM knowledge_chunks WHERE id=:id'),
            {'id':receipt.knowledge_chunk_id})=='pending'


async def test_human_category_survives_publish_and_same_category_retrieval(publication_db,milvus_collection):
    from app.flywheel.publication import ReviewService,PublicationWorker
    from app.knowledge.hybrid_jobs import HybridKnowledgeJobs
    from app.repositories.knowledge import KnowledgeRepository
    from app.retrieval.milvus import HybridMilvusIndex
    from app.retrieval.service import RetrievalService
    from app.retrieval.types import QueryPlan
    from tests.test_hybrid_jobs import Embedder
    repo,identifier=await pending_review(publication_db)
    question='耳机A1保修期限是多久？'
    receipt=await ReviewService(repo).approve(identifier,normalized_question=question,
        approved_answer='【模拟政策】耳机A1保修一年。',category='耳机')
    service=milvus_collection
    index=HybridMilvusIndex(service.uri,collection=service.name,client=service.client)
    await index.ensure_collection()
    knowledge=KnowledgeRepository(publication_db);embedder=Embedder()
    assert (await PublicationWorker(repo,HybridKnowledgeJobs(knowledge,embedder,index)).publish(identifier)).status=='ready'
    class Rerank:
        async def rank(self,query,documents,*,top_n):
            from app.retrieval.types import RerankHit
            return [RerankHit(index=i,score=.9) for i in range(len(documents))][:top_n]
    retrieval=RetrievalService(knowledge,embedder,index,None,Rerank())
    bundle=await retrieval.retrieve(question,category='耳机',strategy='hybrid_rerank',
        query_plan=QueryPlan(standard=question,expansions=[]),top_k=10)
    assert [row.chunk.id for row in bundle.matches]==[int(receipt.knowledge_chunk_id)]
