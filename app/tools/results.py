from copy import deepcopy
import json
from langchain_core.messages import ToolMessage
from app.tools.types import ToolOutcome


def result_error(code='tool_execution_error', message='工具执行失败。'):
    return ToolOutcome({'error': {'code': code, 'message': message}}, 'error', 0)


def normalize_result(raw, definition):
    if isinstance(raw, ToolMessage):
        if raw.status == 'error':
            return result_error()
        artifact = raw.artifact
        content = (artifact.get('structured_content') if isinstance(artifact, dict)
                   else getattr(artifact, 'structured_content', None))
        if content is None:
            content = raw.content
            if isinstance(content, list):
                blocks = [b['text'] for b in content if isinstance(b, dict) and b.get('type') == 'text' and isinstance(b.get('text'), str)]
                content = '\n'.join(blocks)
            if isinstance(content, str):
                try:
                    content = json.loads(content)
                except (ValueError, TypeError):
                    return result_error()
    else:
        content = raw
    if not isinstance(content, dict):
        return result_error()
    content = deepcopy(content)
    faq = definition.source == 'builtin' and definition.name == 'query_faq' and isinstance(content.get('matches'), list)
    status = 'success'
    if 'error' in content or content.get('found') is False:
        raw_error = content.get('error')
        code = raw_error.get('code') if isinstance(raw_error, dict) else 'not_found' if content.get('found') is False else None
        messages = {'not_found': '未找到对应业务数据，请核对信息。',
                    'invalid_keyword': '关键词必须是当前用户问题中的连续原文片段。',
                    'invalid_arguments': '工具参数不符合要求。', 'permission_denied': '当前调用未获授权。'}
        code = code if isinstance(code, str) and code in messages else 'tool_execution_error'
        error = result_error(code, messages.get(code, '工具执行失败。'))
        if not faq:
            return error
        # Only the trusted FAQ contract keeps evidence metadata for its low-confidence gate.
        content = {key: content[key] for key in ('found', 'matches', 'retrieval') if key in content}
        content['error'] = error.content['error']
        status = 'error'
    if definition.output_fields:
        fields = set(definition.output_fields) | {'mock', 'source'}
        content = {k: v for k, v in content.items() if k in fields}
    for key, value in content.items():
        if isinstance(value, str) and value in definition.status_map:
            content[key] = definition.status_map[value]
    try:
        serialized = json.dumps(content, ensure_ascii=False, separators=(',', ':'), allow_nan=False)
        if len(serialized) > 20000 or len(serialized.encode('utf-8')) > 65535:
            error = result_error('tool_result_too_large', '工具结果过大，无法完整保存，请缩小查询范围。')
            if faq:
                retrieval = content.get('retrieval', {})
                strategy = retrieval.get('strategy') if isinstance(retrieval, dict) else None
                error.content.update(found=False, matches=[], retrieval={'strategy':
                    strategy if strategy in ('hybrid_rerank', 'vector', 'hybrid') else 'none'})
            return error
    except (ValueError, TypeError):
        return result_error()
    return ToolOutcome(content, status, 0)
