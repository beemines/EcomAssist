"""Recognize permanent billing failures using typed SDK metadata only."""
from openai import APIStatusError


def is_bigmodel_quota_failure(error: BaseException) -> bool:
    # LangChain may wrap the SDK exception. Never inspect free text or response bodies.
    pending, seen = [error], set()
    while pending and len(seen) < 32:
        item = pending.pop()
        if id(item) in seen:
            continue
        seen.add(id(item))
        if (isinstance(item, APIStatusError) and item.status_code == 429
                and type(item.code) in (str, int) and str(item.code) == '1113'
                and item.request.url.host == 'open.bigmodel.cn'):
            return True
        pending.extend(child for child in (item.__cause__, item.__context__) if child is not None)
        if isinstance(item, BaseExceptionGroup):
            pending.extend(item.exceptions)
    return False
