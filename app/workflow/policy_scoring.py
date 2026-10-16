"""已绑定退款订单的政策评分视角，不改变用户问题或召回查询。"""
import re

from app.orders.types import OrderSnapshot


def refund_policy_question(question: str, order: OrderSnapshot) -> str:
    """仅替换唯一可信开头；否定、日期、金额和剩余诉求逐字保留。"""
    if order.signed_at is None or not order.category.strip():
        return question
    prefixes = {f'订单{order.order_id}的{identity}'
                for identity in (order.model, order.product_name) if identity.strip()}
    matches = [prefix for prefix in prefixes if question.startswith(prefix)]
    if len(matches) != 1:
        return question
    suffix = question[len(matches[0]):]
    # 中文产品名无通用词界，仅接受明确的问句/条件开头；未知版本后缀保留原问。
    starts_request = suffix.lstrip().startswith((
        '能退', '能否退', '可以退', '可否退', '不能退', '不可以退', '不是', '不支持',
        '是否', '是不是', '已经', '已签收', '未签收', '没有', '还能', '刚', '签收', '收到',
        '于', '在', '，', ',', '。', '？', '?', '；', ';', '：', ':'))
    # 比较、多订单、未知型号或边界碰撞不做政策概括；不删除任何后缀实体。
    if (not starts_request or '退' not in suffix or re.search(r'[A-Za-z]', suffix)
            or any(word in suffix for word in ('订单', '和', '与', '比', '或者', '还是', '以及', '另'))
            or any(identity and identity in suffix for identity in (order.model, order.product_name))):
        return question
    punctuation = '' if suffix.endswith(('？', '?', '。', '.', '！', '!', '；', ';')) else '？'
    scoring = (f'{order.category}于{order.signed_at.isoformat()}签收，{suffix}{punctuation}'
               '退货期限与适用条件是什么？')
    return scoring if len(scoring) <= 512 else question
