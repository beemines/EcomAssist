"""Privacy cleaning must preserve the literal requests used for multilabel truth."""

import hashlib

import pytest

from app.topics.cleaning import clean_question


def test_identifiers_and_address_removed_without_losing_size_price_or_negation():
    raw = '手机号13800138000，订单号1001，地址：上海市浦东新区测试路88号301室，XL买大了，39.9元，不要退，只想修。'
    row = clean_question(raw, sample_id='authored-1')
    assert all(secret not in row.text for secret in ('13800138000', '1001', '上海市', '88号', '301室'))
    assert all(meaning in row.text for meaning in ('XL', '39.9元', '不要退', '只想修'))
    assert row.input_hash == hashlib.sha256(raw.encode('utf-8')).hexdigest()
    assert {'phone_redacted', 'order_id_redacted', 'address_redacted'} <= set(row.edits)
    assert not row.quarantine_reasons


def test_email_identity_card_and_tracking_number_removed():
    row = clean_question('身份证110101199001011234，邮箱demo@example.test，运单号SF123456789012在哪里？', sample_id='authored-2')
    assert all(secret not in row.text for secret in ('110101199001011234', 'demo@', 'SF123456789012'))
    assert '在哪里' in row.text


def test_ambiguous_name_and_unmarked_address_quarantined():
    for raw in ('我叫张三想维修，不要退', '请送上海市测试区测试路88号，运费多少'):
        assert clean_question(raw, sample_id='authored-3').quarantine_reasons


def test_no_provenance_guessing_or_keyword_deletion():
    row = clean_question('验收运费怎么算，1000元订单能包邮吗？', sample_id='authored-4')
    assert '验收' in row.text and '1000元' in row.text
    assert not row.quarantine_reasons
    assert not hasattr(row, 'origin')


def test_format_and_narrow_typo_corrections_are_auditable():
    row = clean_question('  ＸＬ\t大了，发漂怎么开？\r\n', sample_id='authored-5')
    assert row.text == 'XL 大了,发票怎么开?'
    assert {'unicode_normalized', 'whitespace_normalized', 'typo_fapiao'} <= set(row.edits)


def test_excess_length_and_empty_text_are_not_silently_truncated():
    raw = '退货需要多少运费' * 100
    row = clean_question(raw, sample_id='authored-6')
    assert row.text == raw and 'text_too_long' in row.quarantine_reasons
    assert 'empty_text' in clean_question('  ', sample_id='authored-7').quarantine_reasons


def test_extreme_raw_text_is_isolated_before_privacy_pattern_matching():
    raw = 'A' * 5000
    row = clean_question(raw, sample_id='authored-long')
    assert row.text == raw
    assert {'text_too_long', 'privacy_review_required'} <= set(row.quarantine_reasons)


@pytest.mark.parametrize('raw', [None, 10, True, ['物流']])
def test_nontext_is_rejected(raw):
    with pytest.raises(ValueError):
        clean_question(raw, sample_id='authored-8')


@pytest.mark.parametrize('kwargs', [dict(from_id=0, to_id=None, limit=1),
    dict(from_id=True, to_id=None, limit=1), dict(from_id=1, to_id=0, limit=1),
    dict(from_id=1, to_id=None, limit=0), dict(from_id=1, to_id=None, limit=101)])
async def test_preview_rejects_invalid_range_before_opening_database(kwargs):
    from app.topics.snapshot import preview_pool
    with pytest.raises(ValueError):
        await preview_pool(None, **kwargs)
