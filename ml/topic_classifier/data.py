"""Frozen grouped multilabel splits. Test labels are never needed for training."""
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

import numpy as np
from iterstrat.ml_stratifiers import MultilabelStratifiedShuffleSplit

from app.topics.grouping import GROUPING_VERSION, group_samples, exact_text_key, validate_augmentation
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy
from app.topics.types import StrictRecord, LabelledSample

SEED = 20261021
SPLITS = ('train','validation','test')


class SplitManifest(StrictRecord):
    schema_version: int = 1
    seed: int
    taxonomy_hash: str
    grouping_version: str
    corpus_hash: str
    splits: dict[str,list[str]]
    group_ids: dict[str,list[str]]
    label_counts: dict[str,dict[str,dict[str,int]]]
    origins: dict[str,dict[str,int]]
    pilot_ids: list[str]
    excluded: list[dict]
    file_hashes: dict[str,str]
    manifest_hash: str


def _content(rows):
    return ''.join(row.model_dump_json()+'\n' for row in rows)


def _sha(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def build_splits(samples, tokenizer, *, seed=SEED) -> SplitManifest:
    if seed != SEED: raise ValueError('The approved seed is frozen; do not search seeds')
    original = sorted(samples,key=lambda row:row.id)
    grouped = group_samples(original)
    excluded = list(grouped.excluded)
    eligible = []
    for row in grouped.samples:
        tokens = tokenizer(row.text,truncation=False,add_special_tokens=True)['input_ids']
        if len(tokens)>128:
            excluded.append(dict(sample_id=row.id,reason='overlength'))
        else: eligible.append(row)
    by_group = defaultdict(list)
    for row in eligible: by_group[row.group_id].append(row)
    groups = sorted(by_group)
    fixed = {g for g in groups if any(row.pilot for row in by_group[g])}
    free = [g for g in groups if g not in fixed]
    held_each = round(len(groups)*.1)
    if held_each<1 or len(free)<=held_each*2:
        raise ValueError('Insufficient independent groups for split coverage')
    taxonomy = default_taxonomy()
    real_groups = {g for g in groups if any(row.origin=='real' for row in by_group[g])}
    def matrix(selected):
        result = []
        for g in selected:
            labels = {t for row in by_group[g] for t in row.labels}
            encoded = [int(t in labels) for t in taxonomy.ordered_names]
            if len(real_groups)>=5: encoded.append(int(g in real_groups))
            result.append(encoded)
        return np.asarray(result,dtype=int)
    first = MultilabelStratifiedShuffleSplit(n_splits=1,test_size=held_each*2,random_state=seed)
    train_idx,held_idx = next(first.split(np.zeros(len(free)),matrix(free)))
    held = [free[i] for i in held_idx]
    second = MultilabelStratifiedShuffleSplit(n_splits=1,test_size=held_each,random_state=seed)
    val_idx,test_idx = next(second.split(np.zeros(len(held)),matrix(held)))
    assigned = dict(train=sorted(fixed|{free[i] for i in train_idx}),
        validation=sorted(held[i] for i in val_idx),test=sorted(held[i] for i in test_idx))
    split_rows = {name:sorted((row for g in assigned[name] for row in by_group[g]),key=lambda row:row.id) for name in SPLITS}
    total = len(eligible)
    for name,target in [('train',.8),('validation',.1),('test',.1)]:
        if abs(len(split_rows[name])/total-target)>.03:
            raise ValueError('Split sample proportions exceed the approved tolerance')
    label_counts,origins = {},{}
    for name,rows in split_rows.items():
        counts = Counter(label for row in rows for label in row.labels)
        label_counts[name] = {label:dict(positive=counts[label],negative=len(rows)-counts[label]) for label in taxonomy.ordered_names}
        origins[name] = dict(Counter(row.origin for row in rows))
        if name != 'train':
            group_positive = Counter(label for g in assigned[name] for label in {t for row in by_group[g] for t in row.labels})
            if any(min(counts[label],len(rows)-counts[label],group_positive[label],len(assigned[name])-group_positive[label])<10
                    for label in taxonomy.ordered_names):
                raise ValueError('Held-out label coverage needs at least ten positive and negative independent groups per class')
            if len(real_groups)>=5 and not (set(assigned[name])&real_groups):
                raise ValueError('True-source groups lack held-out coverage')
    fields = dict(schema_version=1,seed=seed,taxonomy_hash=taxonomy.digest,grouping_version=GROUPING_VERSION,
        corpus_hash=digest([row.model_dump(mode='json') for row in original]),
        splits={name:[row.id for row in rows] for name,rows in split_rows.items()},group_ids=assigned,
        label_counts=label_counts,origins=origins,pilot_ids=sorted(row.id for row in eligible if row.pilot),
        excluded=sorted(excluded,key=lambda x:x['sample_id']),file_hashes={name:_sha(_content(rows)) for name,rows in split_rows.items()})
    return SplitManifest(**fields,manifest_hash=digest(fields))


def load_dataset(root: Path, *, splits=SPLITS) -> SplitManifest:
    root = Path(root)
    manifest = SplitManifest.model_validate_json((root/'manifest.json').read_text(encoding='utf-8'))
    fields = manifest.model_dump(mode='json');fields.pop('manifest_hash')
    if (digest(fields)!=manifest.manifest_hash or manifest.taxonomy_hash!=default_taxonomy().digest
            or manifest.seed!=SEED or set(manifest.splits)!=set(SPLITS)):
        raise ValueError('Dataset manifest identity changed')
    for name in splits:
        if name not in SPLITS: raise ValueError('Unknown split')
        content = (root/(name+'.jsonl')).read_text(encoding='utf-8')
        if _sha(content)!=manifest.file_hashes[name]: raise ValueError('Frozen split content changed')
    return manifest


def write_dataset(samples, manifest: SplitManifest, output: Path, *, augmentations=()):
    if digest([row.model_dump(mode='json') for row in sorted(samples,key=lambda row:row.id)])!=manifest.corpus_hash:
        raise ValueError('Corpus identity changed')
    grouped = group_samples(samples)
    mapping = {row.id:row for row in grouped.samples}
    train = set(manifest.splits['train'])
    children = sorted(augmentations,key=lambda row:row.id)
    seen = {exact_text_key(row.text) for row in grouped.samples}
    for child in children:
        parent = mapping.get(child.id.removesuffix('-aug'))
        if parent is None or parent.id not in train: raise ValueError('Only train parents can be augmented')
        validate_augmentation(parent,child)
        if exact_text_key(child.text) in seen: raise ValueError('Duplicate augmentation across splits')
        seen.add(exact_text_key(child.text))
    if len({row.id for row in children})!=len(children): raise ValueError('Duplicate augmentation ID')
    output = Path(output)
    output.mkdir(parents=True,exist_ok=True)
    if (output/'manifest.json').exists():
        if load_dataset(output).manifest_hash!=manifest.manifest_hash: raise ValueError('Refuse to replace frozen dataset')
    else:
        for name in SPLITS:
            content = _content([mapping[i] for i in manifest.splits[name]])
            if _sha(content)!=manifest.file_hashes[name]: raise ValueError('Split hash mismatch')
            with (output/(name+'.jsonl')).open('x',encoding='utf-8',newline='\n') as stream: stream.write(content)
        with (output/'manifest.json').open('x',encoding='utf-8') as stream: stream.write(manifest.model_dump_json(indent=2))
    if children:
        content = _content(children)
        audit = dict(base_manifest_hash=manifest.manifest_hash,count=len(children),content_hash=_sha(content),
            parent_ids=[row.id.removesuffix('-aug') for row in children])
        for filename,text in [('train-augmentations.jsonl',content),('augmentation.json',json.dumps(audit,ensure_ascii=False,sort_keys=True))]:
            path=output/filename
            if path.exists():
                if path.read_text(encoding='utf-8')!=text: raise ValueError('Refuse to replace frozen augmentation')
            else:
                with path.open('x',encoding='utf-8',newline='\n') as stream: stream.write(text)
    return manifest
