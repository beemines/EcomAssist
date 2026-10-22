"""Synthetic fixtures verify splitting contracts; they are never training evidence."""
import hashlib
from collections import Counter
import pytest
from app.topics.types import LabelledSample
from app.topics.taxonomy import default_taxonomy
from ml.topic_classifier.data import build_splits, validate_augmentation, write_dataset, load_dataset
from app.topics.grouping import group_samples


class Tokenizer:
    def __call__(self, text, **kwargs):
        assert kwargs.get('truncation') is False
        return {'input_ids': list(range(131 if text.startswith('OVERLONG') else len(text)+2))}


def sample(i, labels=('物流',), **changes):
    return LabelledSample(**(dict(id=f's-{i}',text='测试'+hashlib.sha256(str(i).encode()).hexdigest()[:24],
        labels=list(labels),origin='synthetic',group_id=f'g-{i}',source_question_ids=[],pilot=False)|changes))


def corpus(per_class=150):
    return [sample(f'{category}-{i}',(name,),pilot=i<2)
            for category,name in enumerate(default_taxonomy().ordered_names) for i in range(per_class)]


def test_same_family_cross_origin_synonyms_and_source_ids_stay_together():
    rows=[sample(1,text='请问快递现在在哪里?',origin='real',source_question_ids=['1']),
        sample(2,text='请问快递现在在哪儿?',origin='synthetic'),
        sample(3,text='同一逻辑原话另一版本',source_question_ids=['1']),
        sample(4,text='原家族扩写版本',group_id='g-1')]
    grouped=group_samples(rows)
    assert len(grouped.groups)==1 and len(grouped.samples)==4


def test_exact_duplicate_label_conflict_is_quarantined_and_probe_family_excluded():
    rows=[sample(1,text='包裹在哪',labels=['物流']),sample(2,text='包裹在哪',labels=['退换货']),
        sample(3,text='买大了想退',labels=['退换货','尺码']),sample(4,text='同一家族改写',group_id='g-3')]
    result=group_samples(rows)
    assert not result.samples
    assert Counter(row['reason'] for row in result.excluded)=={'conflicting_duplicate':2,'reserved_probe_family':2}


def test_deterministic_grouped_stratification_pilot_train_and_minimum_coverage(tmp_path):
    rows=corpus()
    manifest=build_splits(rows,Tokenizer())
    assert build_splits(list(reversed(rows)),Tokenizer()).model_dump()==manifest.model_dump()
    for name,fraction in [('train',.8),('validation',.1),('test',.1)]:
        assert abs(len(manifest.splits[name])/len(rows)-fraction)<=.03
    pilot={s.id for s in rows if s.pilot}
    assert pilot<=set(manifest.splits['train'])
    assert not (set(manifest.group_ids['train'])&set(manifest.group_ids['test']))
    assert not (set(manifest.group_ids['validation'])&set(manifest.group_ids['test']))
    for name in ('validation','test'):
        assert all(count['positive']>=10 and count['negative']>=10 for count in manifest.label_counts[name].values())
    write_dataset(rows,manifest,tmp_path)
    loaded=load_dataset(tmp_path)
    assert loaded.manifest_hash==manifest.manifest_hash
    (tmp_path/'test.jsonl').write_text('tampered',encoding='utf-8')
    with pytest.raises(ValueError): load_dataset(tmp_path)


def test_length_is_quarantined_before_freeze_and_real_groups_covered():
    rows=corpus()+[sample('long',text='OVERLONG'*35)]
    # Twenty independent true-source groups can be assigned without moving pilot families.
    rows=[s.model_copy(update={'origin':'real'}) if not s.pilot and i%80==0 else s for i,s in enumerate(rows)]
    manifest=build_splits(rows,Tokenizer())
    assert any(x['sample_id']=='s-long' and x['reason']=='overlength' for x in manifest.excluded)
    for name in ('validation','test'):
        assert manifest.origins[name].get('real',0)>0


def test_insufficient_coverage_and_impossible_group_ratios_fail():
    with pytest.raises(ValueError,match='coverage'):
        build_splits(corpus(30),Tokenizer())
    with pytest.raises(ValueError):
        build_splits([s.model_copy(update={'group_id':'one-family'}) for s in corpus(30)],Tokenizer())


def test_augmentation_preserves_parent_identity_requests_values_and_only_train(tmp_path):
    parent=sample(1,text='不要退货,只想修这台型号A12的机器',labels=['保修维修'])
    child=parent.model_copy(update={'id':parent.id+'-aug','text':'这台型号A12的机器不要退货,只想修'})
    validate_augmentation(parent,child)
    for bad in [child.model_copy(update={'labels':('退换货',)}),child.model_copy(update={'group_id':'wrong'}),
                child.model_copy(update={'text':'这台型号A12的机器想退货,不想修'}),
                child.model_copy(update={'text':child.text.replace('A12','A13')})]:
        with pytest.raises(ValueError): validate_augmentation(parent,bad)
    rows=corpus()
    manifest=build_splits(rows,Tokenizer())
    held=next(s for s in rows if s.id in manifest.splits['test'])
    augmented=held.model_copy(update={'id':held.id+'-aug','text':held.text+'呀'})
    with pytest.raises(ValueError,match='train'):
        write_dataset(rows,manifest,tmp_path,augmentations=[augmented])
