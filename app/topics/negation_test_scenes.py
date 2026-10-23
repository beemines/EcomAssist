"""Fresh independent tests mix short utterances and complete natural questions."""
import hashlib
from pathlib import Path
from app.topics.negation import source_context,negation_plan,protected_family
from app.topics.remediation import collect_short,load_short
from app.topics.taxonomy import default_taxonomy


def mixed_plan(count,positives,batch,*,partition):
    if partition!='test':raise ValueError('The mixed profile is only for independent tests')
    plan=negation_plan(count,positives,batch,partition=partition)
    return plan.model_copy(update={'scenario_hints':tuple(hint.replace('4至16字短口语','4至45字独立用户问题') for hint in plan.scenario_hints)})


async def prepare_test(source,teacher,*,output,partition='test',recovery=None):
    if partition!='test':raise ValueError('Only the new independent test partition may use this profile')
    scope,blocked=source_context(source);output=Path(output)
    for preceding in ('train','validation'):
        status,rows=load_short(output/(preceding+'-corpus'))
        scope[preceding+'_status_hash']=status['status_hash'];blocked+=rows
    await collect_short(teacher,output=output/'test-corpus',blocked=blocked,scope=scope,partition='test',target=187,
        minima={label:10 for label in default_taxonomy().ordered_names},multi_fraction=.25,recovery=recovery,
        planner=mixed_plan,row_guard=protected_family,
        profile=dict(version='ch10-negation-independent-mixed-v1',max_chars=45,generation_profile='mixed',
            code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            scene_code_sha256=hashlib.sha256(Path(__file__).with_name('negation.py').read_bytes()).hexdigest()))
    status,rows=load_short(output/'test-corpus')
    return dict(partition='test',status=status['status'],rows=len(rows),status_hash=status['status_hash'])
