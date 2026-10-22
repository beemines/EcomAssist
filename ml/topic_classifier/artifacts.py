"""Frozen human-review selections and reports; never invent human decisions."""
from collections import Counter
from datetime import datetime
import json
import os
from pathlib import Path
import re
import shutil
from uuid import uuid4
import numpy as np
from app.topics.grouping import reserved_probe
from app.topics.reviews import make_review_pack,verify_pack,apply_review,digest
from app.topics.taxonomy import default_taxonomy
from app.topics.types import ClassifyItem
from app.topics.manifest import ModelManifest,read_manifest,verify_manifest,ALLOWED_FILES,DECODER_VERSION
from app.topics.cleaning import CLEANING_VERSION
from ml.topic_classifier.evaluation import evaluate_multilabel,decode_logits
from ml.topic_classifier.doctor import BASE_MODEL,BASE_REVISION,file_hash


def _predictions(rows,predictions):
    if type(predictions) is not dict or set(predictions)!={row.id for row in rows}:
        raise ValueError('Frozen prediction IDs must exactly match the held-out rows')
    return {row.id:default_taxonomy().canonical_labels(predictions[row.id],allow_empty=True) for row in rows}


def make_test_review_packs(rows,predictions,*,dataset_hash,model_version):
    rows=tuple(rows)
    if (len({row.id for row in rows})!=len(rows) or len({row.group_id for row in rows})<68
            or any(row.pilot or reserved_probe(row.text) for row in rows)
            or any(type(value) is not str or not re.fullmatch('[0-9a-f]{64}',value) for value in (dataset_hash,model_version))):
        raise ValueError('Review selection requires at least68 distinct held-out groups, frozen identities and no pilot/probe')
    predictions=_predictions(rows,predictions)
    rank=lambda row:digest(dict(seed=20261021,sample_id=row.id))
    candidates=sorted(rows,key=rank);gold=[];used_groups=set()
    for label in default_taxonomy().ordered_names:
        missing=max(0,2-sum(label in row.labels for row in gold))
        for row in candidates:
            if missing==0:break
            if label in row.labels and row.group_id not in used_groups:
                gold.append(row);used_groups.add(row.group_id);missing-=1
    for row in candidates:
        if len(gold)==68:break
        if row.group_id not in used_groups:gold.append(row);used_groups.add(row.group_id)
    gold=tuple(sorted(gold,key=rank))
    if len(gold)!=68:raise ValueError('Cannot select68 independent held-out examples')
    gold_ids={row.id for row in gold}
    candidates=[row for row in candidates if row.id not in gold_ids and row.group_id not in used_groups and row.labels!=predictions[row.id]]
    def features(row):
        actual=set(row.labels);predicted=set(predictions[row.id])
        return {(name,'FN') for name in actual-predicted}|{(name,'FP') for name in predicted-actual}
    errors=[];covered=set();error_groups=set()
    while candidates and len(errors)<34:
        row=min(candidates,key=lambda row:(-len(features(row)-covered),-len(features(row)),rank(row)))
        candidates=[other for other in candidates if other.group_id!=row.group_id]
        if row.group_id in error_groups:continue
        errors.append(row);error_groups.add(row.group_id);covered.update(features(row))
    def pack(selected,purpose):
        return make_review_pack(selected,snapshot_hash=dataset_hash,teacher_receipts=(),purpose=purpose,
            annotation_notes={row.id:'固定模型预测：'+('、'.join(predictions[row.id]) or '待复核（空预测）')+
                '。请按原句核对预标标签；本包不回流训练、不重调阈值。' for row in selected})
    gold_pack=pack(gold,'test');error_pack=pack(tuple(errors),'errors') if errors else None
    counts=Counter(label for row in gold for label in row.labels)
    fields=dict(dataset_hash=dataset_hash,model_version=model_version,predictions_hash=digest(predictions),
        gold_pack_hash=gold_pack.pack_hash,error_pack_hash=error_pack.pack_hash if error_pack else None,
        gold_count=68,errors_count=len(errors),human_status='pending',
        gold_label_coverage={label:counts[label] for label in default_taxonomy().ordered_names},
        coverage_shortfalls=[label for label in default_taxonomy().ordered_names if counts[label]<2])
    return gold_pack,error_pack,fields|dict(selection_hash=digest(fields))


def human_subset_report(pack,receipt,predictions,selection):
    verify_pack(pack)
    fields={key:value for key,value in selection.items() if key!='selection_hash'}
    if (digest(fields)!=selection.get('selection_hash') or digest(predictions)!=selection['predictions_hash']
            or pack.pack_hash!=selection['gold_pack_hash' if pack.purpose=='test' else 'error_pack_hash']
            or pack.purpose not in ('test','errors')):
        raise ValueError('Human report must retain the exact frozen model predictions and selection')
    receipt_fields=receipt.model_dump(mode='json');receipt_fields.pop('receipt_hash')
    if digest(receipt_fields)!=receipt.receipt_hash or datetime.fromisoformat(receipt.created_at).utcoffset() is None:
        raise ValueError('Human receipt identity or timestamp changed')
    expected=apply_review(pack,receipt.decisions).model_dump(mode='json')
    actual=receipt.model_dump(mode='json')
    for value in (expected,actual):
        value.pop('created_at');value.pop('receipt_hash')
    if expected!=actual:raise ValueError('Human receipt does not match its original frozen pack')
    metrics=None
    if receipt.samples:
        taxonomy=default_taxonomy()
        truth=np.asarray([taxonomy.encode(row.labels) for row in receipt.samples])
        predicted=np.asarray([taxonomy.encode(predictions[row.id]) if predictions[row.id] else [0]*17 for row in receipt.samples])
        metrics=evaluate_multilabel(truth,predicted,taxonomy=taxonomy).model_dump(mode='json')
    return dict(model_version=selection['model_version'],dataset_hash=selection['dataset_hash'],
        source='human_gold_subset' if pack.purpose=='test' else 'human_error_subset',
        receipt_hash=receipt.receipt_hash,reviewed_count=len(receipt.decisions),retained_count=len(receipt.samples),
        excluded_ids=list(receipt.excluded_ids),metrics=metrics,full_silver_report_unchanged=True)


def freeze_json(path,value):
    """Idempotent immutable publication, not a way to replace prior evidence."""
    path=Path(path);text=json.dumps(value,ensure_ascii=False,sort_keys=True,allow_nan=False,indent=2)+'\n'
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:raise ValueError('Refuse to replace different frozen evidence')
        return
    with path.open('x',encoding='utf-8',newline='\n') as out:
        out.write(text);out.flush();os.fsync(out.fileno())


class CPUClassifier:
    """Load known safetensors locally; inference receives IDs/text without truth."""
    def __init__(self,directory,*,weights_hash):
        import torch
        from transformers import AutoConfig,AutoTokenizer,AutoModelForSequenceClassification
        directory=Path(directory)
        if file_hash(directory/'model.safetensors')!=weights_hash:raise ValueError('Classifier weights changed')
        config=AutoConfig.from_pretrained(directory,local_files_only=True,trust_remote_code=False)
        taxonomy=default_taxonomy()
        if (config.model_type!='bert' or config.hidden_size!=768 or config.num_hidden_layers!=12
                or config.num_attention_heads!=12 or config.num_labels!=17
                or config.problem_type!='multi_label_classification'
                or config.id2label!=dict(enumerate(taxonomy.ordered_names))):
            raise ValueError('Only the fixed HFL17-label architecture may run')
        self._torch=torch
        self.tokenizer=AutoTokenizer.from_pretrained(directory,local_files_only=True,trust_remote_code=False)
        self.model=AutoModelForSequenceClassification.from_pretrained(directory,local_files_only=True,
            trust_remote_code=False,use_safetensors=True,weights_only=True).cpu().float().eval()
    def predict(self,items):
        items=tuple(items)
        if not items or any(not isinstance(row,ClassifyItem) for row in items):
            raise ValueError('Inference accepts only nonempty ID/text items, never label-bearing rows')
        if len({row.id for row in items})!=len(items):raise ValueError('Inference IDs must be unique')
        for row in items:
            if len(self.tokenizer(row.text,truncation=False,add_special_tokens=True)['input_ids'])>128:
                raise ValueError('Frozen evaluation input exceeds128 tokens; do not truncate')
        values=[]
        with self._torch.inference_mode():
            for start in range(0,len(items),16):
                encoded=self.tokenizer([row.text for row in items[start:start+16]],padding=True,truncation=False,return_tensors='pt')
                values.append(self.model(**encoded).logits.float().cpu().numpy())
        result=np.concatenate(values,axis=0)
        if result.shape!=(len(items),17) or not np.isfinite(result).all():raise ValueError('Invalid classifier logits')
        return result


def _cpu_checks(training,candidate,items,thresholds):
    original=CPUClassifier(training.best_checkpoint,weights_hash=training.weights_hash)
    copied=CPUClassifier(candidate,weights_hash=training.weights_hash)
    before=original.predict(items);after=copied.predict(items)
    roundtrip=dict(passed=bool(np.allclose(before,after,atol=1e-5,rtol=1e-4)),
        atol=1e-5,rtol=1e-4,sample_count=len(items),max_abs_difference=float(np.abs(before-after).max()))
    probe=ClassifyItem(id='reserved-probe',text='买大了想退')
    prediction=decode_logits(copied.predict([probe]),thresholds.thresholds)[0]
    labels=[label for label,present in zip(default_taxonomy().ordered_names,prediction,strict=True) if present]
    return dict(roundtrip=roundtrip,probe=dict(text=probe.text,labels=labels,expected_labels=['退换货','尺码'],
        passed=labels==['退换货','尺码'],status='classified' if labels else 'needs_review'))


class ExportRejected(ValueError):
    """Retain a verifiable failed candidate for reporting, never activate it."""
    def __init__(self,reason,*,identity,candidate):
        super().__init__(reason)
        self.identity=identity
        self.candidate=candidate


def export_bundle(training,thresholds,reports:Path,output:Path):
    """Export the immutable core; full evaluation/review evidence remains separate."""
    from ml.topic_classifier.train import load_training_receipt
    reports=Path(reports);output=Path(output)
    receipt=load_training_receipt(Path(training.best_checkpoint).parent)
    if receipt!=training:raise ValueError('Export requires the exact completed training receipt')
    context=json.loads((reports/'context.json').read_text(encoding='utf-8'))
    if (context.get('training_receipt_hash')!=receipt.receipt_hash or context.get('dataset_hash')!=receipt.dataset_hash
            or context.get('threshold_hash')!=thresholds.threshold_hash
            or not re.fullmatch('[0-9a-f]{64}',context.get('pilot_receipt_hash',''))):
        raise ValueError('Export context is not bound to the completed training and validation thresholds')
    items=tuple(ClassifyItem.model_validate(row) for row in context['validation_items'])
    if not 1<=len(items)<=16:raise ValueError('CPU roundtrip requires1..16 frozen validation inputs')
    if output.is_symlink():raise ValueError('Candidate directory cannot be a link')
    source=Path(receipt.best_checkpoint)
    if output.exists():
        manifest=read_manifest(output)
        if (manifest.core.training_receipt_hash!=receipt.receipt_hash or manifest.core.dataset_hash!=receipt.dataset_hash
                or manifest.core.pilot_receipt_hash!=context['pilot_receipt_hash']
                or json.loads((output/'thresholds.json').read_text(encoding='utf-8')).get('threshold_hash')!=thresholds.threshold_hash):
            raise ValueError('Candidate already belongs to different frozen source data')
        staging=output
    else:
        output.parent.mkdir(parents=True,exist_ok=True)
        staging=output.parent/('.candidate-'+uuid4().hex);staging.mkdir()
        for name in sorted(ALLOWED_FILES-{'thresholds.json'}):
            path=source/name
            if path.exists():
                if path.is_symlink() or not path.is_file():raise ValueError('Export sources must be ordinary local files')
                shutil.copyfile(path,staging/name)
        freeze_json(staging/'thresholds.json',thresholds.model_dump(mode='json'))
        files={path.name:dict(sha256=file_hash(path),bytes=path.stat().st_size) for path in staging.iterdir()}
        taxonomy=default_taxonomy()
        core=dict(schema_version=1,base_model=BASE_MODEL,base_revision=BASE_REVISION,
            taxonomy_version=taxonomy.version,taxonomy_hash=taxonomy.digest,labels=list(taxonomy.ordered_names),
            cleaning_version=CLEANING_VERSION,decoder_version=DECODER_VERSION,max_tokens=128,seed=20261021,
            dataset_hash=receipt.dataset_hash,augmentation_hash=receipt.augmentation_hash,
            pilot_receipt_hash=context['pilot_receipt_hash'],training_receipt_hash=receipt.receipt_hash,
            training_config_hash=receipt.config_hash,dependency_lock_hash=file_hash(Path(__file__).with_name('uv.lock')),files=files)
        value=ModelManifest.model_validate_json(json.dumps(dict(core=core,model_version=digest(core)),ensure_ascii=False))
        freeze_json(staging/'manifest.json',value.model_dump(mode='json'))
        manifest=read_manifest(staging)
    if manifest.core.files['model.safetensors'].sha256!=receipt.weights_hash:
        raise ValueError('Exported full weights differ from the trained checkpoint')
    checks=_cpu_checks(receipt,staging,items,thresholds)
    for name,check in (('cpu-roundtrip',checks['roundtrip']),('probe',checks['probe'])):
        freeze_json(reports/(name+'.json'),dict(check,model_version=manifest.model_version))
    identity=verify_manifest(staging)
    if not checks['roundtrip']['passed']:
        raise ExportRejected('CPU export roundtrip failed; candidate not published',identity=identity,candidate=staging)
    if not checks['probe']['passed']:
        raise ExportRejected('Independent multilabel probe failed; candidate not published',identity=identity,candidate=staging)
    if staging!=output:os.rename(staging,output)
    return verify_manifest(output)
