"""Compare only matching, complete evaluation populations."""
import json
import math

METRICS=('recall_at_5','recall_at_10','mrr_at_10','faithfulness','absent_refusal_rate')


def compare_runs(rows):
    def unpack(row):
        value=row.get('metrics') or {}
        return json.loads(value) if isinstance(value,str) else value
    completed=[row for row in rows if unpack(row).get('status') in ('completed','completed_with_errors')]
    if not completed: return {'latest_id':None,'previous_id':None,'metrics':{},'declined_count':0}
    latest=completed[0]; current=unpack(latest)
    previous=next((row for row in completed[1:] if unpack(row).get('config_fingerprint')==current.get('config_fingerprint')),None)
    old=unpack(previous) if previous else {}
    result={}
    for name in METRICS:
        now=(current.get('scores') or {}).get(name) or {}
        before=(old.get('scores') or {}).get(name) or {}
        numbers=all(type(value) in (int,float) and math.isfinite(value) for value in (now.get('value'),before.get('value')))
        comparable=bool(previous and numbers and now.get('valid_n',0)>0 and now.get('valid_n')==before.get('valid_n')
            and not current.get('errors') and not old.get('errors'))
        result[name]={'current':now.get('value'),'previous':before.get('value'),
            'valid_n':now.get('valid_n',0),'previous_valid_n':before.get('valid_n',0),
            'delta':now['value']-before['value'] if comparable else None,'comparable':comparable}
    return {'latest_id':latest.get('id'),'previous_id':previous.get('id') if previous else None,
        'metrics':result,'declined_count':sum(value['delta'] is not None and value['delta']<0 for value in result.values()),
        'partial':bool(current.get('errors') or old.get('errors'))}
