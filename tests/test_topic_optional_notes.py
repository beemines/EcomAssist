"""Optional note representations preserve every word; labels and text stay strict."""
import pytest
from app.topics.teacher import parse_prelabels
from app.topics.cleaning import clean_question


def test_null_note_is_normalized_without_changing_text_or_labels():
    sample=clean_question('物流现在在哪里?',sample_id='q')
    rows=parse_prelabels(dict(items=[dict(id='q',cleaned_text=sample.text,labels=['物流'],notes=None)]),[sample])
    assert rows[0].notes=='' and rows[0].cleaned_text==sample.text and rows[0].labels==('物流',)


def test_string_list_notes_are_preserved_in_order_as_lines():
    sample=clean_question('物流?',sample_id='q')
    rows=parse_prelabels(dict(items=[dict(id='q',cleaned_text=sample.text,labels=['物流'],
        notes=['第一条说明','第二条说明'])]),[sample])
    assert rows[0].notes=='第一条说明\n第二条说明'


@pytest.mark.parametrize('value',[False,0,{},[False],['note',0],[['note']]])
def test_non_textual_note_content_stays_invalid(value):
    sample=clean_question('物流?',sample_id='q')
    with pytest.raises(ValueError):
        parse_prelabels(dict(items=[dict(id='q',cleaned_text=sample.text,labels=['物流'],notes=value)]),[sample])
