import pytest


def test_known_tariff_splits_cached_input_and_records_currency_and_source():
    from app.observability.pricing import estimate_cost
    result=estimate_cost('glm-5.3-flash',{'input':800000,'input_cached_tokens':200000,'output':1000000})
    assert result['cost_cny']==pytest.approx(3.486)
    assert result['cost_usd']==pytest.approx(3.486*.14968462882212532)
    assert result['currency']=='CNY' and result['kind']=='tariff_estimate'
    assert result['fx_date']=='2026-10-19'


@pytest.mark.parametrize('model,usage', [('unknown',{'input':10,'output':2}),
    ('glm-5.3-flash',{'total':10}),('glm-5.3-flash',{'input':-1,'output':2}),
    ('glm-5.3-flash',{'input':True,'output':2}),('glm-5.3-flash',{'input':2,'output':True}),
    ('glm-5.3-flash',{'input':2,'output':'bad'})])
def test_unknown_or_invalid_usage_is_never_a_zero_cost(model,usage):
    from app.observability.pricing import estimate_cost
    assert estimate_cost(model,usage) is None


def test_usage_costs_count_generations_once_and_keep_currencies_separate():
    from app.observability.intent_usage import summarize_intent_usage
    from tests.test_intent_usage import root,generation
    item=generation('g',{'input':1000000,'output':1000000},model='glm-5.3-flash',
        cost_details={'total':.25})
    [row]=summarize_intent_usage([root()],[item,item,
        {'id':'parent','trace_id':'t1','type':'SPAN','cost_details':{'total':100}}])
    assert row['currency_cost']==.25 and row['cost_currency']=='USD'
    assert row['estimated_cost_cny']==pytest.approx(3.6)
    assert row['average_tokens']==2000000 and row['model_calls']==1


def test_missing_price_costs_are_distinguished_from_a_known_zero():
    from app.observability.intent_usage import summarize_intent_usage
    from tests.test_intent_usage import root,generation
    [row]=summarize_intent_usage([root()],[generation('x',{'total':4})])
    assert row['currency_cost'] is None and row['unknown_cost_calls']==1
