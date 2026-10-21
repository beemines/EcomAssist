"""Local, auditable privacy masking; uncertain identity spans never go to a teacher."""

import hashlib
import re
import unicodedata

from pydantic import Field, field_validator

from app.topics.types import StrictRecord


CLEANING_VERSION = 'ch10-clean-v1'


class CleanQuestion(StrictRecord):
    sample_id: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    text: str
    input_hash: str = Field(pattern=r'^[0-9a-f]{64}$')
    edits: tuple[str, ...]
    quarantine_reasons: tuple[str, ...]

    @field_validator('edits', 'quarantine_reasons', mode='before')
    @classmethod
    def code_array(cls, value):
        if type(value) not in (list, tuple) or any(type(item) is not str for item in value):
            raise ValueError('Cleaning codes must be a JSON array or tuple of strings')
        return tuple(value)


def clean_question(raw: str, *, sample_id: str) -> CleanQuestion:
    if type(raw) is not str or type(sample_id) is not str or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}', sample_id):
        raise ValueError('Expected text and an explicit safe sample ID')
    input_hash = hashlib.sha256(raw.encode('utf-8')).hexdigest()
    if len(raw) > 4096:
        return CleanQuestion(sample_id=sample_id, text=raw, input_hash=input_hash,
            edits=('overlong_not_processed',), quarantine_reasons=('text_too_long', 'privacy_review_required'))
    edits, quarantine = [], []
    value = unicodedata.normalize('NFKC', raw)
    if value != raw:
        edits.append('unicode_normalized')
    normalized = re.sub(r'\s+', ' ', value).strip()
    if normalized != value:
        edits.append('whitespace_normalized')
    value = normalized

    def mask(pattern, replacement, code, *, flags=0):
        nonlocal value
        value, count = re.subn(pattern, replacement, value, flags=flags)
        if count:
            edits.append(code)

    mask(r'(?<!\d)\d{17}[0-9Xx](?!\d)', '[证件号]', 'identity_redacted')
    mask(r'(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)', '[手机号]', 'phone_redacted')
    mask(r'(?<![A-Z0-9._%+-])[A-Z0-9._%+-]{1,64}@[A-Z0-9.-]{1,253}\.[A-Z]{2,24}',
         '[邮箱]', 'email_redacted', flags=re.I)
    mask(r'((?:订单|运单|快递单|物流单)(?:号|编号)?\s*[:：]?\s*)[A-Z0-9][A-Z0-9_-]{3,63}',
         r'\1[订单号]', 'order_id_redacted', flags=re.I)

    # A labelled address clause ends at punctuation. If it also contains requests,
    # quarantine it rather than teaching a sentence whose meaning may have changed.
    address = re.compile(r'((?:收货)?地址\s*[:：]?|寄到|送到|改到|住在)\s*([^，,;；。\n]{2,100})')
    def redact_address(match):
        detail = match.group(2)
        if not re.search(r'省|市|区|县|路|街|镇|号|栋|楼|室', detail):
            return match.group(0)
        if re.search(r'不要|不想|只想|退货|换货|维修|运费', detail):
            quarantine.append('ambiguous_address_clause')
        edits.append('address_redacted')
        return match.group(1) + '[详细地址]'
    value = address.sub(redact_address, value)

    if re.search(r'我叫|姓名|收件人|联系人|我是[赵钱孙李周吴郑王张刘陈杨黄]', value):
        quarantine.append('name_review_required')
        mask(r'((?:我叫|姓名|收件人|联系人)\s*[:：]?\s*)[\u4e00-\u9fff]{2,4}(?=[，,。；; ]|$)',
             r'\1[姓名]', 'name_redacted')
    if re.search(r'[\u4e00-\u9fff]{2,30}(?:路|街|巷)\s*\d+\s*号', value):
        quarantine.append('unlabelled_address_review_required')
    # Bare long numbers might be account/tracking IDs. Preserve amounts and units.
    if re.search(r'(?<![\d.])\d{8,24}(?![\d.元块厘米码天年个]|\s*(?:元|块|厘米|cm|mm))', value, flags=re.I):
        quarantine.append('untyped_identifier_review_required')
    if '发漂' in value:
        value = value.replace('发漂', '发票')
        edits.append('typo_fapiao')
    if len(value) > 512:
        quarantine.append('text_too_long')
    if not value:
        quarantine.append('empty_text')
    return CleanQuestion(sample_id=sample_id, text=value, input_hash=input_hash,
        edits=tuple(dict.fromkeys(edits)), quarantine_reasons=tuple(dict.fromkeys(quarantine)))
