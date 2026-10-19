"""从完整用户轮次及配对读取结果提取订单锚点，拒绝理解模型制造实体。"""
import json
import re
from dataclasses import dataclass

from langchain_core.messages import AIMessage, BaseMessage, ToolMessage

from app.core.extraction import invalid_output
from app.core.tool_history import completed_turns
from app.repositories.records import MessageRecord, record_from_message


_ORDER = re.compile(r'(?:(?:订单(?:编号|号码|号)?|单号)\s*(?:为|是)?\s*[:：#]?\s*)([A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*)(?![A-Za-z0-9_-])')
_COORDINATED_ORDER = re.compile(r'\s*(?:和|及|与|或|、|/|，|,)\s*(?:(?:订单(?:编号|号码|号)?|单号)\s*[:：#]?\s*)?([A-Za-z0-9]+(?:[-_][A-Za-z0-9]+)*)(?![A-Za-z0-9_-])')
_COMPACT_ORDER = re.compile(r'^\s*(?:(?:请|帮我|麻烦(?:您|你)?)?\s*(?:查询|查一下|查看|查)\s*)?(\d{4,20})\s*(?:的)?(?:物流|订单|退款|退货|售后)')
_MODEL = re.compile(r'(?<![A-Za-z0-9_-])[A-Za-z][A-Za-z0-9]*(?:[-_][A-Za-z0-9]+)+(?![A-Za-z0-9_-])')
_QUANTITY = re.compile(r'\d+(?:\.\d+)?\s*(?:元|天|小时|个月|年|毫升|升|公斤|千克|克)')
_DATE = re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}')


def completed_history(history: list[BaseMessage]) -> list[list[BaseMessage]]:
    """复用 SQL 回放校验，只保留成对工具与最终助手答复俱全的轮次。"""
    rows = []
    for index, message in enumerate(history):
        try:
            rows.append(record_from_message(message, identifier=index))
        except (ValueError, TypeError, KeyError, RecursionError):
            # 无效消息重置当前组，不能跳过它后把残缺工具链拼成完整轮次。
            rows.append(MessageRecord(index, 'user', None, None, None))
    return completed_turns(rows)


def explicit_order_ids(question: str) -> set[str]:
    """明确前缀或句首编号紧接业务主题；型号/金额/日期/手机号不是订单。"""
    identifiers = set()
    for match in _ORDER.finditer(question):
        identifiers.add(match.group(1))
        end = match.end()
        while following := _COORDINATED_ORDER.match(question, end):
            identifiers.add(following.group(1))
            end = following.end()
    compact = _COMPACT_ORDER.match(question)
    if compact and not _PHONE.fullmatch(compact.group(1)):
        identifiers.add(compact.group(1))
    return identifiers


def _order_facts(turn: list[BaseMessage]) -> list[dict]:
    """只信配对订单/物流读取的成功对象，申请与结果的订单身份必须一致。"""
    facts = []
    for request, result in zip(turn[1:-1:2], turn[2:-1:2]):
        if not isinstance(request, AIMessage) or not isinstance(result, ToolMessage):
            continue
        call = request.tool_calls[0]
        if call['name'] not in ('query_order', 'query_logistics'):
            continue
        try:
            payload = json.loads(result.content)
        except (ValueError, TypeError):
            continue
        if (isinstance(payload, dict) and 'error' not in payload and payload.get('status') != 'error'
                and payload.get('success') is not False
                and isinstance(payload.get('order_id'), str)
                and payload['order_id'] == call['args'].get('order_id')):
            facts.append(payload)
    return facts


def _turn_orders(turn: list[BaseMessage]) -> set[str]:
    """合并本轮用户明确表达与成功读取对象，不读取助手正文中的编号。"""
    return explicit_order_ids(turn[0].content) | {fact['order_id'] for fact in _order_facts(turn)}


def trusted_order_ids(history: list[BaseMessage]) -> set[str]:
    """返回本会话已完成历史的所有可追溯订单标识，不替用户选择。"""
    return {identifier for turn in completed_history(history) for identifier in _turn_orders(turn)}


def validate_resolved_entities(raw_question: str, resolved_question: str, history: list[BaseMessage]) -> None:
    """拒绝新造订单、歧义选单、旧单覆盖及无来源型号、日期和数量。"""
    turns = completed_history(history)
    raw_ids, resolved_ids = explicit_order_ids(raw_question), explicit_order_ids(resolved_question)
    latest = next((ids for turn in reversed(turns) if (ids := _turn_orders(turn))), set())
    allowed = raw_ids if raw_ids else latest if len(latest) == 1 else set()
    if not resolved_ids <= allowed or (raw_ids and not raw_ids <= resolved_ids):
        raise invalid_output()
    source = [raw_question]
    for turn in turns:
        turn_ids = _turn_orders(turn)
        if not raw_ids and len(latest) > 1:
            continue
        if not turn_ids or turn_ids <= allowed:
            source.append(turn[0].content)
        for fact in _order_facts(turn):
            if fact['order_id'] in allowed:
                source.extend(str(fact[key]) for key in ('order_id', 'product_id', 'model', 'signed_at', 'as_of') if key in fact)
    source_text = '\n'.join(source)
    for pattern in (_MODEL, _QUANTITY, _DATE):
        if not set(pattern.findall(resolved_question)) <= set(pattern.findall(source_text)):
            raise invalid_output()


@dataclass(frozen=True)
class IdentitySource:
    """Only identities visible in this injected segment and proven by its SQL range."""
    from_msg_id: int
    summary_seq: int | None
    order_ids: frozenset[str]
    texts: tuple[str, ...]


def snapshot_provenance(snapshot, rows):
    from app.repositories.records import message_from_record
    rows = sorted(rows, key=lambda row: row.id)

    def source(first, last, visible, seq):
        original_rows = [row for row in rows if first <= row.id <= last]
        original = [message_from_record(row) for row in original_rows]
        turns = completed_history(original)
        # A cancelled turn's native user text is still a real user expression.
        users = [row.content for row in original_rows if row.role == 'user']
        trusted = list(users)
        facts = [fact for turn in turns for fact in _order_facts(turn)]
        trusted.extend(json.dumps(fact, ensure_ascii=False) for fact in facts)
        trusted_text = '\n'.join(trusted)
        trusted_orders = explicit_order_ids('\n'.join(users)) | {fact['order_id'] for fact in facts}
        # JSON order_id values are visible even without a Chinese "订单" prefix.
        orders = frozenset(identifier for identifier in trusted_orders
                           if identifier in visible and (seq is None or identifier in explicit_order_ids(visible)))
        tokens = tuple(value for pattern in (_MODEL, _QUANTITY, _DATE, _PHONE)
                       for value in pattern.findall(visible) if value in set(pattern.findall(trusted_text)))
        return IdentitySource(first, seq, orders, tokens)

    result = []
    for segment in snapshot.summaries:
        # A segment can cover several successive orders. Preserve SQL user-turn
        # positions inside its range; a single user naming two orders stays a set.
        starts = [row.id for row in rows if row.role == 'user'
                  and segment.from_msg_id <= row.id <= segment.upto_msg_id]
        for index, first in enumerate(starts):
            last = starts[index + 1] - 1 if index + 1 < len(starts) else segment.upto_msg_id
            result.append(source(first, last, segment.content, segment.seq))
    group = []
    for row in (*snapshot.layer2, *snapshot.layer1):
        if row.role == 'user' and group:
            result.append(source(int(group[0].id), int(group[-1].id),
                '\n'.join(item.content or '' for item in group), None))
            group = []
        group.append(row)
    if group:
        result.append(source(int(group[0].id), int(group[-1].id),
            '\n'.join(item.content or '' for item in group), None))
    return tuple(result)


_PHONE = re.compile(r'(?<!\d)1[3-9]\d{9}(?!\d)')


def validate_snapshot_entities(raw_question, resolved_question, snapshot, provenance):
    """Validate finite identity constraints, not arbitrary natural-language fidelity."""
    visible_seqs = {segment.seq for segment in snapshot.summaries}
    sources = [item for item in provenance if item.summary_seq is None or item.summary_seq in visible_seqs]
    groups = [item.order_ids for item in sources if item.order_ids]
    raw_ids, resolved_ids = explicit_order_ids(raw_question), explicit_order_ids(resolved_question)
    if '最开始' in raw_question or '最早' in raw_question or '第一单' in raw_question:
        referenced = groups[0] if groups else frozenset()
        # If the beginning was omitted, the earliest visible segment is not proof.
        if snapshot.omitted_summary_seqs:
            referenced = frozenset()
    elif '上一单' in raw_question:
        referenced = groups[-2] if len(groups) >= 2 else frozenset()
    else:
        referenced = groups[-1] if groups else frozenset()
    allowed = raw_ids or (referenced if len(referenced) == 1 else set())
    if not resolved_ids <= allowed or (raw_ids and not raw_ids <= resolved_ids):
        raise invalid_output()
    text = '\n'.join([raw_question, *(value for item in sources if not item.order_ids or item.order_ids <= allowed
                                    for value in item.texts)])
    for pattern in (_MODEL, _QUANTITY, _DATE, _PHONE):
        before, after = set(pattern.findall(raw_question)), set(pattern.findall(resolved_question))
        if (not after <= set(pattern.findall(text)) or not before <= after
                or pattern is _PHONE and before and after != before):
            raise invalid_output()
