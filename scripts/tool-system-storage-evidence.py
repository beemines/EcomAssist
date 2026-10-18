"""Read-only local SQL evidence for explicitly selected demo conversations."""
import argparse
import asyncio
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from sqlalchemy import text, bindparam
from app.config import load_settings
from app.db.session import Database


async def inspect(ids):
    db = Database(load_settings().database_url)
    try:
        async with db.session() as session:
            tickets = (await session.execute(text('SELECT conversation_id,ticket_no,ticket_type,description FROM tickets WHERE conversation_id IN :ids ORDER BY ticket_no').bindparams(bindparam('ids', expanding=True)), {'ids': ids})).mappings().all()
            audit = (await session.execute(text('SELECT conversation_id,tool_call_id,tool_name,source,status,error_code,retry_count,elapsed_ms FROM tool_audit_logs WHERE conversation_id IN :ids ORDER BY id').bindparams(bindparam('ids', expanding=True)), {'ids': ids})).mappings().all()
        print(json.dumps({'conversations': ids, 'ticket_count': len(tickets),
            'tickets': [dict(row) for row in tickets], 'audit': [dict(row) for row in audit]}, ensure_ascii=False, indent=2, default=str))
    finally:
        await db.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('conversation_ids', nargs='+', type=int)
    args = parser.parse_args()
    if any(value <= 0 for value in args.conversation_ids): parser.error('IDs must be positive')
    asyncio.run(inspect(args.conversation_ids))
