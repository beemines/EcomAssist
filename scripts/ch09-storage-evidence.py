"""Read only selected Ch09 facts; UTF-8 output avoids PowerShell 5.1 JSON decoding."""
import argparse
import asyncio
import json
import sys
from pathlib import Path
from uuid import UUID
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from sqlalchemy import text
from app.config import load_settings
from app.db.session import Database
from app.flywheel.types import database_id
from app.flywheel.repository import row_dict


async def read(args):
    database=Database(load_settings(ROOT/'.env').database_url)
    result={}
    try:
        async with database.session() as session:
            await session.execute(text('SET TRANSACTION READ ONLY'))
            if args.conversation_id:
                result['conversation']=[row_dict(row) for row in (await session.execute(text(
                    'SELECT id,status,summary,summary_upto_msg_id,layer1_from_msg_id FROM conversations WHERE id=:id'),
                    {'id':args.conversation_id})).mappings()]
                result['pool']=[row_dict(row) for row in (await session.execute(text(
                    'SELECT id,conversation_id,user_message_id,assistant_message_id,raw_question,source,reason,'
                    'snapshot_status,retrieved_chunks,matched_review_id,processing FROM low_confidence_questions '
                    'WHERE conversation_id=:id ORDER BY id LIMIT 100'),{'id':args.conversation_id})).mappings()]
            if args.review_id:
                result['review']=[row_dict(row) for row in (await session.execute(text(
                    'SELECT id,normalized_question,ai_suggested_answer,occurrence_count,review_status,'
                    'approved_answer,knowledge_chunk_id,publication FROM review_queue WHERE id=:id'),
                    {'id':args.review_id})).mappings()]
            if args.run_key:
                result['evaluation']=[row_dict(row) for row in (await session.execute(text(
                    'SELECT run_key,triggered_by,dataset_size,metrics,created_at FROM eval_runs WHERE run_key=:key'),
                    {'key':args.run_key})).mappings()]
            await session.rollback()
        return result
    finally: await database.dispose()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--conversation-id',type=database_id)
    parser.add_argument('--review-id',type=database_id)
    parser.add_argument('--run-key',type=lambda value:str(UUID(value)))
    args=parser.parse_args()
    if not any(vars(args).values()): parser.error('Choose at least one conversation, review or run key')
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    try: print(json.dumps(asyncio.run(read(args)),ensure_ascii=False,indent=2))
    except Exception as exc: parser.exit(1,f'Read stopped: {type(exc).__name__}; inspect schema/config locally\n')


if __name__=='__main__': main()

