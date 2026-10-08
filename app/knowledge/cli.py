# 离线知识任务统一持有外层任务锁，避免导入、挖掘和向量化同时修改知识状态。
"""Run with python -m app.knowledge.cli; every mutation uses the shared job lock."""

import argparse
import asyncio
from contextlib import AsyncExitStack
from datetime import datetime, timedelta
from pathlib import Path
import sys

from app.config import load_settings
from app.db.session import Database
from app.core.llm import create_model
from app.knowledge.extraction import QAExtractor
from app.knowledge.history import BEIJING, KnowledgeHistory, window
from app.knowledge.mining import ConversationMiningJob, MiningBatchError, deduplicate_staging
from app.knowledge.chunking import ChunkingError
from app.knowledge.ingestion import import_document
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.knowledge.locking import job_lock
from app.knowledge.migration import migrate
from app.knowledge.vectorization import PendingVectorizer
from app.knowledge.vectors import MilvusIndex
from app.repositories.knowledge import KnowledgeRepository


# 定义迁移、文档导入、会话挖掘、暂存去重与向量化等离线任务的命令参数。
def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Offline dense knowledge jobs")
    commands = result.add_subparsers(dest="command", required=True)
    commands.add_parser("migrate", help="Apply or verify the supplied two-table DDL")
    importer = commands.add_parser("import-document", help="Import a UTF-8 Markdown document as pending chunks")
    importer.add_argument("--path", type=Path, required=True)
    importer.add_argument("--type", choices=("policy", "faq", "manual"), required=True, dest="content_type")
    commands.add_parser('init-vectors', help='Create or verify the explicit dense Milvus collection')
    vectorizer = commands.add_parser('vectorize-pending', help='Resume pending chunks with idempotent primary keys')
    vectorizer.add_argument('--batch-size', type=int, default=20)
    miner = commands.add_parser('mine-conversations', help='Extract QA from completed conversations in a Beijing half-open window')
    miner.add_argument('--start', type=datetime.fromisoformat, required=True)
    miner.add_argument('--end', type=datetime.fromisoformat, required=True)
    miner.add_argument('--batch-size', type=int, default=20)
    commands.add_parser('deduplicate-staging', help='Promote globally unique staged QA as pending knowledge')
    commands.add_parser('run-daily', help='Mine the previous Beijing day, deduplicate and vectorize under one lock')
    return result


# 以北京时间当日零点为终点，返回前一自然日的左闭右开时间窗口。
def previous_day(now: datetime | None = None) -> tuple[datetime, datetime]:
    now = now if now is not None else datetime.now(BEIJING)
    end = now.astimezone(BEIJING).replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=None)
    return end - timedelta(days=1), end


# 在同一任务锁内执行所选工作并管理外部客户端；每日任务串联挖掘、去重和向量化。
async def run(args: argparse.Namespace) -> None:
    settings = load_settings()
    database = Database(settings.database_url)
    try:
        # 一次命令共用同一把锁；退出栈按注册顺序的逆序回收模型、嵌入与向量客户端。
        async with job_lock(database), AsyncExitStack() as resources:
            repository = KnowledgeRepository(database)
            if args.command == "migrate":
                await migrate(database)
                print("Knowledge schema ready")
            elif args.command == "import-document":
                ids = await import_document(args.path, args.content_type, KnowledgeRepository(database))
                print(f"Imported {len(ids)} pending chunks")
            elif args.command == 'deduplicate-staging':
                print(await deduplicate_staging(repository))
            if args.command in ('mine-conversations', 'run-daily'):
                model = create_model(settings.model_copy(update={'max_output_tokens': settings.qa_max_output_tokens}))
                resources.callback(model.root_client.close)
                resources.push_async_callback(model.root_async_client.close)
                start, end = previous_day() if args.command == 'run-daily' else (args.start, args.end)
                start, end = window(start, end)
                print(f'Mining Beijing window [{start.isoformat()}, {end.isoformat()})')
                counts = await ConversationMiningJob(KnowledgeHistory(database), repository,
                    QAExtractor(model, settings.input_token_budget)).run(start, end, getattr(args, 'batch_size', 20))
                print(counts)
            if args.command in ('init-vectors', 'vectorize-pending', 'run-daily'):
                index = MilvusIndex(str(settings.milvus_uri), timeout=settings.milvus_timeout_seconds)
                resources.push_async_callback(index.aclose)
                if args.command == 'init-vectors':
                    await index.ensure_collection()
                    print('Dense vector collection ready')
                else:
                    embedder = SiliconFlowEmbedder(settings)
                    resources.push_async_callback(embedder.aclose)
                    count = await PendingVectorizer(repository, embedder, index).run(getattr(args, 'batch_size', 20))
                    print(f'Vectorized {count} pending chunks')
    finally:
        await database.dispose()


# 解析参数并运行异步任务，将可公开诊断与通用失败映射为退出码，避免输出敏感异常内容。
def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        asyncio.run(run(args))
    except (ChunkingError, MiningBatchError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        # 驱动或配置异常可能包含凭据及文档内容，通用失败只输出异常类型。
        print(f"Knowledge job failed ({type(exc).__name__}); check configuration and input", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
