"""Explicit standard-API tariff estimates; never present these as invoices."""
from decimal import Decimal
from urllib.parse import urlsplit

PRICE_VERSION='bigmodel-standard-2026-10-20-ecb-2026-10-19'
PRICE_SOURCE='https://docs.bigmodel.cn/cn/guide/start/pricing'
FX_SOURCE='https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'
USD_PER_CNY=Decimal('1.1225')/Decimal('7.4991')


def standard_bigmodel_endpoint(value):
    parsed=urlsplit(str(value))
    return parsed.scheme=='https' and parsed.hostname=='open.bigmodel.cn' and parsed.path.rstrip('/')=='/api/paas/v4'


def estimate_cost(model,usage):
    if model!='glm-5.3-flash' or not isinstance(usage,dict): return None
    counted=('input','output','input_cached_tokens','input_cache_read','output_reasoning',
        'output_reasoning_tokens','prompt_tokens','completion_tokens')
    if any(key in usage and (type(usage[key]) is not int or usage[key]<0) for key in counted): return None
    if 'input' in usage and 'output' in usage:
        uncached=usage['input']; cached=usage.get('input_cached_tokens',usage.get('input_cache_read',0))
        output=usage['output']+usage.get('output_reasoning',usage.get('output_reasoning_tokens',0))
    elif 'prompt_tokens' in usage and 'completion_tokens' in usage:
        details=usage.get('prompt_tokens_details') or {}
        if not isinstance(details,dict): return None
        cached=details.get('cached_tokens',0)
        if type(cached) is not int or cached<0: return None
        uncached=usage['prompt_tokens']-cached; output=usage['completion_tokens']
    else: return None
    if any(type(value) is not int or value<0 for value in (uncached,cached,output)): return None
    costs={'input':Decimal(uncached)*Decimal('.8')/1000000,
        'input_cached_tokens':Decimal(cached)*Decimal('.23')/1000000,
        'output':Decimal(output)*Decimal('2.8')/1000000}
    cny=sum(costs.values())
    return {'kind':'tariff_estimate','currency':'CNY','cost_cny':float(cny),
        'cost_usd':float(cny*USD_PER_CNY),
        'usd_details':{**{key:float(value*USD_PER_CNY) for key,value in costs.items()},'total':float(cny*USD_PER_CNY)},
        'price_version':PRICE_VERSION,'price_source':PRICE_SOURCE,
        'fx_date':'2026-10-19','fx_source':FX_SOURCE,'usd_per_cny':float(USD_PER_CNY)}
