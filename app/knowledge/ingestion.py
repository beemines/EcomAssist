# 文档导入先完成整份文件的离线解析，再交由仓储原子保存。
from pathlib import Path

from app.knowledge.chunking import chunk_markdown
from app.repositories.knowledge import KnowledgeRepository


# 读取兼容 BOM 的 UTF-8 文档，完整分块校验后一次插入 pending 记录并关联相邻块，返回主键。
async def import_document(path: Path, content_type: str, repository: KnowledgeRepository) -> list[int]:
    """Validate the whole UTF-8 document before the one atomic pending insert."""
    drafts = chunk_markdown(path.read_text(encoding="utf-8-sig"), document_name=path.stem,
                            content_type=content_type)
    return await repository.add_chunks(drafts, link_neighbors=True)
