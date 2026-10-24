"""A corrected sampler cannot silently change or resend a prior paid request."""
from collections import Counter
import json
import pytest
from app.topics.corpus import _plan,_frozen_plan
from app.topics.reviews import digest
from app.topics.taxonomy import default_taxonomy


def counts():return Counter({name:30 for name in default_taxonomy().ordered_names if name!='其他'})


def test_new_other_scenes_do_not_force_a_product_business_ask(tmp_path):
    plan=_plan(16,counts(),80,focused_other=True)
    assert all(labels==('其他',) for labels in plan.scenario_labels)
    assert all('具体业务诉求' in hint for hint in plan.scenario_hints)
    assert not any('围绕家居' in hint or '围绕宠物' in hint for hint in plan.scenario_hints)


def test_existing_paid_stage_reconstructs_exact_legacy_plan_then_freezes_it(tmp_path):
    legacy=_plan(16,counts(),0);scope={'fixture':True}
    payload=dict(scope=scope,plan=legacy.model_dump(mode='json'))
    (tmp_path/'generate-0000.json').write_text(json.dumps(dict(state='complete',intent_hash=digest(payload))),encoding='utf-8')
    frozen=_frozen_plan(tmp_path,0,16,counts(),scope)
    assert frozen==legacy
    assert _frozen_plan(tmp_path,0,16,Counter(),scope)==legacy
    assert (tmp_path/'plan-0000.json').exists()


def test_new_stage_uses_corrected_plan_once_and_rejects_plan_tampering(tmp_path):
    scope={'fixture':True};plan=_frozen_plan(tmp_path,0,16,counts(),scope)
    assert plan==_plan(16,counts(),0,focused_other=True)
    assert _frozen_plan(tmp_path,0,16,Counter(),scope)==plan
    path=tmp_path/'plan-0000.json';record=json.loads(path.read_text(encoding='utf-8'))
    record['plan']['scenario_hints'][0]='tampered'
    path.write_text(json.dumps(record),encoding='utf-8')
    with pytest.raises(ValueError):_frozen_plan(tmp_path,0,16,counts(),scope)


def test_old_stage_with_unreconstructible_intent_is_never_reissued(tmp_path):
    (tmp_path/'generate-0000.json').write_text(json.dumps(dict(state='failed',intent_hash='0'*64)),encoding='utf-8')
    with pytest.raises(ValueError):_frozen_plan(tmp_path,0,16,counts(),{})
    assert not (tmp_path/'plan-0000.json').exists()
