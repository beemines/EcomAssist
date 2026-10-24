"""The shared taxonomy is the wire and training label contract."""

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.topics.taxonomy import load_taxonomy
from app.topics.types import LabelledSample, ModelIdentity, Prediction


TAXONOMY = Path(__file__).resolve().parents[1] / 'config/topic-taxonomy.json'
EXPECTED = ('退换货', '物流', '尺码', '发票', '质量问题', '运费', '优惠活动', '价保',
            '支付', '订单修改', '库存补货', '商品信息', '保修维修', '账号', '会员积分', '评价', '其他')


def test_taxonomy_order_and_reject_unknown():
    taxonomy = load_taxonomy(TAXONOMY)
    assert taxonomy.ordered_names == EXPECTED
    assert taxonomy.encode(('尺码', '退换货')) == (1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    assert taxonomy.canonical_labels(('尺码', '退换货')) == ('退换货', '尺码')
    for labels in (('未知',), ('物流', '物流'), ('其他', '物流'), (), '物流'):
        with pytest.raises(ValueError):
            taxonomy.canonical_labels(labels)
    assert len(taxonomy.digest) == 64
    assert taxonomy.version
    assert all(item.boundary.strip() for item in taxonomy.topics)


@pytest.mark.parametrize('change', ['index', 'name', 'blank', 'version', 'extra', 'schema_bool'])
def test_taxonomy_rejects_corrupt_definitions(tmp_path, change):
    value = json.loads(TAXONOMY.read_text(encoding='utf-8'))
    if change == 'index':
        value['topics'][0]['id'] = 2
    elif change == 'name':
        value['topics'][1]['name'] = value['topics'][0]['name']
    elif change == 'blank':
        value['topics'][0]['boundary'] = ' '
    elif change == 'version':
        value['version'] = ''
    elif change == 'extra':
        value['hidden_rule'] = 'unversioned'
    else:
        value['schema_version'] = True
    path = tmp_path / 'taxonomy.json'
    path.write_text(json.dumps(value, ensure_ascii=False), encoding='utf-8')
    with pytest.raises(ValueError):
        load_taxonomy(path)


def test_taxonomy_digest_tracks_boundary_and_ignores_json_whitespace(tmp_path):
    original = load_taxonomy(TAXONOMY)
    value = json.loads(TAXONOMY.read_text(encoding='utf-8'))
    path = tmp_path / 'taxonomy.json'
    path.write_text(json.dumps(value, indent=4), encoding='utf-8')
    assert load_taxonomy(path).digest == original.digest
    value['topics'][0]['boundary'] += ' 新增边界。'
    path.write_text(json.dumps(value), encoding='utf-8')
    assert load_taxonomy(path).digest != original.digest


def sample(**changes):
    return dict(id='synthetic-1', text='买大了想退', labels=['尺码', '退换货'], origin='synthetic',
                group_id='family-1', source_question_ids=[], pilot=True) | changes


def test_labelled_sample_preserves_origin_and_string_ids():
    row = LabelledSample.model_validate(sample())
    assert row.labels == ('退换货', '尺码')
    assert row.origin == 'synthetic'
    assert row.pilot is True
    actual = LabelledSample.model_validate(sample(id='pool-9007199254740993', origin='unverified',
        source_question_ids=['9007199254740993']))
    assert actual.source_question_ids == ('9007199254740993',)


@pytest.mark.parametrize('changes', [
    {'labels': ['其他', '尺码']}, {'labels': ['尺码', '尺码']}, {'labels': ['未知']},
    {'labels': []}, {'id': 1}, {'source_question_ids': [1]}, {'source_question_ids': ['01']},
    {'origin': 'real_customer_guessed'}, {'text': '  '}, {'pilot': 1}, {'group_id': ''},
])
def test_labelled_sample_rejects_ambiguous_data(changes):
    with pytest.raises(ValidationError):
        LabelledSample.model_validate(sample(**changes))


def prediction(**changes):
    return dict(id='9007199254740993', labels=['退换货', '尺码'], probabilities=[0.7] * 17,
                status='classified', model_version='model-v1', taxonomy_version='ch10-topics-v1') | changes


def test_prediction_accepts_json_arrays_without_numeric_id_coercion():
    row = Prediction.model_validate(prediction())
    assert row.id == '9007199254740993'
    assert row.labels == ('退换货', '尺码')
    assert len(row.probabilities) == 17
    assert Prediction.model_validate_json(row.model_dump_json()) == row


@pytest.mark.parametrize('bad', [True, float('nan'), float('inf'), -0.1, 1.1, '0.9', 10**1000])
def test_prediction_rejects_nonfinite_or_coerced_probabilities(bad):
    with pytest.raises(ValidationError):
        Prediction.model_validate(prediction(probabilities=[bad] + [0.1] * 16))


@pytest.mark.parametrize('changes', [
    {'probabilities': [0.1] * 16}, {'probabilities': None}, {'labels': []},
    {'labels': ['其他', '物流']}, {'labels': ['物流', '物流']}, {'labels': ['未知']},
    {'id': 9007199254740993}, {'model_version': ''}, {'taxonomy_version': ''},
    {'status': 'needs_review'}, {'status': 'input_too_long'},
])
def test_prediction_rejects_invalid_status_payload_combinations(changes):
    with pytest.raises(ValidationError):
        Prediction.model_validate(prediction(**changes))


def test_prediction_separates_uncertainty_and_input_errors():
    uncertain = Prediction.model_validate(prediction(labels=[], status='needs_review'))
    assert uncertain.labels == () and len(uncertain.probabilities) == 17
    error = Prediction.model_validate(prediction(labels=[], probabilities=None, status='input_too_long'))
    assert error.probabilities is None
    with pytest.raises(ValidationError):
        Prediction.model_validate(prediction(labels=[], probabilities=[0.0] * 17, status='invalid_input'))


def test_model_identity_is_bounded_and_exact():
    args = dict(model_version='model-v1', taxonomy_version='ch10-topics-v1',
                taxonomy_hash=load_taxonomy(TAXONOMY).digest, cleaning_version='clean-v1', max_tokens=128)
    assert ModelIdentity(**args).max_tokens == 128
    for changed in ({'max_tokens': True}, {'max_tokens': 127}, {'taxonomy_hash': 'x' * 64},
                    {'model_version': 'x' * 129}, {'cleaning_version': ''}):
        with pytest.raises(ValidationError):
            ModelIdentity(**(args | changed))
