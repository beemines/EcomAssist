"""Frozen batch scope and prediction identity are checked before DB writes."""
import pytest
from app.topics.batch import validate_predictions
from app.topics.repository import BatchPreview, PreparedQuestion, make_preview, verify_preview
from app.topics.types import ModelIdentity, Prediction
from app.topics.taxonomy import default_taxonomy
from app.topics.cleaning import CLEANING_VERSION


def identity():
    taxonomy = default_taxonomy()
    return ModelIdentity(model_version='fixture-v1',taxonomy_version=taxonomy.version,taxonomy_hash=taxonomy.digest,
                         cleaning_version=CLEANING_VERSION,max_tokens=128)


def preview():
    return make_preview(database_identity='a'*64,identity=identity(),from_id='41',to_id='42',high_water='42',
        reclassify=False,items=[PreparedQuestion(id='41',input_hash='b'*64,text='运费多少?',status='ready')])


def prediction(**change):
    return Prediction.model_validate(dict(id='41',labels=['运费'],probabilities=[.7]*17,status='classified',
        model_version='fixture-v1',taxonomy_version=default_taxonomy().version) | change)


@pytest.mark.parametrize('change', [dict(id='42'),dict(model_version='different'),dict(taxonomy_version='different')])
def test_batch_rejects_unrequested_id_or_prediction_version_drift(change):
    with pytest.raises(ValueError):
        validate_predictions(preview(), [prediction(**change)])


def test_batch_rejects_duplicate_predictions_or_modified_frozen_scope():
    with pytest.raises(ValueError):
        validate_predictions(preview(), [prediction(),prediction()])
    with pytest.raises(ValueError):
        verify_preview(preview().model_copy(update={'high_water':'100'}))
    checked=BatchPreview.model_validate_json(preview().model_dump_json())
    verify_preview(checked)


def test_uncertain_result_is_kept_as_uncertain_with_no_invented_label():
    rows=validate_predictions(preview(), [prediction(labels=[],status='needs_review')])
    assert rows[0].status=='needs_review' and not rows[0].labels
