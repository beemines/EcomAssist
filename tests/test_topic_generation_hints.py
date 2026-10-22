"""Generated scene hints improve diversity without changing the allowed output contract."""
from pydantic import SecretStr
import pytest
from app.topics.teacher import TeacherClient,GenerationPlan
from app.topics.taxonomy import default_taxonomy


async def test_bounded_hint_is_input_only_and_cannot_override_generated_fields():
    plan=GenerationPlan(count=1,scenario_labels=[['物流']],taxonomy_hash=default_taxonomy().digest,
        scenario_hints=['大件家电送货预约；只问物流，避免重复上一批措辞'])
    async with TeacherClient(None,api_key=SecretStr('fixture-no-network')) as client:
        async def capture(stage,items,parse,**metadata):
            assert stage=='generate' and items[0]['scenario_hint']==plan.scenario_hints[0]
            expected=items[0]
            return parse(dict(items=[dict(id=expected['id'],family_id=expected['family_id'],
                requested_labels=expected['requested_labels'],text='大件家电能提前预约哪天送达吗?')]))
        client._call=capture
        rows=await client.generate(plan)
    assert rows[0].requested_labels==('物流',)


def test_scene_hints_reject_personal_data_before_transport():
    with pytest.raises(ValueError):
        GenerationPlan(count=1,scenario_labels=[['物流']],taxonomy_hash=default_taxonomy().digest,
            scenario_hints=['请联系手机号13800138000确认物流'])
