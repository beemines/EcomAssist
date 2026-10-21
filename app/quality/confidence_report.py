"""Readable statistics derived locally from frozen retrieval evidence."""
import math


def distribution(values):
    values=sorted(values)
    if any(type(value) not in (float,int) or not math.isfinite(value) for value in values):
        raise ValueError('Nonfinite confidence')
    def quantile(p):
        if not values: return None
        index=(len(values)-1)*p; left=int(index); fraction=index-left
        return values[left]*(1-fraction)+values[min(left+1,len(values)-1)]*fraction
    return {'n':len(values),'min':quantile(0),'p25':quantile(.25),'median':quantile(.5),'p75':quantile(.75),'max':quantile(1)}


def rate_summary(matrix):
    answerable=matrix['true_negative']+matrix['false_positive']
    unanswerable=matrix['true_positive']+matrix['false_negative']
    return {'answerable_n':answerable,'unanswerable_n':unanswerable,
        'answerable_pass_rate':matrix['true_negative']/answerable if answerable else None,
        'false_allow_rate':matrix['false_negative']/unanswerable if unanswerable else None}


def recompute_reference_report(root):
    """Reconstruct owned evidence by hashes, with no SQL, HTTP or new retrieval."""
    import json
    from dataclasses import asdict
    from datetime import datetime,timezone
    from pathlib import Path
    from app.rag_evaluation.dataset import load_dataset,DATASET_ID
    from app.quality.calibration import CalibrationSample,CalibrationSplit,build_calibration_split
    from app.quality.evidence_confidence import canonical_hash,parse_rule,verify_rule
    from app.quality.reference_confidence import fit_reference_rule
    root=Path(root).resolve()
    original=root/'runtime/ch09-evidence/calibration'
    dataset=load_dataset(DATASET_ID,root=root/'evals/datasets')
    split=CalibrationSplit.model_validate_json((original/'split.json').read_text(encoding='utf-8'))
    if split!=build_calibration_split(dataset):
        raise ValueError('Frozen split differs from deterministic dataset partition')
    old=parse_rule((original/'rule.json').read_text(encoding='utf-8'))
    verify_rule(old,top_k=old.source.top_k,budget_fingerprint=old.source.budget_fingerprint,
        dataset_fingerprint=dataset.fingerprint,corpus_hash=dataset.corpus_hash,require_actual=True)
    if old.split_fingerprint!=split.fingerprint or tuple(old.calibration_ids)!=split.calibration_ids:
        raise ValueError('Frozen split differs from verified source rule')
    manifest=json.loads((original/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('state')!='completed' or not manifest.get('cleanup',{}).get('ok'):
        raise ValueError('Original retrieval run is incomplete')
    run_id=manifest['run_id']
    if not __import__('re').fullmatch(r'[0-9a-f]{32}',run_id): raise ValueError('Invalid source run')
    resource=json.loads((original/'resources'/run_id/'manifest.json').read_text(encoding='utf-8'))
    hashes=resource['ownership']['content_hashes']
    chunks={canonical_hash(asdict(chunk.draft)):chunk for chunk in dataset.chunks}
    if len(chunks)!=len(dataset.chunks) or len(hashes)!=len(chunks) or set(hashes.values())!=set(chunks):
        raise ValueError('Original owned chunks differ from frozen corpus')
    by_physical={identifier:chunks[digest].draft for identifier,digest in hashes.items()}
    cases={case.eval_id:case for case in dataset.cases}
    samples=[CalibrationSample.model_validate_json(line) for line in
        (original/'samples.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    by_id={row.eval_id:row for row in samples}
    if canonical_hash([by_id[key].model_dump(mode='json') for key in split.calibration_ids])!=old.calibration_fingerprint:
        raise ValueError('Original calibration labels differ from verified source rule')
    texts={row.eval_id:{'question':cases[row.eval_id].query,'matches':[
        {'id':item.chunk_id,'question':by_physical[item.chunk_id].questions,
            'answer':by_physical[item.chunk_id].answer} for item in row.rankings]} for row in samples}
    report=fit_reference_rule(samples,split,texts)
    report.update(created_at=datetime.now(timezone.utc).isoformat(),
        source={'kind':'actual_retrieval_offline_recompute','original_run_id':run_id,
            'dataset_fingerprint':dataset.fingerprint,'corpus_hash':dataset.corpus_hash,
            'retrieval_samples_hash':__import__('hashlib').sha256((original/'samples.jsonl').read_bytes()).hexdigest()},
        previous_rule=old.model_dump(mode='json'),actual_external_calls=0)
    output=root/'runtime/ch09-evidence/reference-calibration'
    output.mkdir(parents=True,exist_ok=True)
    for name,value in (('report.json',report),('rule.json',report['rule'])):
        temporary=output/(name+'.tmp')
        temporary.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
        temporary.replace(output/name)
    return report


def read_confidence_report(root,active_rule=None):
    import json
    from pathlib import Path
    from app.quality.evidence_confidence import parse_rule,verify_rule
    def summary(rule):
        return {key:getattr(rule,key) for key in ('algorithm','threshold','weights','score_floor','rule_version')}
    active=summary(active_rule) if active_rule is not None else None
    path=Path(root)/'runtime/ch09-evidence/reference-calibration/report.json'
    if not path.exists(): return {'available':False,'reason':'no_calibration_report','active':active}
    if path.stat().st_size>3*1024*1024: raise ValueError('Calibration report exceeds limit')
    report=json.loads(path.read_text(encoding='utf-8'))
    rule=parse_rule(report['rule'])
    verify_rule(rule,top_k=rule.source.top_k,budget_fingerprint=rule.source.budget_fingerprint)
    return {**report,'available':True,'active':active,'recommended':summary(rule),
        'recommendation_active':active is not None and active['rule_version']==rule.rule_version}


if __name__=='__main__':
    import json
    from pathlib import Path
    report=recompute_reference_report(Path(__file__).resolve().parents[2])
    print(json.dumps({key:report[key] for key in ('calibration','held_out','actual_external_calls')},ensure_ascii=False))
