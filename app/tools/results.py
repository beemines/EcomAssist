from copy import deepcopy
import json
from langchain_core.messages import ToolMessage
from app.tools.types import ToolOutcome


def result_error(code='tool_execution_error', message='工具未返回有效业务结果。'):
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
    if 'error' in content:
        return ToolOutcome(content, 'error', 0)
    if content.get('found') is False:
        if definition.name == 'query_faq' and isinstance(content.get('matches'), list):
            content['error'] = {'code': 'not_found', 'message': '未找到可靠知识证据。'}
            return ToolOutcome(content, 'error', 0)
        return result_error('not_found', '未找到对应业务数据，请核对信息。')
    if definition.output_fields:
        fields = set(definition.output_fields) | {'mock', 'source'}
        content = {k: v for k, v in content.items() if k in fields}
    for key, value in content.items():
        if isinstance(value, str) and value in definition.status_map:
            content[key] = definition.status_map[value]
    try:
        json.dumps(content, ensure_ascii=False, allow_nan=False)
    except (ValueError, TypeError):
        return result_error()
    return ToolOutcome(content, 'success', 0)
