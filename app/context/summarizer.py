"""Strict summary protocol and conservative lexical checks, not a faithfulness proof."""
import asyncio
import json
import re

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from app.context.prompts import summary_messages
from app.context.summary_sources import summary_source_rows
from app.context.tokens import estimate_payload
from app.context.types import SummaryBatch
from app.core.llm import model_with_output_budget
from app.workflow.entities import explicit_order_ids


SUMMARY_OUTPUT_TOKENS = 512
_TOKEN = re.compile(r'(?<![A-Za-z0-9_-])[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*(?![A-Za-z0-9_-])')
_SOCIAL = re.compile(r'(?:(?:你好|您好|嗨|哈喽|谢谢(?:你|您)?|多谢|不客气|辛苦了|再见|拜拜|早上好|下午好|晚上好)[，,！!。.?？\s]*)+')
_NEGATIONS = (
    r'不想退款|不要退款|不退款', r'未找到|没找到|找不到', r'没收到|未收到|尚未收到',
    r'未解决|没解决|尚未解决', r'无法开机|不能开机', r'没有提交|未提交|尚未提交',
    r'尚未退款|未退款|还没退款|没有退款', r'取消.{0,4}表单|表单.{0,4}取消',
)
_POSITIVE_ACTIONS = (r'已(?:经)?退款(?:成功)?|退款(?:已)?成功|退款完成|已到账',
                     r'已(?:经)?提交(?:退款)?申请', r'已(?:经)?解决|恢复正常|修复成功',
                     r'已(?:经)?收到|已(?:经)?找到(?:包裹)?|已签收')
_STAGES = (r'已(?:经)?申请(?:退款)?', r'打开.{0,4}表单', r'待审核')
_REJECTED_ORDER = re.compile(r'不是\s*(?:订单)?\s*([A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*)')
_UNRESOLVED_ORDER = re.compile(r'待确认|未明确|没(?:有)?明确|未区分|没(?:有)?区分|不明确|不确定|哪(?:一)?单|哪个|那个|那(?:一)?单|其中一单')
_ORDER_DOUBT = re.compile(
    r'待确认|未明确|没(?:有)?明确|未区分|没(?:有)?区分|不明确|不确定|哪(?:一)?单|哪个'
    # Known tentative identity phrases must not clear a pending candidate scope.
    # Keep these tied to identity, rather than any uncertainty or polite "吧".
    # An order noun needs a following ID; shipping/state predicates are not identity.
    r'|(?:可能|也许|大概|好像|应该|或许|估计|似乎|我猜)\s*(?:就)?是\s*'
    r'(?:(?:订单(?:编号|号码|号)?\s*(?:为|是)?\s*[:：#]?\s*)?'
    r'[A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*'
    r'|最开始|最早|第一(?:个|笔)订单|上一(?:个|笔)?订单|上一单)'
    r'|(?:就是|是)\s*(?:订单)?\s*[A-Za-z0-9_-]+\s*吧')
_ORDER_SELECTION = re.compile(r'我选|选择|选定|就是|请查|查询|我要|我说的是|指的是|换成|换单|改查|改为')
_POSITIONAL_ORDER = re.compile(r'(?:最开始|最早)(?:的)?(?:那个|那笔)?订单|第一(?:个|笔)订单|上一(?:个|笔)?订单|上一单')
_ORDER_CLARIFICATION = re.compile(r'哪(?:一)?单|哪个订单|确认(?:一下)?(?:具体|要查的)?订单')


def _tokens(text):
    return {match.group() for match in _TOKEN.finditer(text)
            if any(char.isdigit() for char in match.group()) or '-' in match.group() or '_' in match.group()}


def _sources(batch):
    """User text plus adjacent, matched, successful tool objects; never assistant identities."""
    rows = summary_source_rows(batch)
    users = [row.content or '' for row in rows if row.role == 'user']
    facts = [json.loads(row.content) for row in rows if row.role == 'tool']
    return users, facts


def required_entities(batch: SummaryBatch) -> set[str]:
    users, facts = _sources(batch)
    identities = _tokens('\n'.join(users))
    for fact in facts:
        identities.update(str(fact[key]) for key in ('order_id', 'product_id', 'model', 'phone', 'phone_number')
                          if fact.get(key) is not None)
    return identities


def _asserted(text, pattern):
    """Only a narrow lexical action guard; arbitrary paraphrase still needs evaluation."""
    for clause in re.split(r'[。；;\n]|但是|但', text):
        for match in re.finditer(pattern, clause):
            if not re.search(r'未|没|不|尚无|无证据', clause[max(0,match.start()-18):match.start()]):
                return True
    return False


def _order_reference_unresolved(rows) -> bool:
    """Track lexical uncertainty/narrowing in source order, not general coreference.

    Assistant clarification can retain uncertainty but cannot select an identity.
    The count is only reference scope; this guard does not resolve a positional ID.
    """
    candidates, unresolved = 0, False
    for row in rows:
        text = row.content or ''
        if row.role == 'user':
            ids = explicit_order_ids(text)
            doubt = _ORDER_DOUBT.search(text)
            if ids:
                if not doubt and (not unresolved or _ORDER_SELECTION.search(text)):
                    candidates, unresolved = len(ids), False
                    if re.search(r'换成|换单|改查|改为', text):
                        candidates = 1
                else:
                    candidates = max(candidates, len(ids))
            if candidates > 1 and _UNRESOLVED_ORDER.search(text):
                unresolved = True
            if candidates and not doubt and _POSITIONAL_ORDER.search(text):
                candidates, unresolved = 1, False
        elif row.role == 'assistant' and candidates > 1 and _ORDER_CLARIFICATION.search(text):
            unresolved = True
    return unresolved


def validate_summary(content: str, batch: SummaryBatch) -> str:
    if not isinstance(content, str) or len(content) > 200 or (content and not content.strip()):
        raise ValueError('Summary must be text of at most 200 characters.')
    users, facts = _sources(batch)
    # Ordinary assistant offers of help are not new trusted business facts.
    # User business text and any tool activity still prevent empty coverage.
    social = (bool(users) and not facts and all(_SOCIAL.fullmatch(value.strip()) for value in users)
              and not any(row.role == 'tool' or row.tool_calls_json is not None for row in batch.source_rows))
    if social:
        if content:
            raise ValueError('Pure greetings must not invent summary facts.')
        return content
    if not content:
        raise ValueError('Business facts cannot have an empty summary.')
    if re.search(r'\[\s*\d+(?:\s*[,，-]\s*\d+)*\s*\]', content):
        raise ValueError('Historical summaries cannot carry policy citation numbers.')
    source = '\n'.join([*users, *(json.dumps(fact, ensure_ascii=False) for fact in facts)])
    if not _tokens(content) <= _tokens(source):
        raise ValueError('Summary entity has no trusted source.')
    if any(entity not in content for entity in required_entities(batch)):
        raise ValueError('Summary omitted a source entity; use smaller complete batches.')
    for pattern in _NEGATIONS:
        if re.search(pattern, source) and not re.search(pattern, content):
            raise ValueError('Summary dropped a source negation or action state.')
    for pattern in _STAGES:
        if re.search(pattern, source) and not re.search(pattern, content):
            raise ValueError('Summary omitted an explicit action stage.')
    for pattern in _POSITIVE_ACTIONS:
        if _asserted(content, pattern) and not _asserted(source, pattern):
            raise ValueError('Summary asserts an unsupported completed action.')
    orders = explicit_order_ids('\n'.join(users))
    if len(orders) > 1:
        if re.search(r'不是|换成|换单|改查|改为', '\n'.join(users)):
            if not re.search(r'不是|换成|换单|改查|改为', content):
                raise ValueError('Summary lost the explicit order switch.')
            if set(_REJECTED_ORDER.findall('\n'.join(users))) != set(_REJECTED_ORDER.findall(content)):
                raise ValueError('Summary changed which order was explicitly rejected.')
        if (_order_reference_unresolved(batch.source_rows)
                and not re.search(r'待确认|未明确|未区分|不明确|没有区分', content)):
            raise ValueError('Multiple orders must retain unresolved identity.')
    if facts and not re.search(r'当时|曾|历史', content):
        raise ValueError('Tool facts must be labelled as historical.')
    if any(fact.get('mock') is True for fact in facts) and not re.search(r'模拟|mock', content):
        raise ValueError('Mock facts must retain their simulation label.')
    return content


def summary_input_tokens(batch: SummaryBatch) -> int:
    return estimate_payload(summary_messages(batch))


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate summary JSON key.')
        result[key] = value
    return result


class SummaryGenerator:
    def __init__(self, model, settings, *, context_logger=None, observability=None):
        # Existing factory has zero SDK retries. Reject an externally misconfigured
        # client instead of shallow-copying a retry setting the owned SDK ignores.
        if isinstance(model, ChatOpenAI) and (model.max_retries != 0 or model.root_async_client.max_retries != 0):
            raise ValueError('Summary client must disable automatic retries.')
        self.model = model_with_output_budget(model, settings, SUMMARY_OUTPUT_TOKENS).bind(
            response_format={'type': 'json_object'})
        self.observability = observability
        if observability is not None and observability.handler is not None:
            self.model = self.model.with_config(callbacks=[observability.handler])
        self.window = settings.model_context_window
        self.safety = max(256, (self.window * 3 + 99) // 100)
        self.timeout = settings.llm_timeout_seconds
        self.context_logger = context_logger

    async def summarize(self, batch: SummaryBatch) -> str:
        if self.observability is None or self.observability.client is None:
            return await self._summarize(batch)
        from uuid import uuid4
        from app.observability.tracing import begin_execution, ExecutionIdentity
        identity = ExecutionIdentity(batch.conversation_id, str(batch.from_msg_id), uuid4().hex, 'summary')
        with begin_execution(self.observability, identity):
            return await self._summarize(batch)

    async def _summarize(self, batch: SummaryBatch) -> str:
        messages = summary_messages(batch)
        if estimate_payload(messages) + SUMMARY_OUTPUT_TOKENS + self.safety > self.window:
            raise ValueError('Summary window input + output + safety exceeded.')
        async with asyncio.timeout(self.timeout):
            if self.context_logger is not None:
                from app.context.types import ModelContextPacket
                import hashlib
                packet = ModelContextPacket(messages, (), estimate_payload(messages), SUMMARY_OUTPUT_TOKENS,
                    hashlib.sha256(messages[0].content.encode('utf-8')).hexdigest(), batch.source_hash)
                self.context_logger.model(packet, conversation_id=batch.conversation_id,
                    user_message_id=str(batch.from_msg_id), phase='summary', call_index=batch.expected_seq + 1)
            raw = await self.model.ainvoke(messages)
        if (not isinstance(raw, AIMessage) or raw.response_metadata.get('finish_reason') != 'stop'
                or raw.tool_calls or raw.invalid_tool_calls or raw.additional_kwargs.get('tool_calls')
                or raw.additional_kwargs.get('function_call') or raw.additional_kwargs.get('refusal')
                or not isinstance(raw.content, str)):
            raise ValueError('Summary requires normal stop, text and no tools or refusal.')
        parsed = json.loads(raw.content, object_pairs_hook=_unique_object)
        if not isinstance(parsed, dict) or set(parsed) != {'content'}:
            raise ValueError('Summary JSON must have exactly the content field.')
        return validate_summary(parsed['content'], batch)
