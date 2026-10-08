"""通过应用 API 评估工具选择，读取持久流水进行独立审计。"""

import argparse
import asyncio
import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

import httpx

from app.repositories.conversations import ConversationRepository
from app.repositories.records import decode_tool_calls
from evals.evaluate import save_report
from evals.smoke import chat_round, create_conversation


@dataclass
class ToolEvaluationReport:
    attempted: int
    not_attempted: int
    cases: list[dict]


# 独立核对已提交的消息流水、工具申请、匹配结果和最终回答。
# 校验工单号及 FAQ 结果结构，保留回答失败前已经完成的工具事实。
def audit_messages(rows, case, stream) -> dict:
    result = {'actual_tool': None, 'actual_args': {}, 'actual_found': None,
              'matches': None, 'tool_result': None, 'ticket_no': None, 'audit_error': None, 'passed': False,
              'answer_phrase_match': all(text in stream['text'] for text in case.get('answer_contains', []))}
    try:
        users = [r for r in rows if r.role == 'user']
        requests = [r for r in rows if r.tool_calls is not None]
        tools = [r for r in rows if r.role == 'tool']
        answers = [r for r in rows if r.role == 'assistant' and r.tool_calls is None]
        if len(users) != 1 or users[0].content != case['message']:
            raise ValueError
        if len(requests) > 1 or len(tools) != len(requests):
            raise ValueError
        if requests:
            call = decode_tool_calls(requests[0].tool_calls)[0]
            result.update(actual_tool=call['name'], actual_args=call['args'])
            if tools[0].tool_call_id != call['id'] or not users[0].id < requests[0].id < tools[0].id:
                raise ValueError
            content = json.loads(tools[0].content)
            if not isinstance(content, dict) or 'error' in content:
                raise ValueError
            result.update(actual_tool=call['name'], actual_args=call['args'], tool_result=content,
                          actual_found=content.get('found'), matches=content.get('matches'), ticket_no=content.get('ticket_no'))
            if call['name'] == 'query_faq':
                if type(content.get('found')) is not bool or not isinstance(content.get('matches'), list) or content['found'] != bool(content['matches']) or len(content['matches']) > 3:
                    raise ValueError
            if call['name'] == 'create_ticket':
                expected_no = 'T' + sha256(f"{stream['conversation_id']}:{users[0].id}:{call['id']}".encode()).hexdigest()[:31]
                if content.get('ticket_no') != expected_no or content.get('status') != '待处理':
                    raise ValueError
        # 即使最终回答失败，也保留已经完成的工具审计事实。
        if len(answers) != 1 or answers[0].content != stream['text']:
            raise ValueError
        if answers[0].id <= (tools[0].id if tools else users[0].id):
            raise ValueError
        result['passed'] = (stream['error_code'] is None and result['actual_tool'] == case['expected_tool']
                            and result['actual_args'] == case['expected_args']
                            and result['actual_found'] == case['expected_found'])
    except (ValueError, TypeError, KeyError):
        result['audit_error'] = 'invalid_committed_audit'
    return result


# 每个工具样例创建独立会话，比较 SSE 结果与数据库流水后汇总报告。
# 网络或流协议失败后停止后续真实请求，标签质量差异仍可继续采样。
async def evaluate_tools(client: httpx.AsyncClient, base_url: str, cases: Sequence[dict], *, repository: ConversationRepository) -> ToolEvaluationReport:
    records, attempted, stopped = [], 0, False
    for case in cases:
        record = {key: case[key] for key in ('id', 'category', 'message', 'expected_tool', 'expected_args', 'expected_found')}
        record.update(passed=False, error_code='not_attempted', stream=None, conversation_id=None,
                      actual_tool=None, actual_args=None, actual_found=None, matches=None, ticket_no=None,
                      final_answer=None, human_answer_review='pending', http_request_count=0,
                      model_request_count=None, model_count_source='requires_upstream_instrumentation')
        records.append(record)
        if stopped:
            continue
        attempted += 1
        created = await create_conversation(client, base_url, 'tool-eval-' + uuid4().hex)
        record['http_request_count'] = 1
        record['conversation_id'] = created['conversation_id']
        if created['error_code']:
            record['error_code'] = created['error_code']
            stopped = True
            continue
        stream = await chat_round(client, base_url, created['conversation_id'], case['message'], min_deltas=1)
        stream['conversation_id'] = created['conversation_id']
        record.update(stream=stream, final_answer=stream['text'], error_code=stream['error_code'], http_request_count=2)
        try:
            rows = await repository.load_messages(created['conversation_id'])
            record.update(audit_messages(rows, case, stream))
        except Exception:
            record['audit_error'] = 'audit_unavailable'
        if stream['error_code']:
            # 失败后不再发真实请求；标签/回答质量差异仍继续采样。
            stopped = True
    return ToolEvaluationReport(attempted, len(cases) - attempted, records)


# 加载标注与数据库配置，运行工具评估并保存报告，最后归还数据库连接池。
async def run_cli(args):
    from app.config import load_settings
    from app.db.session import Database
    settings = load_settings()
    database = Database(settings.database_url)
    try:
        cases = [json.loads(line) for line in args.cases.read_text(encoding='utf-8').splitlines() if line.strip()]
        async with httpx.AsyncClient(trust_env=False) as client:
            report = await evaluate_tools(client, args.base_url, cases, repository=ConversationRepository(database))
        output = asdict(report)
        output['http_request_count'] = sum(c['http_request_count'] for c in report.cases)
        output['model_request_count'] = None
        output['human_answer_review'] = 'pending'
        save_report(args.output, output)
        print(json.dumps({'attempted': report.attempted, 'not_attempted': report.not_attempted, 'passed': sum(c['passed'] for c in report.cases)}))
        return 0 if all(c['passed'] for c in report.cases) else 1
    finally:
        await database.dispose()


# 接收应用地址、样例文件和报告路径，启动异步工具评估。
def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-url', default='http://127.0.0.1:8000')
    parser.add_argument('--cases', type=Path, default=Path('evals/tool_cases.jsonl'))
    parser.add_argument('--output', type=Path, default=Path('.cache/tool-evaluation.json'))
    return asyncio.run(run_cli(parser.parse_args()))


if __name__ == '__main__':
    raise SystemExit(main())
