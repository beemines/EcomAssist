"""Four explainable signals; fit on calibration labels, never on held-out labels."""
import math
import re
import unicodedata
from typing import Literal
from pydantic import model_validator
from app.quality.evidence_confidence import (
    ConfidenceRule,EvidenceDecision,canonical_hash,selected_rankings,
)

REFERENCE_ALGORITHM='ch09-four-signal-zero-allow-v3'
WEIGHTS=(5,2,2,1)
_FILLER=re.compile(r'请问|麻烦|一下|这个|那个|可以|能不能|是否|多少|怎么|如何|什么|有没有|的话|我的|你们|我们|我想|知道|告诉我')


class ReferenceConfidenceRule(ConfidenceRule):
    algorithm: Literal['ch09-four-signal-zero-allow-v2','ch09-four-signal-zero-allow-v3']
    weights: tuple[int,int,int,int]

    @model_validator(mode='after')
    def valid_parameters(self):
        if self.weights!=WEIGHTS or not 0<=self.score_floor<=1:
            raise ValueError('Invalid frozen four-signal parameters')
        return self


def reference_rule(base,*,threshold,score_floor):
    raw=base.model_dump(mode='json',exclude={'rule_version'})
    raw.update(algorithm=REFERENCE_ALGORITHM,weights=list(WEIGHTS),
        threshold=threshold,score_floor=score_floor)
    raw['rule_version']=canonical_hash(raw)
    return ReferenceConfidenceRule.model_validate_json(__import__('json').dumps(raw))


def _normalize(value):
    return re.sub(r'\s+','',unicodedata.normalize('NFKC',value).casefold())


_UNITS={alias:canonical for canonical,aliases in (
    ('kg',('kg','公斤','千克')),('g',('g','克')),('l',('l','升')),('ml',('ml','毫升')),
    ('w',('w','瓦')),('v',('v','伏')),('mm',('mm','毫米')),('cm',('cm','厘米')),('m',('m','米')),
    ('元',('元',)),('天',('天',)),('个月',('个月',)),('年',('年',)),
    ('小时',('小时',)),('分钟',('分钟',)),('%',('%',))) for alias in aliases}
_QUANTITY=re.compile(r'(?<![a-z0-9.])(\d+(?:\.\d+)?)('+ '|'.join(
    re.escape(unit) for unit in sorted(_UNITS,key=len,reverse=True))+r')(?![a-z])')


def _quantities(value):
    result=set()
    for number,unit in _QUANTITY.findall(value):
        whole,_,fraction=number.partition('.')
        whole=whole.lstrip('0') or '0';fraction=fraction.rstrip('0')
        result.add(whole+('.'+fraction if fraction else '')+_UNITS[unit])
    return result


def clause_features(question,matches,*,legacy=False):
    if not isinstance(question,str) or not question.strip():
        raise ValueError('Four-signal confidence requires the actual question')
    query=_normalize(question)
    body=_normalize('\n'.join(str(row.get(key) or '') for row in matches
        for key in ('question','answer','content')))
    pattern=r'[a-z][a-z0-9_-]*\d[a-z0-9_-]*'
    if legacy: pattern+=r'|\d+(?:\.\d+)?(?:元|天|个月|年|瓦|毫升|小时|分钟|%)'
    anchors=sorted(set(re.findall(pattern,query)))
    # Substring matching must not confuse XM-A1 with XM-A17 or 99 with 199.
    missing=[anchor for anchor in anchors if re.search(r'(?<![a-z0-9])'+re.escape(anchor)+r'(?![a-z0-9])',body) is None]
    if not legacy:
        quantities=_quantities(query)
        anchors+=sorted(quantities)
        missing+=sorted(quantities-_quantities(body))
    terms=set()
    for token in re.findall(r'[\u4e00-\u9fff]+',_FILLER.sub(' ',query)):
        terms.update(token[i:i+2] for i in range(len(token)-1))
    coverage=sum(term in body for term in terms)/len(terms) if terms else 1.
    return {'clause_signal':0. if missing else coverage,'anchors_complete':not missing,
        'anchor_count':len(anchors),'missing_anchors':missing,
        'clause_terms':len(terms),'matched_terms':sum(term in body for term in terms)}


def reference_features(scores,*,question,matches,score_floor,top_k,legacy=False):
    scores=sorted(scores,reverse=True)
    if any(not math.isfinite(score) or not 0<=score<=1 for score in scores):
        raise ValueError('Four-signal rule requires bounded authoritative rerank scores')
    has_top2=len(scores)>=2
    top1=scores[0] if scores else 0.
    gap=top1-scores[1] if has_top2 else 0.
    count=sum(score>score_floor for score in scores)
    return {'top1':top1,'top1_signal':top1,'gap':gap,'gap_signal':gap,
        'has_top2':has_top2,'selected_count':len(scores),'effective_count':count,
        'count_ratio':count/top_k,**clause_features(question,matches,legacy=legacy)}


def reference_score(features):
    return round((5*features['top1_signal']+2*features['count_ratio']+
        2*features['gap_signal']+features['clause_signal'])/10,12)


def evaluate_reference(payload,rule,*,question,top_k):
    ranked=selected_rankings(payload)
    if len(ranked)>top_k: raise ValueError('Too many selected chunks')
    features=reference_features([score for _,score in ranked],question=question,
        matches=payload['matches'],score_floor=rule.score_floor,top_k=top_k,
        legacy=rule.algorithm=='ch09-four-signal-zero-allow-v2')
    score=reference_score(features) if ranked else 0.
    useful=bool(ranked) and features['anchors_complete'] and score>rule.threshold
    return EvidenceDecision(useful=useful,evidence_confidence=score,features=features,
        reason='calibrated_evidence_pass' if useful else 'calibrated_evidence_insufficient',
        rule_version=rule.rule_version)


def fit_reference_rule(samples,split,texts):
    from app.quality.calibration import CalibrationSplit
    split=CalibrationSplit.model_validate_json(split.model_dump_json())
    from app.quality.calibration import _matrix
    from app.quality.confidence_report import distribution,rate_summary
    samples=sorted(samples,key=lambda item:item.eval_id)
    by_id={row.eval_id:row for row in samples}
    expected=set(split.calibration_ids)|set(split.held_out_ids)
    if len(by_id)!=len(samples) or set(by_id)!=expected or set(texts)!=expected:
        raise ValueError('Calibration identities mismatch')
    source=samples[0].source
    if source.dataset_fingerprint!=split.dataset_fingerprint or any(row.source!=source for row in samples):
        raise ValueError('Calibration source mismatch')
    training=[by_id[key] for key in split.calibration_ids]
    heldout=[by_id[key] for key in split.held_out_ids]
    if {row.sufficient for row in training}!={False,True}:
        raise ValueError('Calibration needs both classes')
    observed=sorted(item.score for row in training for item in row.rankings)
    if not observed: raise ValueError('Calibration has no scores')
    floors=sorted({observed[int((len(observed)-1)*p)] for p in (0,.25,.5,.75,1)})
    def features(row,floor):
        value=texts[row.eval_id]
        if len(value['matches'])!=len(row.rankings): raise ValueError('Prompt evidence identity mismatch')
        return reference_features([item.score for item in row.rankings],question=value['question'],
            matches=value['matches'],score_floor=floor,top_k=source.top_k)
    def matrix(rows,items,threshold):
        return _matrix([row.sufficient for row in rows],
            [bool(row.rankings) and item['anchors_complete'] and reference_score(item)>threshold
                for row,item in zip(rows,items)])[0]
    best=None
    for floor in floors:
        items=[features(row,floor) for row in training]
        values=sorted({reference_score(item) for item in items}|{0.,1.})
        thresholds=sorted(set(values)|{(a+b)/2 for a,b in zip(values,values[1:])})
        for threshold in thresholds:
            result=matrix(training,items,threshold)
            order=(result['false_allow'],result['false_refusal'],-result['f1'],-threshold,floor)
            if best is None or order<best[0]: best=(order,floor,threshold)
    _,floor,threshold=best
    data=dict(schema_version=1,algorithm=REFERENCE_ALGORITHM,source=source.model_dump(mode='json'),
        split_fingerprint=split.fingerprint,calibration_fingerprint=canonical_hash([
            {'sample':row.model_dump(mode='json'),'input':texts[row.eval_id]} for row in training]),
        calibration_ids=list(split.calibration_ids),top1_distribution=[0.,1.],gap_distribution=[0.,1.],
        score_floor=floor,weights=list(WEIGHTS),threshold=threshold)
    selected=ReferenceConfidenceRule.model_validate_json(__import__('json').dumps({**data,'rule_version':canonical_hash(data)}))
    train_items=[features(row,floor) for row in training]
    held_items=[features(row,floor) for row in heldout]
    train_matrix=matrix(training,train_items,threshold); held_matrix=matrix(heldout,held_items,threshold)
    records=[{'eval_id':row.eval_id,'sufficient':row.sufficient,'side':side,
        'features':item,'evidence_confidence':reference_score(item)}
        for side,rows,items in (('calibration',training,train_items),('held_out',heldout,held_items))
        for row,item in zip(rows,items)]
    return {'schema_version':1,'rule':selected.model_dump(mode='json'),
        'selection_policy':'zero_false_allow_then_max_answerable_pass',
        'signal_weights':dict(zip(('top1','count','gap','clause'),(.5,.2,.2,.1))),
        'clause_algorithm':'lexical-anchors-v1','calibration':{**train_matrix,**rate_summary(train_matrix)},
        'held_out':{**held_matrix,**rate_summary(held_matrix)},'samples':records,
        'distributions':{side:{label:distribution([row['evidence_confidence'] for row in records
            if row['side']==side and row['sufficient']==flag]) for label,flag in (('answerable',True),('unanswerable',False))}
            for side in ('calibration','held_out')},
        'threshold_scan':[{'threshold':value,**rate_summary(matrix(training,train_items,value))}
            for value in sorted({round(.05+i*.01,2) for i in range(91)}|{threshold})]}
