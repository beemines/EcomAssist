from pathlib import Path

from app.knowledge.chunking import chunk_markdown
from app.repositories.knowledge import KnowledgeRepository


async def import_document(path: Path, content_type: str, repository: KnowledgeRepository) -> list[int]:
    """Validate the whole UTF-8 document before the one atomic pending insert."""
    drafts = chunk_markdown(path.read_text(encoding="utf-8-sig"), document_name=path.stem,
                            content_type=content_type)
    return await repository.add_chunks(drafts, link_neighbors=True)
