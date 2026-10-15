"""Task9只读SQL/SQLite证据，绝不清理业务行。"""
import argparse
import asyncio
import json
from pathlib import Path
from types import SimpleNamespace

from sqlalchemy import text
from app.config import load_settings
from app.db.session import Database
from app.workflow.persistence import open_checkpointer, checkpoint_config, durable_completed_root


async def snapshot(conversation_id=None, assistant_id=None, checkpoint_id=None):
    """读取明确配置目标与原始saver根；SQL助手和根必须一致才核验。"""
    settings = load_settings()
    db = Database(settings.database_url)
    result = {'target': {'host': settings.mysql_host, 'port': settings.mysql_port, 'database': settings.mysql_database, 'user': settings.mysql_user},
              'checkpoint_path': str(settings.workflow_checkpoint_path.resolve())}
    try:
        async with db.session() as session:
            result['refunds'] = [dict(r) for r in (await session.execute(text('SELECT * FROM refund_requests ORDER BY id'))).mappings()]
            result['tickets'] = [dict(r) for r in (await session.execute(text('SELECT ticket_no,conversation_id,status FROM tickets ORDER BY ticket_no'))).mappings()]
            result['conversations'] = [dict(r) for r in (await session.execute(text('SELECT id,status FROM conversations ORDER BY id'))).mappings()]
            if conversation_id:
                result['messages'] = [dict(r) for r in (await session.execute(text('SELECT id,role,content,tool_calls,tool_call_id FROM messages WHERE conversation_id=:cid ORDER BY id'), {'cid': int(conversation_id)})).mappings()]
        if conversation_id:
            async with open_checkpointer(settings.workflow_checkpoint_path.resolve()) as saver:
                config = checkpoint_config(conversation_id, checkpoint_id=checkpoint_id)
                stored = await saver.aget_tuple(config)
                if stored:
                    raw = stored.checkpoint['channel_values']
                    snap = SimpleNamespace(config=stored.config, values=raw)
                    durable = await durable_completed_root(saver, snap, conversation_id, checkpoint_id=checkpoint_id)
                    result['root_evidence'] = {'durable': durable, 'conversation_id': conversation_id,
                        'assistant_message_id': raw.get('final_message_id'), 'checkpoint_id': stored.config['configurable']['checkpoint_id'],
                        'turn_status': raw.get('turn_status'), 'raw_question': raw.get('raw_question'),
                        'resolved_question': raw.get('resolved_question'), 'intent': raw.get('intent'), 'route': raw.get('route'),
                        'refund_decision': raw.get('refund_decision'), 'refund_offer': raw.get('refund_offer'),
                        'order_selection': raw.get('order_selection'), 'stage_usage': raw.get('stage_usage'),
                        'tool_call_count': raw.get('tool_call_count'), 'final_answer': raw.get('final_answer')}
                    matching = next((m for m in result['messages'] if str(m['id']) == str(assistant_id or raw.get('final_message_id')) and m['role'] == 'assistant' and m['tool_calls'] is None), None)
                    result['sql_evidence'] = {'verified': bool(durable and matching and matching['content'] == raw.get('final_answer') and str(matching['id']) == str(raw.get('final_message_id'))),
                        'conversation_id': conversation_id, 'assistant_message_id': str(matching['id']) if matching else None}
        return result
    finally:
        await db.dispose()


def main():
    """输出本机证据文件；错误不包含数据库连接串或密钥。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--conversation-id')
    parser.add_argument('--assistant-id')
    parser.add_argument('--checkpoint-id')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    data = asyncio.run(snapshot(args.conversation_id, args.assistant_id, args.checkpoint_id))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + '\n', encoding='utf-8')
    print(json.dumps({'target': data['target'], 'refund_count': len(data['refunds']), 'output': str(args.output)}, ensure_ascii=False))


if __name__ == '__main__':
    main()

