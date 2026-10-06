from sqlalchemy import select

from app.db.models import FAQ
from app.db.session import Database


class FAQRepository:
    """只在问题列做字面子串检索，不扩展同义词。"""

    def __init__(self, database: Database):
        self.database = database

    async def search(self, keyword: str, limit: int = 3) -> list[dict]:
        if not isinstance(keyword, str) or not 1 <= len(keyword) <= 128:
            raise ValueError("Invalid FAQ keyword.")
        if type(limit) is not int or limit < 1:
            raise ValueError("Invalid FAQ limit.")
        async with self.database.session() as session, session.begin():
            rows = (await session.scalars(select(FAQ).where(FAQ.question.contains(keyword, autoescape=True)).order_by(FAQ.id).limit(min(limit, 3)))).all()
            return [{"id": row.id, "question": row.question, "answer": row.answer, "category": row.category} for row in rows]
