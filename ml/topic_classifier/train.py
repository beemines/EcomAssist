"""Full-parameter local training; held-out truth is never opened here."""
from dataclasses import dataclass
from contextlib import contextmanager
from datetime import datetime,timezone
import hashlib
import json
import math
import os
from pathlib import Path
import time
from uuid import uuid4

import numpy as np
import torch
from pydantic import Field,model_validator
from sklearn.metrics import f1_score
from transformers import TrainingArguments

from app.topics.grouping import validate_augmentation,exact_text_key
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.types import LabelledSample,StrictRecord
from ml.topic_classifier.data import load_dataset,SEED
from ml.topic_classifier.doctor import BASE_MODEL,BASE_REVISION,file_hash,verify_base


CONFIG=dict(max_tokens=128,epochs=8,effective_batch=16,fp16=True,gradient_checkpointing=True,
    learning_rate=2e-5,weight_decay=.01,warmup_steps=.1,max_grad_norm=1.,
    patience=2,minimum_improvement=.001,checkpoint_selection='validation_macro_f1_at_0.5_earlier_tie')


class TrainingReceipt(StrictRecord):
    best_checkpoint:str
    history_path:str
    dataset_hash:str
    config_hash:str
    augmentation_hash:str
    best_epoch:float=Field(ge=1,le=8)
    best_macro_f1:float=Field(ge=0,le=1)
    encoder_before:str
    encoder_after:str
    weights_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    history_hash:str=Field(pattern=r'^[0-9a-f]{64}$')
    receipt_hash:str

    @model_validator(mode='after')
    def identity(self):
        fields=self.model_dump(mode='json');fields.pop('receipt_hash')
        if self.receipt_hash!=digest(fields) or self.encoder_before==self.encoder_after:
            raise ValueError('Training receipt identity or encoder training proof changed')
        return self


@dataclass(frozen=True)
class TrainingData:
    train:tuple
    validation:tuple
    manifest_hash:str
    augmentation_hash:str


def training_arguments(output:Path,micro_batch:int) -> TrainingArguments:
    if type(micro_batch) is not int or micro_batch not in (1,2,4):
        raise ValueError('Only measured micro-batches 4,2,1 may maintain effective batch16')
    return TrainingArguments(output_dir=str(output),num_train_epochs=CONFIG['epochs'],
        per_device_train_batch_size=micro_batch,per_device_eval_batch_size=micro_batch,
        gradient_accumulation_steps=CONFIG['effective_batch']//micro_batch,fp16=CONFIG['fp16'],gradient_checkpointing=CONFIG['gradient_checkpointing'],
        learning_rate=CONFIG['learning_rate'],weight_decay=CONFIG['weight_decay'],warmup_steps=CONFIG['warmup_steps'],
        max_grad_norm=CONFIG['max_grad_norm'],optim='adamw_torch',
        eval_strategy='epoch',save_strategy='epoch',logging_strategy='epoch',save_total_limit=2,
        load_best_model_at_end=True,metric_for_best_model='macro_f1',greater_is_better=True,
        report_to='none',dataloader_num_workers=0,seed=SEED,data_seed=SEED,
        restore_callback_states_from_checkpoint=True,save_only_model=False)


def read_training_data(root:Path) -> TrainingData:
    root=Path(root);manifest=load_dataset(root,splits=('train','validation'))
    memberships=[set(manifest.splits[name]) for name in ('train','validation','test')]
    families=[set(manifest.group_ids[name]) for name in ('train','validation','test')]
    if any(memberships[i]&memberships[j] or families[i]&families[j] for i in range(3) for j in range(i+1,3)):
        raise ValueError('Training and held-out identities/families overlap')
    audit=json.loads((root/'data-audit.json').read_text(encoding='utf-8'))
    if (audit.get('manifest_hash')!=manifest.manifest_hash or type(audit.get('augmentation')) is not dict
            or audit['augmentation'].get('status')!='complete'):
        raise ValueError('Training requires a completed frozen augmentation audit')
    def read(name):
        rows=tuple(LabelledSample.model_validate_json(line) for line in (root/name).read_text(encoding='utf-8').splitlines() if line.strip())
        if len({row.id for row in rows})!=len(rows):raise ValueError('Repeated training-data identities')
        return rows
    train=read('train.jsonl');validation=read('validation.jsonl')
    for name,rows in (('train',train),('validation',validation)):
        if set(row.id for row in rows)!=set(manifest.splits[name]):raise ValueError('Frozen membership changed')
        if any(row.group_id not in manifest.group_ids[name] for row in rows):raise ValueError('Frozen family changed')
    overlay=json.loads((root/'augmentation.json').read_text(encoding='utf-8'))
    augmentation_hash=file_hash(root/'train-augmentations.jsonl')
    if overlay.get('base_manifest_hash')!=manifest.manifest_hash or overlay.get('content_hash')!=augmentation_hash:
        raise ValueError('Frozen train augmentation identity changed')
    children=read('train-augmentations.jsonl');parents={row.id:row for row in train}
    if overlay.get('count')!=len(children) or overlay.get('parent_ids')!=[row.id.removesuffix('-aug') for row in children]:
        raise ValueError('Augmentation membership changed')
    seen={exact_text_key(row.text) for row in train+validation}
    for child in children:
        parent=parents.get(child.id.removesuffix('-aug'))
        if parent is None:raise ValueError('Only frozen training parents may be augmented')
        validate_augmentation(parent,child)
        if child.id in set.union(*memberships) or exact_text_key(child.text) in seen:
            raise ValueError('Augmentation duplicates original or held-out content')
        seen.add(exact_text_key(child.text))
    return TrainingData(train+children,validation,manifest.manifest_hash,augmentation_hash)


class EncodedSamples(torch.utils.data.Dataset):
    def __init__(self,rows,tokenizer):
        self.rows=tuple(rows);self.tokenizer=tokenizer
        for row in self.rows:
            if len(tokenizer(row.text,truncation=False,add_special_tokens=True)['input_ids'])>CONFIG['max_tokens']:
                raise ValueError('A frozen training input exceeds128 tokens; never silently truncate')
    def __len__(self):return len(self.rows)
    def __getitem__(self,index):
        row=self.rows[index]
        encoded=self.tokenizer(row.text,truncation=False,add_special_tokens=True)
        return dict(encoded,labels=torch.tensor(default_taxonomy().encode(row.labels),dtype=torch.float32))


def compute_metrics(result):
    logits,truth=result
    if isinstance(logits,tuple):logits=logits[0]
    logits=np.asarray(logits,dtype=np.float64);truth=np.asarray(truth)
    if (logits.ndim!=2 or logits.shape[1]!=17 or logits.shape!=truth.shape or len(logits)==0
            or not np.isfinite(logits).all() or not np.isin(truth,[0,1]).all()):
        raise ValueError('Expected finite logits and binary truth with all17 labels')
    prediction=logits>=0
    prediction[:,-1]&=~prediction[:,:-1].any(axis=1)
    return dict(macro_f1=float(f1_score(truth,prediction,average='macro',zero_division=0)),
        micro_f1=float(f1_score(truth,prediction,average='micro',zero_division=0)),
        needs_review_rate=float((~prediction.any(axis=1)).mean()))


def assert_full_trainable(model):
    if any(not parameter.requires_grad for parameter in model.parameters()):
        raise ValueError('Every encoder and classification parameter must be trainable')
    return sum(parameter.numel() for parameter in model.parameters())


def encoder_hash(model):
    value=hashlib.sha256()
    for name,tensor in sorted(model.base_model.state_dict().items()):
        value.update(name.encode());value.update(str(tensor.dtype).encode())
        value.update(str(tuple(tensor.shape)).encode());value.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return value.hexdigest()


def best_validation_epoch(history):
    rows=[row for row in history if 'eval_macro_f1' in row and 'epoch' in row]
    if not rows or any(not math.isfinite(row['eval_macro_f1']) for row in rows):
        raise ValueError('No finite validation epoch exists')
    return min(rows,key=lambda row:(-row['eval_macro_f1'],row['epoch']))


def load_training_receipt(root:Path) -> TrainingReceipt:
    root=Path(root).resolve()
    receipt=TrainingReceipt.model_validate_json((root/'receipt.json').read_text(encoding='utf-8'))
    if Path(receipt.best_checkpoint).resolve()!=root/'best' or Path(receipt.history_path).resolve()!=root/'history.json':
        raise ValueError('Training artifact paths do not belong to this completed run')
    if file_hash(root/'best/model.safetensors')!=receipt.weights_hash or file_hash(root/'history.json')!=receipt.history_hash:
        raise ValueError('Full trained weights or training history changed')
    identity=json.loads((root/'run.json').read_text(encoding='utf-8'))
    if (digest(identity)!=receipt.config_hash or identity.get('dataset_hash')!=receipt.dataset_hash
            or identity.get('augmentation_hash')!=receipt.augmentation_hash or identity.get('base')!=BASE_MODEL
            or identity.get('revision')!=BASE_REVISION or identity.get('seed')!=SEED or identity.get('config')!=CONFIG
            or identity.get('lock_hash')!=file_hash(Path(__file__).with_name('uv.lock'))):
        raise ValueError('Completed training configuration or dataset identity changed')
    if 'sampling' in identity:
        sampling=json.loads((root/'sampling.json').read_text(encoding='utf-8'))
        if (sampling!=identity['sampling'] or sampling.get('profile')!='short30-v1'
                or sampling.get('sampling_hash')!=digest({k:v for k,v in sampling.items() if k!='sampling_hash'})):
            raise ValueError('Training sampling evidence changed')
    history=json.loads((root/'history.json').read_text(encoding='utf-8'))
    best=best_validation_epoch(history['epochs'])
    if (history.get('config_hash')!=receipt.config_hash or history.get('dataset_hash')!=receipt.dataset_hash
            or history.get('encoder_before')!=receipt.encoder_before or history.get('encoder_after')!=receipt.encoder_after
            or history.get('parameters')!=history.get('trainable_parameters') or history.get('parameters',0)<100_000_000
            or best['epoch']!=receipt.best_epoch or best['eval_macro_f1']!=receipt.best_macro_f1):
        raise ValueError('Training curve/full-parameter proof does not match its receipt')
    return receipt


def _write(path,value):
    temporary=path.with_name('.'+path.name+'.'+uuid4().hex+'.tmp')
    try:
        with temporary.open('x',encoding='utf-8') as out:
            json.dump(value,out,ensure_ascii=False,allow_nan=False,indent=2);out.flush();os.fsync(out.fileno())
        os.replace(temporary,path)
    finally:temporary.unlink(missing_ok=True)


@contextmanager
def training_lease(output:Path):
    """The OS releases the fixed-file lock on process death; never unlink it."""
    marker=output/'.train.lock'
    if marker.is_symlink():raise RuntimeError('Training lock cannot be a link')
    descriptor=os.open(marker,os.O_RDWR|os.O_CREAT,0o600)
    with os.fdopen(descriptor,'r+b',buffering=0) as stream:
        try:
            if os.name=='nt':
                import msvcrt
                msvcrt.locking(stream.fileno(),msvcrt.LK_NBLCK,1)
            else:
                import fcntl
                fcntl.flock(stream.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except OSError as exc:raise RuntimeError('Another training process owns this output') from exc
        try:
            if os.fstat(stream.fileno()).st_size==0:stream.write(b'\0')
            yield
        finally:
            stream.seek(0)
            if os.name=='nt':msvcrt.locking(stream.fileno(),msvcrt.LK_UNLCK,1)
            else:fcntl.flock(stream.fileno(),fcntl.LOCK_UN)


def train(dataset:Path,base_dir:Path,output:Path,*,seed:int=SEED,resume:bool=False,short_sampling:bool=False) -> TrainingReceipt:
    from transformers import AutoConfig,AutoTokenizer,AutoModelForSequenceClassification,Trainer,EarlyStoppingCallback,set_seed
    if seed!=SEED:raise ValueError('Do not search random seeds against held-out results')
    if type(short_sampling) is not bool:raise ValueError('The local control must be explicitly enabled')
    data=read_training_data(dataset);base=verify_base(base_dir)
    if not torch.cuda.is_available():raise RuntimeError('The approved full-parameter training requires measured local CUDA')
    doctor=json.loads((base_dir.parent/'doctor.json').read_text(encoding='utf-8'))
    probe=doctor.get('probe',{})
    if (doctor.get('revision')!=BASE_REVISION or doctor.get('base_files')!=base['files']
            or not probe.get('weights_discarded') or probe.get('trainable_parameters')!=probe.get('parameters')
            or probe.get('micro_batch') not in (1,2,4) or probe.get('effective_batch')!=16 or probe.get('max_tokens')!=128):
        raise ValueError('The full-parameter GPU preflight is missing or belongs to another base')
    identity=dict(dataset_hash=data.manifest_hash,augmentation_hash=data.augmentation_hash,base=BASE_MODEL,
        revision=BASE_REVISION,base_files=base['files'],seed=seed,config=CONFIG,
        micro_batch=probe['micro_batch'],lock_hash=file_hash(Path(__file__).with_name('uv.lock')),
        taxonomy_hash=default_taxonomy().digest,trainer_code_hash=file_hash(Path(__file__)))
    if short_sampling:
        from ml.topic_classifier.sampling import sampling_record,ShortSamplingTrainer
        identity['sampling']=sampling_record(data.train)
        identity['sampling_code_hash']=file_hash(Path(__file__).with_name('sampling.py'))
    config_hash=digest(identity);output=Path(output).resolve();output.mkdir(parents=True,exist_ok=True)
    lease=training_lease(output);lease.__enter__()
    started=time.monotonic()
    try:
        state_path=output/'run.json'
        if state_path.exists():
            if json.loads(state_path.read_text(encoding='utf-8'))!=identity:raise ValueError('Training data/config identity changed')
            if (output/'receipt.json').exists():raise ValueError('Completed training is immutable; do not rerun it')
            if not resume:raise ValueError('Interrupted training requires explicit same-data/config resume')
        else:
            if resume or any(output.glob('checkpoint-*')):raise ValueError('No bound training run exists for these checkpoints')
            _write(state_path,identity)
        if short_sampling:
            sampling_path=output/'sampling.json'
            if sampling_path.exists() and json.loads(sampling_path.read_text(encoding='utf-8'))!=identity['sampling']:
                raise ValueError('Frozen control sampling changed')
            if not sampling_path.exists():_write(sampling_path,identity['sampling'])
        set_seed(seed)
        tokenizer=AutoTokenizer.from_pretrained(base_dir,local_files_only=True,trust_remote_code=False)
        config=AutoConfig.from_pretrained(base_dir,local_files_only=True,trust_remote_code=False)
        if config.model_type!='bert' or config.hidden_size!=768 or config.num_hidden_layers!=12:
            raise ValueError('The approved fixed HFL architecture is required')
        taxonomy=default_taxonomy();config.num_labels=17;config.problem_type='multi_label_classification'
        config.id2label=dict(enumerate(taxonomy.ordered_names));config.label2id={name:i for i,name in config.id2label.items()}
        model=AutoModelForSequenceClassification.from_pretrained(base_dir,config=config,local_files_only=True,
            trust_remote_code=False,use_safetensors=False,weights_only=True)
        parameters=assert_full_trainable(model);before=encoder_hash(model)
        def collate(features):
            labels=torch.stack([row['labels'] for row in features])
            batch=tokenizer.pad([{k:v for k,v in row.items() if k!='labels'} for row in features],padding=True,return_tensors='pt')
            return dict(batch,labels=labels)
        trainer_class=ShortSamplingTrainer if short_sampling else Trainer
        trainer=trainer_class(model=model,args=training_arguments(output,probe['micro_batch']),processing_class=tokenizer,
            train_dataset=EncodedSamples(data.train,tokenizer),eval_dataset=EncodedSamples(data.validation,tokenizer),
            data_collator=collate,compute_metrics=compute_metrics,
            callbacks=[EarlyStoppingCallback(early_stopping_patience=CONFIG['patience'],early_stopping_threshold=CONFIG['minimum_improvement'])])
        checkpoints=sorted(output.glob('checkpoint-*'),key=lambda p:int(p.name.split('-')[-1]))
        if resume and not checkpoints:raise ValueError('No saved epoch checkpoint is available to resume')
        torch.cuda.reset_peak_memory_stats()
        trainer.train(resume_from_checkpoint=str(checkpoints[-1]) if resume else None)
        best=best_validation_epoch(trainer.state.log_history)
        if trainer.state.best_global_step!=best['step'] or abs(trainer.state.best_metric-best['eval_macro_f1'])>1e-12:
            raise ValueError('Trainer selected a different checkpoint from validation macro-F1 with earlier ties')
        best_source=Path(trainer.state.best_model_checkpoint or '').resolve()
        if best_source.parent!=output or not (best_source/'model.safetensors').is_file():
            raise ValueError('The validation-selected checkpoint is missing; never export different latest weights')
        after=encoder_hash(model)
        if after==before:raise ValueError('Encoder weights did not change; full fine-tuning was not demonstrated')
        best_dir=output/'best'
        if best_dir.exists():raise ValueError('Refuse to replace a prior best export')
        trainer.save_model(str(best_dir));tokenizer.save_pretrained(best_dir)
        if not (best_dir/'model.safetensors').is_file():raise ValueError('Best weights were not exported as safetensors')
        history=dict(config_hash=config_hash,dataset_hash=data.manifest_hash,epochs=trainer.state.log_history,
            best_epoch=best['epoch'],best_step=best['step'],best_macro_f1=best['eval_macro_f1'],
            best_source=str(best_source),best_source_weights_hash=file_hash(best_source/'model.safetensors'),
            parameters=parameters,trainable_parameters=assert_full_trainable(model),encoder_before=before,encoder_after=after,
            duration_seconds=time.monotonic()-started,finished_at=datetime.now(timezone.utc).isoformat(),
            peak_allocated_bytes=torch.cuda.max_memory_allocated(),peak_reserved_bytes=torch.cuda.max_memory_reserved(),
            stop_reason='early_stopping' if trainer.state.epoch<CONFIG['epochs'] else 'max_epochs',gpu=torch.cuda.get_device_name(0))
        _write(output/'history.json',history)
        fields=dict(best_checkpoint=str(best_dir),history_path=str(output/'history.json'),dataset_hash=data.manifest_hash,
            config_hash=config_hash,augmentation_hash=data.augmentation_hash,best_epoch=float(best['epoch']),
            best_macro_f1=float(best['eval_macro_f1']),encoder_before=before,encoder_after=after,
            weights_hash=file_hash(best_dir/'model.safetensors'),history_hash=file_hash(output/'history.json'))
        receipt=TrainingReceipt(**fields,receipt_hash=digest(fields));_write(output/'receipt.json',receipt.model_dump())
        return receipt
    except BaseException as exc:
        if not (output/'receipt.json').exists():
            _write(output/'interruption.json',dict(error_type=type(exc).__name__,config_hash=config_hash,
                duration_seconds=time.monotonic()-started,status='incomplete'))
        raise
    finally:lease.__exit__(None,None,None)
