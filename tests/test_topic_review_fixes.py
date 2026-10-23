"""Concrete privacy and short-family defects from the final independent review."""
import pytest
from app.topics.cleaning import clean_question
from app.topics.teacher import _private_text_safe
from app.topics.grouping import group_samples
from app.topics.types import LabelledSample


@pytest.mark.parametrize('raw',[
    '我是何小明，运单号SF123456789在哪里',
    '我是欧阳小明,发票能开吗',
    '我姓何叫小明,包裹到哪了',
])
def test_explicit_name_cues_are_isolated_without_a_surname_allowlist(raw):
    result=clean_question(raw,sample_id='review-name')
    assert 'name_review_required' in result.quarantine_reasons
    assert not _private_text_safe(raw,'review-name')


def test_closed_role_description_is_not_mistaken_for_an_actual_name():
    raw='我是会员,积分怎么用'
    result=clean_question(raw,sample_id='review-role')
    assert result.text==raw and not result.quarantine_reasons


@pytest.mark.parametrize('raw',[
    '地址改到北京市海淀区中关村大街1号发票能开吗',
    '请寄到上海市测试路88号XL码39.9元',
    '地址北京市测试路1号积分怎么用',
])
def test_address_with_undelimited_suffix_cannot_silently_become_safe_teacher_text(raw):
    result=clean_question(raw,sample_id='review-address')
    assert 'ambiguous_address_clause' in result.quarantine_reasons
    assert 'address_redacted' in result.edits
    assert not any(secret in result.text for secret in ('北京市','上海市','88号','1号'))


def row(identifier,text,*,pilot=False):
    return LabelledSample(id=identifier,text=text,labels=['会员积分'],origin='synthetic',
        group_id='group-'+identifier,source_question_ids=[],pilot=pilot)


def test_short_near_duplicate_of_pilot_cannot_become_a_distinct_split_family():
    result=group_samples([row('pilot','积分快过期了怎么用掉?',pilot=True),row('short','积分快过期了怎么用')])
    assert len(result.groups)==1
    assert {r.id for r in result.samples}=={'pilot','short'}
    assert len({r.group_id for r in result.samples})==1


def test_short_near_match_does_not_erase_a_negation_or_merge_opposite_requests():
    texts=['这个商品我就不要退货','这个商品我就要退货']
    result=group_samples([row(str(i),t) for i,t in enumerate(texts)])
    assert len(result.groups)==2
    assert {r.text for r in result.samples}==set(texts)
