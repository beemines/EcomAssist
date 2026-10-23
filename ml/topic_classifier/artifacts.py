"""Frozen human-review selections and reports; never invent human decisions."""
from collections import Counter
from datetime import datetime
import gc
from html import escape
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
from app.topics.types import ClassifyItem,LabelledSample
from app.topics.manifest import ModelManifest,read_manifest,verify_manifest,ALLOWED_FILES,DECODER_VERSION
from app.topics.cleaning import CLEANING_VERSION
from ml.topic_classifier.evaluation import evaluate_multilabel,decode_logits,select_thresholds,ThresholdSet
from ml.topic_classifier.doctor import BASE_MODEL,BASE_REVISION,file_hash


def _predictions(rows,predictions):
    if type(predictions) is not dict or set(predictions)!={row.id for row in rows}:
        raise ValueError('Frozen prediction IDs must exactly match the held-out rows')
    return {row.id:default_taxonomy().canonical_labels(predictions[row.id],allow_empty=True) for row in rows}


def make_test_review_packs(rows,predictions,*,dataset_hash,model_version,required_scenes=None):
    rows=tuple(rows)
    if (len({row.id for row in rows})!=len(rows) or len({row.group_id for row in rows})<68
            or any(row.pilot or reserved_probe(row.text) for row in rows)
            or any(type(value) is not str or not re.fullmatch('[0-9a-f]{64}',value) for value in (dataset_hash,model_version))):
        raise ValueError('Review selection requires at least68 distinct held-out groups, frozen identities and no pilot/probe')
    predictions=_predictions(rows,predictions)
    rank=lambda row:digest(dict(seed=20261021,sample_id=row.id))
    candidates=sorted(rows,key=rank);gold=[];used_groups=set()
    if required_scenes is not None:
        ids={r.id for r in rows}
        if (type(required_scenes) is not dict or set(required_scenes)!={'A','B'} or
                any(type(v) not in (list,tuple) or len(set(v))!=len(v) or not set(v)<=ids for v in required_scenes.values())
                or set(required_scenes['A'])&set(required_scenes['B'])):
            raise ValueError('Invalid explicit held-out scene memberships')
        for scene in ('A','B'):
            selected=0
            for row in candidates:
                if row.id in required_scenes[scene] and row.group_id not in used_groups:
                    gold.append(row);used_groups.add(row.group_id);selected+=1
                    if selected==4:break
            if selected!=4:raise ValueError('Four independent examples per required scene are needed')
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
    if required_scenes is not None:
        fields['gold_scene_coverage']={scene:len(gold_ids&set(required_scenes[scene])) for scene in ('A','B')}
        fields['required_scenes_hash']=digest(required_scenes)
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


def finalize_run(reports,model,*,review_root):
    """Add actual human subset evidence; never rerun training or calibration."""
    from app.topics.review_submission import TopicReviewService
    from app.topics.manifest import ReleaseManifest,FileDigest,verify_release
    reports=Path(reports);model=Path(model);review_root=Path(review_root)
    complete=json.loads((reports/'complete.json').read_text(encoding='utf-8'))
    if complete.get('completion_hash')!=digest({k:v for k,v in complete.items() if k!='completion_hash'}):
        raise ValueError('Completed evaluation was modified')
    for name,sha in complete['artifact_hashes'].items():
        if file_hash(reports/name)!=sha:raise ValueError('Frozen evaluation artifact changed')
    selection=json.loads((reports/'review-selection.json').read_text(encoding='utf-8'))
    predictions={}
    for line in (reports/'predictions.jsonl').read_text(encoding='utf-8').splitlines():
        row=json.loads(line)
        if row['id'] in predictions:raise ValueError('Duplicate frozen prediction')
        predictions[row['id']]=tuple(row['predicted_labels'])
    if digest(predictions)!=selection['predictions_hash']:raise ValueError('Frozen predictions changed')
    outputs={};human_reports={}
    for prefix,folder in (('gold','test-review'),('error','error-review')):
        if prefix=='error' and not selection['errors_count']:continue
        service=TopicReviewService(review_root/folder)
        receipt=service.state()
        if receipt is None:raise ValueError(f'Actual human review is pending: {folder}')
        pack=service.pack();result=human_subset_report(pack,receipt,predictions,selection)
        if not receipt.samples:raise ValueError('Actual human review retained no evaluable examples')
        outputs[prefix+'-pack.json']=pack.model_dump(mode='json')
        outputs[prefix+'-receipt.json']=receipt.model_dump(mode='json')
        outputs[prefix+'-report.json']=result;human_reports[prefix]=result
    for prefix,result in human_reports.items():freeze_json(reports/f'{prefix}.json',result)
    finalized=dict(model_version=complete['model_version'],dataset_hash=selection['dataset_hash'],human_status='reviewed',
        gold_receipt_hash=human_reports['gold']['receipt_hash'],
        error_receipt_hash=human_reports.get('error',{}).get('receipt_hash'),model_published=complete['model_published'])
    if complete['model_published']:
        if verify_manifest(model).model_version!=complete['model_version']:raise ValueError('Model identity changed')
        evidence=model/'evidence';evidence.mkdir(exist_ok=True)
        copy_names={'evaluation-complete.json':'complete.json','silver.json':'silver.json','predictions.jsonl':'predictions.jsonl',
            'review-selection.json':'review-selection.json','probe.json':'probe.json','cpu-roundtrip.json':'cpu-roundtrip.json'}
        for name,source in copy_names.items():_freeze_text(evidence/name,(reports/source).read_text(encoding='utf-8'))
        for name,value in outputs.items():freeze_json(evidence/name,value)
        names=set(copy_names)|set(outputs)
        files={name:FileDigest(sha256=file_hash(evidence/name),bytes=(evidence/name).stat().st_size) for name in names}
        fields=dict(schema_version=1,model_version=complete['model_version'],human_status='reviewed',
            files={name:record.model_dump(mode='json') for name,record in files.items()})
        release=ReleaseManifest(**fields,release_hash=digest(fields))
        freeze_json(model/'release.json',release.model_dump(mode='json'))
        verify_release(model)
        finalized['release_hash']=release.release_hash
    freeze_json(reports/'human-complete.json',finalized)
    return finalized


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
        model,loading=AutoModelForSequenceClassification.from_pretrained(directory,local_files_only=True,
            trust_remote_code=False,use_safetensors=True,weights_only=True,output_loading_info=True)
        if any(loading.get(key) for key in ('missing_keys','unexpected_keys','mismatched_keys','error_msgs','error_messages')):
            del model
            gc.collect()
            raise ValueError('Trained weights are incomplete or incompatible; random initialization is forbidden')
        self.model=model.cpu().float().eval()
    def predict(self,items):
        if self.model is None:raise ValueError('Classifier has been closed')
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
                encoded={key:value.cpu() for key,value in encoded.items()}
                values.append(self.model(**encoded).logits.float().cpu().numpy())
        result=np.concatenate(values,axis=0)
        if result.shape!=(len(items),17) or not np.isfinite(result).all():raise ValueError('Invalid classifier logits')
        return result
    def close(self):
        self.model=None;self.tokenizer=None
        gc.collect()


def _cpu_checks(training,candidate,items,thresholds):
    original=CPUClassifier(training.best_checkpoint,weights_hash=training.weights_hash)
    copied=None
    try:
        copied=CPUClassifier(candidate,weights_hash=training.weights_hash)
        before=original.predict(items);after=copied.predict(items)
        roundtrip=dict(passed=bool(np.allclose(before,after,atol=1e-5,rtol=1e-4)),
            atol=1e-5,rtol=1e-4,sample_count=len(items),max_abs_difference=float(np.abs(before-after).max()))
        # Release diagnostics are separate from train/validation/test and never alter predictions.
        expected=(('买大了',('尺码',)),('尺码买大了',('尺码',)),('买大了想退',('退换货','尺码')),
            ('尺码大了想退',('退换货','尺码')),('买小了想退',('退换货','尺码')),('太大了想换',('退换货','尺码')),
            ('尺寸不合适想退',('退换货','尺码')),('不退货,只问尺码',('尺码',)))
        probes=tuple(ClassifyItem(id=f'reserved-probe-{i}',text=text) for i,(text,_) in enumerate(expected))
        decoded=decode_logits(copied.predict(probes),thresholds.thresholds)
        cases=[]
        for (text,want),prediction in zip(expected,decoded,strict=True):
            labels=[label for label,present in zip(default_taxonomy().ordered_names,prediction,strict=True) if present]
            cases.append(dict(text=text,labels=labels,expected_labels=list(want),passed=labels==list(want),
                status='classified' if labels else 'needs_review'))
        primary=next(row for row in cases if row['text']=='买大了想退')
        return dict(roundtrip=roundtrip,probe=primary|dict(passed=all(row['passed'] for row in cases),
            primary_passed=primary['passed'],cases=cases))
    finally:
        original.close()
        if copied is not None:copied.close()


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
        raise ExportRejected('Independent multilabel/negation probes failed; candidate not published',identity=identity,candidate=staging)
    if staging!=output:os.rename(staging,output)
    return verify_manifest(output)


def _freeze_text(path,text):
    if path.exists():
        if path.read_text(encoding='utf-8')!=text:raise ValueError('Refuse to replace different frozen artifact')
        return
    with path.open('x',encoding='utf-8',newline='\n') as out:out.write(text)


def _metrics_html(report,model_version,probe_passed):
    cards=[]
    for row in report.per_class:
        tn,fp=row.confusion[0];fn,tp=row.confusion[1]
        cards.append(f'<section><h2>{escape(row.label)}</h2><p>正例 {row.support} · '
            f'P {row.precision:.3f} / R {row.recall:.3f} / F1 {row.f1:.3f}</p>'
            '<table><tr><th></th><th>预测阴性</th><th>预测阳性</th></tr>'
            f'<tr><th>真实阴性</th><td>TN {tn}</td><td>FP {fp}</td></tr>'
            f'<tr><th>真实阳性</th><td>FN {fn}</td><td>TP {tp}</td></tr></table>'
            f'<small>{escape("；".join(row.undefined_denominators))}</small></section>')
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'+\
        '<title>主题模型评测报告</title><style>body{margin:32px auto;padding:0 24px;max-width:1100px;background:#f5f7f3;color:#253f38;font:16px system-ui}code{overflow-wrap:anywhere}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:16px}section{background:white;border:1px solid #d5e0d7;border-radius:16px;padding:20px}table{width:100%;border-collapse:collapse}th,td{padding:7px;border:1px solid #d5e0d7}small{color:#845947}</style>'+\
        f'<h1>主题模型 · 冻结留出评测</h1><p>模型 <code>{escape(model_version)}</code></p>'+\
        '<p>此为完整 silver 留出集（LLM 预标），不是人工 gold。人工修订另出报告，不能回调阈值。</p>'+\
        f'<p>样本 {report.sample_count} · 固定17类 Macro-F1 {report.macro_f1:.3f} · Micro-F1 {report.micro_f1:.3f} · '+\
        f'完全匹配 {report.exact_match:.3f} · Hamming {report.hamming_loss:.4f} · 待复核率 {report.needs_review_rate:.3f}</p>'+\
        f'<p>独立多标签 probe：{"通过" if probe_passed else "未通过，候选禁止发布"}。真实来源子集和全部预测见同目录 JSON。</p><main>'+''.join(cards)+'</main></html>'


def evaluate_run(dataset:Path,training:Path,output:Path,*,pilot_receipt_hash:str,model_output=None,review_root=None):
    """Freeze validation choices before opening test truth; leave human reviews pending."""
    from ml.topic_classifier.data import load_dataset
    from ml.topic_classifier.train import load_training_receipt,training_lease
    from app.topics.reviews import render_review_html
    dataset=Path(dataset);output=Path(output);output.mkdir(parents=True,exist_ok=True)
    model_output=Path(model_output or output.parent/'model').resolve()
    review_root=Path(review_root or output.parent).resolve()
    receipt=load_training_receipt(training)
    manifest=load_dataset(dataset,splits=('train','validation'))
    if (receipt.dataset_hash!=manifest.manifest_hash or not re.fullmatch('[0-9a-f]{64}',pilot_receipt_hash)
            or file_hash(dataset/'train-augmentations.jsonl')!=receipt.augmentation_hash):
        raise ValueError('Evaluation source does not match the completed training and frozen pilot')
    scope=dict(training_receipt_hash=receipt.receipt_hash,dataset_hash=manifest.manifest_hash,
        augmentation_hash=receipt.augmentation_hash,pilot_receipt_hash=pilot_receipt_hash,
        model_output=str(model_output),review_root=str(review_root))
    coverage_contract=None
    if dataset.parent.name=='coverage-v5' or (dataset/'coverage.json').exists():
        from ml.topic_classifier.coverage_repair import read_contract
        coverage_contract,coverage_hash=read_contract(dataset)
        training_scope=json.loads((Path(training)/'run.json').read_text(encoding='utf-8'))
        if coverage_contract['manifest_hash']!=manifest.manifest_hash or training_scope.get('coverage_contract_hash')!=coverage_hash:
            raise ValueError('Evaluation coverage contract differs from actual training')
        scope['coverage_contract_hash']=coverage_hash
    with training_lease(output):
        freeze_json(output/'evaluation-run.json',scope)
        complete=output/'complete.json'
        if complete.exists():
            saved=json.loads(complete.read_text(encoding='utf-8'))
            fields={k:v for k,v in saved.items() if k!='completion_hash'}
            if saved.get('scope_hash')!=digest(scope) or saved.get('completion_hash')!=digest(fields):
                raise ValueError('Completed evaluation identity changed')
            for name,sha in saved['artifact_hashes'].items():
                if file_hash(output/name)!=sha:raise ValueError('Frozen evaluation artifact changed')
            load_dataset(dataset,splits=('test',))
            if saved['model_published'] and verify_manifest(model_output).model_version!=saved['model_version']:
                raise ValueError('Completed model identity changed')
            return saved
        def read(name):
            return tuple(LabelledSample.model_validate_json(line)
                for line in (dataset/(name+'.jsonl')).read_text(encoding='utf-8').splitlines() if line.strip())
        def inference_items(rows):return tuple(ClassifyItem(id=row.id,text=row.text) for row in rows)
        classifier=CPUClassifier(receipt.best_checkpoint,weights_hash=receipt.weights_hash)
        try:
            validation=read('validation');threshold_file=output/'thresholds.json'
            if threshold_file.exists():thresholds=ThresholdSet.model_validate_json(threshold_file.read_text(encoding='utf-8'))
            else:
                if (output/'predictions.jsonl').exists():raise ValueError('Test was already opened; never recalibrate thresholds')
                values=classifier.predict(inference_items(validation))
                truth=np.asarray([default_taxonomy().encode(row.labels) for row in validation])
                thresholds=select_thresholds(values,truth,split='validation')
                freeze_json(threshold_file,thresholds.model_dump(mode='json'))
            context=dict(training_receipt_hash=receipt.receipt_hash,dataset_hash=manifest.manifest_hash,
                threshold_hash=thresholds.threshold_hash,pilot_receipt_hash=pilot_receipt_hash,
                validation_items=[row.model_dump(mode='json') for row in inference_items(validation[:2])])
            freeze_json(output/'context.json',context)
            published=True
            try:identity=export_bundle(receipt,thresholds,output,model_output)
            except ExportRejected as rejected:
                identity=rejected.identity;published=False
            # The first test-truth read is after threshold/context publication and candidate identity.
            load_dataset(dataset,splits=('test',));test=read('test')
            logits=classifier.predict(inference_items(test));predicted=decode_logits(logits,thresholds.thresholds)
            taxonomy=default_taxonomy();truth=np.asarray([taxonomy.encode(row.labels) for row in test])
            metrics=evaluate_multilabel(truth,predicted,taxonomy=taxonomy)
            predictions={row.id:tuple(label for label,selected in zip(taxonomy.ordered_names,predicted[i],strict=True) if selected)
                for i,row in enumerate(test)}
            by_origin={}
            for origin in ('real','demo','synthetic','unverified'):
                indices=[i for i,row in enumerate(test) if row.origin==origin]
                by_origin[origin]=dict(sample_count=len(indices),metrics=evaluate_multilabel(truth[indices],predicted[indices],taxonomy=taxonomy).model_dump(mode='json') if indices else None)
            freeze_json(output/'silver.json',dict(model_version=identity.model_version,source='LLM_prelabelled_silver',
                dataset_hash=manifest.manifest_hash,metrics=metrics.model_dump(mode='json'),by_origin=by_origin,human_status='pending'))
            lines=''.join(json.dumps(dict(id=row.id,text=row.text,group_id=row.group_id,origin=row.origin,
                silver_labels=list(row.labels),predicted_labels=list(predictions[row.id]),logits=logits[i].tolist()),
                ensure_ascii=False,allow_nan=False,sort_keys=True)+'\n' for i,row in enumerate(test))
            _freeze_text(output/'predictions.jsonl',lines)
            required_scenes=None
            if coverage_contract is not None:
                from app.topics.coverage_repair import scene_of,audit_scene_coverage
                path=dataset/'test-scenes.json'
                if path.is_symlink() or file_hash(path)!=coverage_contract['test_scene_hash']:
                    raise ValueError('Frozen held-out scene membership changed')
                required_scenes=json.loads(path.read_text(encoding='utf-8'))
                if required_scenes!={s:sorted(r.id for r in test if scene_of(r)==s) for s in ('A','B')}:
                    raise ValueError('Held-out scene identity differs from actual frozen rows')
                audit_scene_coverage(test,partition='test')
            gold,errors,selection=make_test_review_packs(test,predictions,dataset_hash=manifest.manifest_hash,
                model_version=identity.model_version,required_scenes=required_scenes)
            for name,pack in (('test-review',gold),('error-review',errors)):
                if pack is not None:
                    root=review_root/name;root.mkdir(parents=True,exist_ok=True)
                    freeze_json(root/'pack.json',pack.model_dump(mode='json'))
                    _freeze_text(root/'review.html',render_review_html(pack,review_port={'remediation-v2':8008,'negation-v4':8009,'coverage-v5':8010}.get(review_root.name,8007)))
            freeze_json(output/'review-selection.json',selection)
            probe=json.loads((output/'probe.json').read_text(encoding='utf-8'))
            _freeze_text(output/'metrics.html',_metrics_html(metrics,identity.model_version,probe['passed']))
            names=('thresholds.json','context.json','silver.json','predictions.jsonl','review-selection.json','cpu-roundtrip.json','probe.json','metrics.html')
            result=dict(status='complete',scope_hash=digest(scope),dataset_size=len(test),model_version=identity.model_version,
                model_published=published,probe_passed=probe['passed'],human_status='pending',gold_count=68,errors_count=selection['errors_count'],
                artifact_hashes={name:file_hash(output/name) for name in names})
            result['completion_hash']=digest(result);freeze_json(complete,result)
            return result
        finally:classifier.close()
