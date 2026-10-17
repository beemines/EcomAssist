"""Read-only SQL and existing root SQLite evidence; never setup a saver or DDL."""
import argparse
import asyncio
from contextlib import closing
from dataclasses import asdict
import json
from pathlib import Path
import sqlite3
import sys

from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from app.context.acceptance import profile_settings
from app.db.session import Database
from app.repositories.context import ContextRepository
from app.repositories.conversations import ConversationRepository, _conversation_id
from app.repositories.records import record_from_message


def read_checkpoint(path, conversation_id):
    path = Path(path).resolve()
    if not path.is_file():
        return None
    with closing(sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)) as db:
        db.execute('PRAGMA query_only=ON')
        row = db.execute('SELECT checkpoint_id,type,checkpoint FROM checkpoints '
            'WHERE thread_id=? AND checkpoint_ns=? ORDER BY checkpoint_id DESC LIMIT 1',
            (conversation_id, '')).fetchone()
    if row is None:
        return None
    checkpoint = JsonPlusSerializer().loads_typed((row[1], row[2]))
    state = checkpoint['channel_values']
    if state.get('conversation_id') != conversation_id:
        raise ValueError('Checkpoint conversation mismatch')
    return dict(checkpoint_id=row[0], turn_status=state.get('turn_status'),
        context_snapshot=state.get('context_snapshot'),
        messages=[asdict(record_from_message(message, identifier=int(message.id))) for message in state.get('messages', [])])


async def collect(database, checkpoint, conversation_id):
    _conversation_id(conversation_id)
    raw = [asdict(row) for row in await ConversationRepository(database).load_messages(conversation_id)]
    anchors, summaries = await ContextRepository(database).load(conversation_id)
    root = read_checkpoint(checkpoint, conversation_id)
    return dict(conversation_id=conversation_id, mode='read-only-storage', original_rows=raw,
        anchors=asdict(anchors), summaries=[asdict(segment) | {'created_at': segment.created_at.isoformat()} for segment in summaries],
        checkpoint=root, checkpoint_exists=root is not None,
        sql_checkpoint_equal=(raw == root['messages']) if root is not None else None)


async def run(args):
    config = profile_settings(args.profile)
    root = Path(__file__).resolve().parents[1]
    path = args.checkpoint or root/f'runtime/workflow/context-{args.profile}-8004.sqlite'
    database = Database(config.database_url)
    try:
        result = await collect(database, path, args.conversation_id)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    finally:
        await database.dispose()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--conversation-id', required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--profile', choices=('default','demo'), default='default')
    parser.add_argument('--checkpoint', type=Path)
    args = parser.parse_args(argv)
    try:
        asyncio.run(run(args))
    except Exception as exc:
        print(f'Storage evidence failed ({type(exc).__name__}); no migration attempted', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
