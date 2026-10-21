"""只读原轮完成根的展示元数据，不运行图、检索、业务或摘要。"""
from copy import deepcopy
from contextlib import aclosing
import json

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from app.schemas.conversation import MessagePage
from app.workflow.persistence import completed_history_roots


_ACTION_LABELS = {'handoff': '转人工', 'create_ticket': '建工单'}


def _trace_status(trace, state):
    if trace.get('status') in ('success', 'error'):
        return trace['status']
    # Only old Workflow producers omitted status. Require their actual paired
    # receipt inside this completed turn, never infer completion from a request.
    if ('status' in trace or trace.get('origin') != 'workflow' or not isinstance(trace.get('node'), str)
            or (trace.get('node'), trace.get('name')) not in {
                ('load_order', 'query_order'), ('retrieve_knowledge', 'query_faq'),
                ('retrieve_policies', 'query_faq')}):
        return None
    messages = state.get('messages')
    if not isinstance(messages, list):
        return None
    start = next((i for i, message in enumerate(messages) if isinstance(message, HumanMessage)
                  and message.id == state.get('user_message_id')), None)
    if start is None:
        return None
    for request, result in zip(messages[start+1:], messages[start+2:]):
        if isinstance(request, HumanMessage) or isinstance(result, HumanMessage):
            break
        if (isinstance(request, AIMessage) and len(request.tool_calls) == 1
                and request.tool_calls[0].get('id') == trace['tool_call_id']
                and request.tool_calls[0].get('name') == trace['name']
                and isinstance(result, ToolMessage) and result.tool_call_id == trace['tool_call_id']):
            try:
                payload = json.loads(result.content)
            except (TypeError, ValueError):
                return None
            if not isinstance(payload, dict):
                return None
            return 'error' if result.status == 'error' or 'error' in payload else 'success'
    return None


def _citations(values):
    """与原公开SSE一样只允许已保存的引用字段。坏来源不生成可点引用。"""
    if not isinstance(values, list) or len(values) > 10:
        return []
    seen = set()
    for item in values:
        if (not isinstance(item, dict) or set(item) != {'n', 'chunk_id', 'section_path', 'question', 'answer'}
                or type(item['n']) is not int or not 1 <= item['n'] <= 10 or item['n'] in seen
                or any(not isinstance(item[key], str) or not item[key] for key in ('chunk_id', 'question', 'answer'))
                or (item['section_path'] is not None and not isinstance(item['section_path'], str))):
            return []
        seen.add(item['n'])
    return deepcopy(values)


class HistoryReader:
    def __init__(self, checkpointer, repository):
        self.checkpointer, self.repository = checkpointer, repository

    async def decorate(self, page: MessagePage) -> MessagePage:
        """按final SQL ID建一次原根映射；SQL正文不匹配和缺源均保留裸原文。"""
        messages = {row.id: row for row in page.messages if row.role == 'assistant' and row.tool_calls is None}
        metadata = {}
        if self.checkpointer is not None and messages:
            async with aclosing(completed_history_roots(self.checkpointer, page.conversation_id)) as roots:
                return await self._decorate_roots(page, messages, roots)
        return page.model_copy(update={'turn_metadata': metadata}, deep=True)

    async def _decorate_roots(self, page, messages, roots):
        """持有迭代器时不调用其他saver接口；异常/取消由aclosing确定性释放游标。"""
        metadata = {}
        async for checkpoint_id, state in roots:
            final_id = state.get('final_message_id')
            if not isinstance(final_id, str) or final_id in metadata:
                continue
            row = messages.get(final_id)
            if row is None or not isinstance(row.content, str) or row.content != state.get('final_answer'):
                continue
            locator = {'assistant_message_id': final_id, 'checkpoint_id': checkpoint_id}
            item = {'turn_status': 'completed', 'citations': _citations(state.get('citations', [])),
                    'tool_badges': []}
            if isinstance(state.get('raw_question'), str) and state['raw_question'].strip():
                item['feedback'] = dict(locator)
            # 只提供既有接口所需定位；许可仍由后续业务接口重新核验。
            actions = state.get('suggested_actions', [])
            if isinstance(actions, list):
                options = [{'action': action, 'label': _ACTION_LABELS[action]} for action in _ACTION_LABELS if action in actions]
                if options:
                    item['actions'] = {**locator, 'options': options}
            offer = state.get('refund_offer')
            if (isinstance(offer, dict) and offer.get('assistant_message_id') == final_id
                    and isinstance(offer.get('offer_id'), str)):
                item['refund_offer'] = {**locator, 'offer_id': offer['offer_id']}
            traces = state.get('tool_trace')
            for trace in traces if isinstance(traces, list) else []:
                if (isinstance(trace, dict) and isinstance(trace.get('name'), str)
                        and isinstance(trace.get('tool_call_id'), str)):
                    status = _trace_status(trace, state)
                    if status is not None:
                        item['tool_badges'].append({key: trace[key] for key in ('name', 'tool_call_id')} | {'status': status})
            metadata[final_id] = item
        return page.model_copy(update={'turn_metadata': metadata}, deep=True)
