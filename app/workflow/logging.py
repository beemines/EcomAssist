"""独立控制台审计：只投影固定枚举、受控身份和非负计数，不修改根日志。"""
import hashlib
import json
import logging
import math
import re
import sys
from uuid import UUID

logger = logging.getLogger('app.workflow.audit')
_console_handler = logging.StreamHandler()
_console_handler.setFormatter(None)
_ENUMS = {
    'event': {'workflow_node', 'workflow_lifecycle', 'workflow_ticket', 'workflow_refund'},
    'node': {'resolve_reference', 'classify_intent', 'retrieve_knowledge', 'confidence_gate',
        'knowledge_fallback', 'complaint_response', 'social_response', 'log_response',
        'llm_call', 'tool_node', 'finalize_answer', 'other_response', 'resolve_order', 'prepare_order_selection',
        'await_order_selection', 'load_order', 'expand_queries', 'retrieve_policies', 'classification', 'expansion', 'no_order_response'},
    'phase': {'prepared', 'checkpoint_complete', 'terminal', 'confirmed', 'result'},
    'intent': {'物流', '订单', '商品咨询', '退款退货', '售后', '投诉', '闲聊', '其他'},
    'route': {'knowledge', 'business', 'complaint', 'social', 'other', 'after_sales'},
    'reason_code': {'retrieval_low_conf', 'self_check'},
    'origin': {'workflow', 'agent'}, 'name': {'query_faq', 'query_order', 'query_logistics', 'query_product'},
    'decision_transport': {'business_tool', 'native_control', 'json_control'},
    'status': {'success', 'error'}, 'turn_status': {'completed'}, 'action': {'create_ticket', 'submit_refund'},
    'outcome': {'success', 'error', 'timeout', 'cancelled', 'disconnected', 'paused'},
    'code': {'upstream_error', 'upstream_timeout', 'invalid_structured_output', 'invalid_answer',
        'invalid_answer_citations', 'input_too_long', 'token_budget', 'tool_execution_error',
        'tool_timeout', 'invalid_arguments', 'invalid_keyword', 'conversation_ended',
        'action_not_found', 'invalid_action', 'conversation_busy', 'service_unavailable'},
}
_COUNTS = {'decision_count', 'tool_call_count', 'attempts'}
_USAGE = {'actual', 'estimated', 'actual_calls', 'estimated_calls'}


def safe_fields(values):
    """拒绝自由文本；模型工具ID仅记摘要，未知错误代码归一为受控通用值。"""
    result = {}
    for key, value in values.items():
        enum = _ENUMS.get({'selected_intent': 'intent', 'selected_route': 'route'}.get(key, key))
        if enum is not None:
            if value is None or isinstance(value, str) and value in enum:
                result[key] = value
            elif key == 'code':
                result[key] = 'upstream_error'
        elif key in {'conversation_id', 'user_message_id', 'assistant_message_id', 'final_message_id'}:
            if isinstance(value, (int, str)) and re.fullmatch(r'[1-9][0-9]{0,19}', str(value)):
                result[key] = str(value)
        elif key == 'checkpoint_id' and isinstance(value, str):
            try:
                result[key] = str(UUID(value))
            except ValueError:
                pass
        elif key == 'ticket_no' and isinstance(value, str) and re.fullmatch(r'T[0-9a-fA-F]{31,32}', value):
            result[key] = value
        elif key == 'request_no' and isinstance(value, str) and re.fullmatch(r'R[0-9a-f]{64}', value):
            result[key] = value
        elif key == 'tool_call_id' and isinstance(value, str):
            result['tool_call_id_hash'] = hashlib.sha256(value.encode()).hexdigest()[:16]
        elif key == 'tool_call_id_hash' and isinstance(value, str) and re.fullmatch(r'[0-9a-f]{16}', value):
            result[key] = value
        elif key in _COUNTS and type(value) is int and value >= 0:
            result[key] = value
        elif key == 'usage' and isinstance(value, dict):
            result[key] = {k: v for k, v in value.items() if k in _USAGE and type(v) is int and v >= 0}
        elif key == 'stage_usage' and isinstance(value, dict):
            result[key] = {stage: {**safe_fields({'usage': data}).get('usage', {}),
                **safe_fields({'elapsed_seconds': data.get('elapsed_seconds')})}
                for stage, data in value.items() if stage in
                {'understanding', 'classification', 'expansion', 'sufficiency', 'retrieval'} and isinstance(data, dict)}
        elif key in {'prior_pending', 'useful'} and type(value) is bool:
            result[key] = value
        elif key == 'elapsed_seconds' and type(value) in (int, float) and math.isfinite(value) and value >= 0:
            result[key] = round(value, 3)
    return result


class WorkflowFormatter(logging.Formatter):
    """不渲染消息模板、异常或堆栈，重复投影防止调用方绕过白名单。"""
    def format(self, record):
        """输出可直接采集的单行JSON，禁止追加任意异常文本。"""
        return json.dumps(safe_fields(getattr(record, 'workflow', {})), ensure_ascii=False, separators=(',', ':'))


def configure_workflow_logging():
    """只配置自己拥有的INFO处理器，不改根日志、外部捕获器及既有协议WARNING。"""
    if _console_handler not in logger.handlers:
        logger.addHandler(_console_handler)
    _console_handler.stream = sys.stderr
    _console_handler.setFormatter(WorkflowFormatter())
    logger.setLevel(logging.INFO)
    logger.disabled = False
    logger.propagate = False


def log_audit(event, **metadata):
    """所有审计入口先裁剪，避免其他处理器接触不可信文本。"""
    logger.info(event, extra={'workflow': safe_fields({'event': event, **metadata})})


def log_lifecycle(prepared, phase, **metadata):
    """运行边界只记录本轮SQL身份、已观察计数及受控状态。"""
    log_audit('workflow_lifecycle', conversation_id=prepared.conversation_id,
        user_message_id=str(prepared.user_message_id), phase=phase, **prepared.audit, **metadata)


def log_terminal(prepared, outcome, **metadata):
    """每轮最多一个终态，释放和取消重复进入也不会产生重复结果。"""
    if not prepared.terminal_logged:
        prepared.terminal_logged = True
        log_lifecycle(prepared, 'terminal', outcome=outcome, **metadata)
