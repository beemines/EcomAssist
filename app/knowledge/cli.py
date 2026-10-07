"""Run with python -m app.knowledge.cli; every mutation uses the shared job lock."""

import argparse
import asyncio
from contextlib import AsyncExitStack
from pathlib import Path
import sys

from app.config import load_settings
from app.db.session import Database
from app.knowledge.chunking import ChunkingError
from app.knowledge.ingestion import import_document
from app.knowledge.embeddings import SiliconFlowEmbedder
from app.knowledge.locking import job_lock
from app.knowledge.migration import migrate
from app.knowledge.vectorization import PendingVectorizer
from app.knowledge.vectors import MilvusIndex
from app.repositories.knowledge import KnowledgeRepository


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
    return result


async def run(args: argparse.Namespace) -> None:
    settings = load_settings()
    database = Database(settings.database_url)
    try:
        async with job_lock(database):
            if args.command == "migrate":
                await migrate(database)
                print("Knowledge schema ready")
            elif args.command == "import-document":
                ids = await import_document(args.path, args.content_type, KnowledgeRepository(database))
                print(f"Imported {len(ids)} pending chunks")
            elif args.command in ('init-vectors', 'vectorize-pending'):
                async with AsyncExitStack() as resources:
                    index = MilvusIndex(str(settings.milvus_uri), timeout=settings.milvus_timeout_seconds)
                    resources.push_async_callback(index.aclose)
                    if args.command == 'init-vectors':
                        await index.ensure_collection()
                        print('Dense vector collection ready')
                    else:
                        embedder = SiliconFlowEmbedder(settings)
                        resources.push_async_callback(embedder.aclose)
                        count = await PendingVectorizer(KnowledgeRepository(database), embedder, index).run(args.batch_size)
                        print(f'Vectorized {count} pending chunks')
    finally:
        await database.dispose()


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        asyncio.run(run(args))
    except ChunkingError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except Exception as exc:
        # Driver/config exceptions can embed credentials or document contents.
        print(f"Knowledge job failed ({type(exc).__name__}); check configuration and input", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
