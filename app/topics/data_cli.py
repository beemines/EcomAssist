"""Explicit preparation commands; no imports start paid calls or background workers."""

import argparse
import asyncio
from collections import Counter
from difflib import SequenceMatcher
import hashlib
import json
import os
from pathlib import Path
import re
from uuid import uuid4

from app.topics.snapshot import SnapshotPreview, export_pool, preview_pool, write_new_json


def _atomic_json(path: Path, value):
    temporary = path.with_name(path.name + '.tmp')
    write_new_json(temporary, value)
    os.replace(temporary, path)


async def _checkpoint(name, intent, call, teacher, journal_dir, record_type, *, recovery=None):
    from app.topics.reviews import digest
    intent_hash = digest(intent)
    path = journal_dir / (name + '.json') if journal_dir is not None else None
    if path is not None and path.exists():
        saved = json.loads(path.read_text(encoding='utf-8'))
        if saved.get('intent_hash') != intent_hash:
            raise ValueError('Paid stage is incomplete or its frozen scope changed; no automatic repeat')
        if saved.get('state') == 'complete':
            expected_hash = saved.get('record_hash')
            if digest({key: value for key, value in saved.items() if key != 'record_hash'}) != expected_hash:
                raise ValueError('Paid-stage checkpoint was modified')
            rows = tuple(record_type.model_validate_json(json.dumps(row, ensure_ascii=False)) for row in saved['data'])
            receipt=saved['receipt']
            if saved.get('offline_revalidation',{}).get('quarantine'):
                receipt=receipt|{'offline_revalidation':saved['offline_revalidation']}
            return rows, receipt
        if saved.get('state')=='not_sent':
            if (set(saved)!={'state','intent_hash','error_class','receipt','record_hash'}
                    or saved['receipt'] is not None or saved['error_class']!='BudgetError'
                    or digest({key:value for key,value in saved.items() if key!='record_hash'})!=saved['record_hash']):
                raise ValueError('Unsent-stage proof is invalid; no repeat')
            write_new_json(path.with_name(f'{name}.unsent-{uuid4().hex}.json'),
                dict(prior=saved,reason='Explicit new execution after a guard proved no HTTP was sent'))
            _atomic_json(path,dict(state='in_flight',intent_hash=intent_hash))
        elif (saved.get('state') != 'failed' or not saved.get('receipt') or recovery is None
                or recovery[0] != name or type(recovery[1]) is not str or not recovery[1].strip()):
            raise ValueError('Paid stage is incomplete; explicit same-scope failed-stage recovery is required')
        else:
            write_new_json(path.with_name(f'{name}.recovery-{uuid4().hex}.json'),
                           dict(prior=saved, reason=recovery[1]))
            _atomic_json(path, dict(state='in_flight', intent_hash=intent_hash))
    if path is not None:
        if not path.exists():
            write_new_json(path, dict(state='in_flight', intent_hash=intent_hash))
    teacher.last_receipt = None
    try:
        result = await call()
    except BaseException as exc:
        if path is not None:
            from app.topics.budget import BudgetError
            unsent=isinstance(exc,BudgetError) and teacher.last_receipt is None
            saved=dict(state='not_sent' if unsent else 'failed',intent_hash=intent_hash,
                error_class=type(exc).__name__,receipt=teacher.last_receipt)
            if unsent:saved['record_hash']=digest(saved)
            _atomic_json(path,saved)
        raise
    saved = dict(state='complete', intent_hash=intent_hash, data=[row.model_dump(mode='json') for row in result],
                 receipt=teacher.last_receipt)
    if path is not None:
        _atomic_json(path, saved | {'record_hash': digest(saved)})
    return result, teacher.last_receipt


def _reserved_probe(text):
    normalized = re.sub(r'[\W_]+', '', text)
    reference = '买大了想退'
    return (reference in normalized or SequenceMatcher(None, normalized, reference).ratio() >= 0.82)


def _verify_snapshot(snapshot):
    from app.topics.cleaning import clean_question
    from app.topics.reviews import digest
    if (snapshot.snapshot_hash != digest([row.model_dump(mode='json') for row in snapshot.rows])
            or tuple(row.id for row in snapshot.rows) != snapshot.preview.ids
            or any(clean_question(row.raw_question, sample_id=row.cleaned.sample_id) != row.cleaned for row in snapshot.rows)):
        raise ValueError('Frozen snapshot hash or local cleaning results changed')


async def build_pilot(snapshot, teacher, *, count=68, journal_dir=None, recovery=None):
    from app.topics.cleaning import clean_question
    from app.topics.prompts import PROMPT_VERSION, system_prompt
    from app.topics.reviews import digest, make_review_pack
    from app.topics.taxonomy import default_taxonomy
    from app.topics.teacher import GeneratedQuestion, GenerationPlan, Prelabel
    from app.topics.types import LabelledSample
    if count != 68:
        raise ValueError('The approved pilot consists of 68 samples')
    _verify_snapshot(snapshot)
    taxonomy = default_taxonomy()
    scope = dict(snapshot_hash=snapshot.snapshot_hash, count=count, taxonomy_hash=taxonomy.digest,
        prompt_version=PROMPT_VERSION, prompt_hashes={stage: hashlib.sha256(system_prompt(stage).encode()).hexdigest()
                                                     for stage in ('generate', 'label')})
    if journal_dir is not None:
        run = journal_dir / 'run.json'
        if run.exists():
            if json.loads(run.read_text(encoding='utf-8'))['scope_hash'] != digest(scope):
                raise ValueError('Pilot journal belongs to a different frozen preparation')
        else:
            write_new_json(run, dict(scope_hash=digest(scope), scope=scope,
                                    budget_before=teacher.ledger.summary().model_dump()))
    families = {}
    for row in snapshot.rows:
        if row.cleaned.quarantine_reasons or _reserved_probe(row.cleaned.text):
            continue
        key = hashlib.sha256(row.cleaned.text.encode()).hexdigest()
        families.setdefault(key, []).append(row)
    # Cap pool contribution so a small, skewed historical pool cannot crowd out
    # the taxonomy coverage and at least 17 multi-request examples in this audit.
    selected = list(families.items())[:20]
    samples, receipts, notes, scenarios = [], [], {}, {}
    for start in range(0, len(selected), 16):
        batch = selected[start:start+16]
        cleaned = [rows[0].cleaned for _, rows in batch]
        labelled, receipt = await _checkpoint(f'label-pool-{start:03}',
            dict(scope=scope, samples=[row.model_dump(mode='json') for row in cleaned]),
            lambda cleaned=cleaned: teacher.label(cleaned), teacher, journal_dir, Prelabel, recovery=recovery)
        receipts.append(receipt)
        for (key, rows), label in zip(batch, labelled, strict=True):
            samples.append(LabelledSample(id=label.id, text=label.cleaned_text, labels=label.labels,
                origin='unverified', group_id='pool-family-' + key[:32], source_question_ids=[row.id for row in rows], pilot=True))
            notes[label.id] = label.notes
    needed = count - len(samples)
    requested = [(name,) for name in taxonomy.ordered_names]
    for index in range(needed - len(requested)):
        left, right = index % 16, (index * 7 + 3) % 16
        if left == right:
            right = (right + 1) % 16
        requested.append(taxonomy.canonical_labels((taxonomy.ordered_names[left], taxonomy.ordered_names[right])))
    generated = []
    for start in range(0, needed, 16):
        labels = requested[start:start+16]
        plan = GenerationPlan(count=len(labels), scenario_labels=labels, taxonomy_hash=taxonomy.digest)
        rows, receipt = await _checkpoint(f'generate-{start:03}', dict(scope=scope, plan=plan.model_dump(mode='json')),
            lambda plan=plan: teacher.generate(plan), teacher, journal_dir, GeneratedQuestion, recovery=recovery)
        generated.extend(rows)
        receipts.append(receipt)
    seen = {sample.text for sample in samples}
    eligible = []
    for row in generated:
        if row.text not in seen and not _reserved_probe(row.text):
            eligible.append(row)
            seen.add(row.text)
    for start in range(0, len(eligible), 16):
        batch = eligible[start:start+16]
        cleaned = [clean_question(row.text, sample_id=row.id) for row in batch]
        labelled, receipt = await _checkpoint(f'label-generated-{start:03}',
            dict(scope=scope, samples=[row.model_dump(mode='json') for row in cleaned]),
            lambda cleaned=cleaned: teacher.label(cleaned), teacher, journal_dir, Prelabel, recovery=recovery)
        receipts.append(receipt)
        for parent, label in zip(batch, labelled, strict=True):
            samples.append(LabelledSample(id=label.id, text=label.cleaned_text, labels=label.labels,
                origin='synthetic', group_id=parent.family_id, source_question_ids=[], pilot=True))
            notes[label.id] = label.notes
            scenarios[label.id] = parent.requested_labels
    return make_review_pack(samples, snapshot_hash=snapshot.snapshot_hash, teacher_receipts=receipts,
                            annotation_notes=notes, scenario_labels=scenarios)


def _coverage(pack):
    from app.topics.taxonomy import default_taxonomy
    counts = Counter(label for sample in pack.samples for label in sample.labels)
    multi = sum(len(sample.labels) > 1 for sample in pack.samples)
    return dict(samples=len(pack.samples), target=68, label_counts=dict(counts),
        missing_labels=[name for name in default_taxonomy().ordered_names if not counts[name]],
        multi_request=multi, required_multi_request=17,
        complete=len(pack.samples) == 68 and multi >= 17 and len(counts) == 17,
        origins=dict(Counter(sample.origin for sample in pack.samples)))


async def pilot_command(args):
    from app.config import load_settings
    from app.topics.budget import APPROVAL_ID, BUDGET_PATH, BudgetLedger
    from app.topics.reviews import render_review_html
    from app.topics.snapshot import PoolSnapshot
    from app.topics.teacher import configured_teacher
    snapshot = PoolSnapshot.model_validate_json(args.snapshot.read_text(encoding='utf-8'))
    _verify_snapshot(snapshot)
    ledger = BudgetLedger(BUDGET_PATH, APPROVAL_ID)
    retry_stage, retry_reason = args.retry_failed_stage, args.retry_reason
    if (bool(retry_stage) != bool(retry_reason) or (retry_stage and
            (not args.execute or not re.fullmatch(r'(label-pool|generate|label-generated)-[0-9]{3}', retry_stage)
             or not retry_reason.strip() or len(retry_reason) > 512))):
        raise ValueError('Recovery needs --execute, one exact failed stage and a nonblank diagnostic reason')
    if not args.execute:
        print(json.dumps(dict(mode='preview', snapshot_rows=len(snapshot.rows), target=68,
            quarantined=sum(bool(row.cleaned.quarantine_reasons) for row in snapshot.rows),
            budget=ledger.summary().model_dump()), ensure_ascii=False))
        return
    settings = load_settings(env_file=os.environ.get('CH10_ENV_FILE', '.env'))
    async with configured_teacher(settings, ledger, evidence_dir=args.output/'diagnostics') as teacher:
        pack = await build_pilot(snapshot, teacher, journal_dir=args.output/'journal',
                                 recovery=(retry_stage, retry_reason) if retry_stage else None)
    outputs = {'pack.json': pack.model_dump(mode='json'), 'coverage.json': _coverage(pack),
               'budget.json': ledger.summary().model_dump()}
    for name, value in outputs.items():
        path = args.output/name
        if path.exists():
            if name == 'pack.json' and json.loads(path.read_text(encoding='utf-8'))['pack_hash'] != pack.pack_hash:
                raise ValueError('Existing review pack must not be overwritten')
        else:
            write_new_json(path, value)
    html = args.output/'review.html'
    if not html.exists():
        html.write_text(render_review_html(pack), encoding='utf-8')
    data = args.output/'samples.jsonl'
    if not data.exists():
        with data.open('x', encoding='utf-8', newline='\n') as stream:
            stream.writelines(sample.model_dump_json()+'\n' for sample in pack.samples)
    decisions = args.output/'decisions.jsonl'
    if not decisions.exists():
        with decisions.open('x', encoding='utf-8', newline='\n') as stream:
            for sample in pack.samples:
                stream.write(json.dumps(dict(sample_id=sample.id, pack_hash=pack.pack_hash, decision=None,
                    final_labels=list(sample.labels), reviewer='', reviewed_at=None, notes=''), ensure_ascii=False)+'\n')
    print(json.dumps(dict(coverage=_coverage(pack), pack_hash=pack.pack_hash,
                         budget=ledger.summary().model_dump(), status='awaiting_human_review'), ensure_ascii=False))


async def expand_command(args):
    from app.config import load_settings
    from app.topics.budget import APPROVAL_ID,BUDGET_PATH,BudgetLedger
    from app.topics.corpus import expand_corpus,corpus_status
    from app.topics.review_submission import TopicReviewService
    from app.topics.snapshot import PoolSnapshot
    from app.topics.teacher import configured_teacher
    service=TopicReviewService(args.pilot_receipt.parent)
    if args.pilot_receipt.resolve()!=(service.root/'review-receipt.json').resolve():
        raise ValueError('Select the original human receipt filename')
    review=service.state()
    if review is None: raise ValueError('Actual pilot human review is still missing')
    snapshot=PoolSnapshot.model_validate_json(args.snapshot.read_text(encoding='utf-8'))
    _verify_snapshot(snapshot)
    if service.pack().snapshot_hash!=snapshot.snapshot_hash:
        raise ValueError('Human review belongs to another pool snapshot')
    ledger=BudgetLedger(BUDGET_PATH,APPROVAL_ID)
    if not args.execute:
        print(json.dumps(dict(mode='preview',human_review=review.receipt_hash,pilot_retained=len(review.samples),
            target_groups=2040,minimum_per_class=100,budget=ledger.summary().model_dump()),ensure_ascii=False));return
    retry=args.retry_failed_stage;reason=args.retry_reason
    if bool(retry)!=bool(reason) or retry and (not re.fullmatch(r'(generate|label)-[0-9]{4}',retry) or not reason.strip() or len(reason)>512):
        raise ValueError('Recovery requires one diagnosed failed stage and explicit reason')
    settings=load_settings(env_file=os.environ.get('CH10_ENV_FILE','.env'))
    args.output.mkdir(parents=True,exist_ok=True)
    async with configured_teacher(settings,ledger,evidence_dir=args.output/'diagnostics') as teacher:
        await expand_corpus(snapshot,review,teacher,output=args.output,recovery=(retry,reason) if retry else None,
            progress=lambda value:print(json.dumps(value,ensure_ascii=False),flush=True))
    result=corpus_status(args.output)
    print(json.dumps(dict(status=result['status'],groups=result['independent_groups'],budget=result['budget']),ensure_ascii=False))
    if result['status']!='complete': raise SystemExit(2)


async def augment_command(args):
    from app.config import load_settings
    from app.topics.augmentation import select_train_parents,augment_training,load_augmentations
    from app.topics.budget import APPROVAL_ID,BUDGET_PATH,BudgetLedger
    from app.topics.teacher import configured_teacher
    parents,manifest=select_train_parents(args.dataset)
    ledger=BudgetLedger(BUDGET_PATH,APPROVAL_ID)
    if not args.execute:
        print(json.dumps(dict(mode='preview',base_manifest_hash=manifest['manifest_hash'],train_parents=len(parents),
            maximum_children_per_parent=1,budget=ledger.summary().model_dump()),ensure_ascii=False));return
    retry=args.retry_failed_stage;reason=args.retry_reason
    if bool(retry)!=bool(reason) or retry and (not re.fullmatch(r'augment-[0-9]{4}',retry) or not reason.strip() or len(reason)>512):
        raise ValueError('Recovery requires one diagnosed failed augmentation and explicit reason')
    settings=load_settings(env_file=os.environ.get('CH10_ENV_FILE','.env'))
    async with configured_teacher(settings,ledger,evidence_dir=args.output/'diagnostics') as teacher:
        await augment_training(args.dataset,teacher,output=args.output,recovery=(retry,reason) if retry else None)
    result,_=load_augmentations(args.output)
    print(json.dumps(dict(status=result['status'],accepted=result['accepted'],selected=result['selected'],
        budget=ledger.summary().model_dump()),ensure_ascii=False))


async def remediate_command(args):
    from app.config import load_settings
    from app.topics.remediation import original_source,prepare_remediation
    from app.topics.budget import BudgetLedger,BUDGET_PATH,APPROVAL_ID,REMEDIATION_APPROVAL_ID
    from app.topics.teacher import configured_teacher
    ledger=BudgetLedger(BUDGET_PATH,APPROVAL_ID)
    if ledger.summary().approval_revision!=REMEDIATION_APPROVAL_ID:raise ValueError('Explicit450/10CNY remediation approval required')
    manifest,_,_=original_source(args.source)
    if not args.execute:
        print(json.dumps(dict(mode='preview',source_manifest=manifest['manifest_hash'],new_train_target=128,new_test_target=187,
            external_data='new_synthetic_questions_and_taxonomy_only',budget=ledger.summary().model_dump()),ensure_ascii=False));return
    if bool(args.retry_failed_stage)!=bool(args.retry_reason) or args.retry_failed_stage and (
            not re.fullmatch(r'(train|test)-(generate|label)-[0-9]{4}',args.retry_failed_stage) or not args.retry_reason.strip()
            or len(args.retry_reason)>512):raise ValueError('One diagnosed stage and bounded reason are required')
    recovery=(args.retry_failed_stage,args.retry_reason) if args.retry_failed_stage else None
    settings=load_settings(env_file=os.environ.get('CH10_ENV_FILE','.env'))
    async with configured_teacher(settings,ledger,evidence_dir=args.output/'teacher-diagnostics') as teacher:
        result=await prepare_remediation(args.source,teacher,output=args.output,recovery=recovery)
    print(json.dumps(result|dict(budget=ledger.summary().model_dump()),ensure_ascii=False))


async def negation_command(args):
    from app.config import load_settings
    from app.topics.negation import source_context,prepare_partition
    from app.topics.budget import BudgetLedger,BUDGET_PATH,APPROVAL_ID,NEGATION_APPROVAL_ID,EVIDENCE_ROOT
    from app.topics.teacher import configured_teacher
    ledger=BudgetLedger(BUDGET_PATH,APPROVAL_ID)
    if ledger.summary().approval_revision!=NEGATION_APPROVAL_ID:raise ValueError('Explicit500/10CNY authorization required')
    scope,_=source_context(args.source)
    if not args.execute:
        print(json.dumps(dict(mode='preview',partition=args.partition,source_manifest=scope['source_manifest_hash'],
            target=187 if args.partition=='test' else 64,external_data='new_synthetic_questions_and_taxonomy_only',
            budget=ledger.summary().model_dump()),ensure_ascii=False));return
    if args.output.resolve()!=(EVIDENCE_ROOT/'negation-v4').resolve():raise ValueError('Use the independent negation-v4 output')
    if bool(args.retry_failed_stage)!=bool(args.retry_reason) or args.retry_failed_stage and (
            not re.fullmatch(r'(train|validation|test)-(generate|label)-[0-9]{4}',args.retry_failed_stage)
            or not args.retry_reason.strip() or len(args.retry_reason)>512):raise ValueError('One diagnosed stage and bounded reason required')
    settings=load_settings(env_file=os.environ.get('CH10_ENV_FILE','.env'))
    recovery=(args.retry_failed_stage,args.retry_reason) if args.retry_failed_stage else None
    async with configured_teacher(settings,ledger,evidence_dir=args.output/'teacher-diagnostics') as teacher:
        if args.partition=='test':
            from app.topics.negation_test_scenes import prepare_test
            result=await prepare_test(args.source,teacher,output=args.output,recovery=recovery)
        else:result=await prepare_partition(args.source,teacher,output=args.output,partition=args.partition,recovery=recovery)
    print(json.dumps(result|dict(budget=ledger.summary().model_dump()),ensure_ascii=False))


def review_command(args):
    from app.topics.reviews import ReviewPack, apply_review, load_decisions
    pack = ReviewPack.model_validate_json(args.pack.read_text(encoding='utf-8'))
    receipt = apply_review(pack, load_decisions(args.decisions))
    if args.execute:
        write_new_json(args.output, receipt.model_dump(mode='json'))
    print(json.dumps(dict(mode='execute' if args.execute else 'preview', accepted=len(receipt.samples),
        excluded=len(receipt.excluded_ids), receipt_hash=receipt.receipt_hash), ensure_ascii=False))


async def snapshot_command(args):
    from app.config import load_settings
    from app.db.session import Database
    settings = load_settings(env_file=os.environ.get('CH10_ENV_FILE', '.env'))
    database = Database(settings.database_url)
    try:
        if args.execute:
            if args.preview_file is None or args.preview:
                raise ValueError('Execute needs --preview-file and no --preview')
            if args.from_id != 1 or args.to_id is not None or args.limit != 100:
                raise ValueError('Execute uses the exact saved preview; omit new range flags')
            preview = SnapshotPreview.model_validate_json(args.preview_file.read_text(encoding='utf-8'))
            snapshot = await export_pool(database, preview, args.output)
            summary = dict(rows=len(snapshot.rows), unique_texts=len({row.cleaned.input_hash for row in snapshot.rows}),
                origins=dict(Counter(row.origin for row in snapshot.rows)),
                sources=dict(Counter(row.source for row in snapshot.rows)),
                quarantined=sum(bool(row.cleaned.quarantine_reasons) for row in snapshot.rows),
                snapshot_hash=snapshot.snapshot_hash)
        else:
            if args.preview_file is not None:
                raise ValueError('--preview-file is used only with --execute')
            preview = await preview_pool(database, from_id=args.from_id, to_id=args.to_id, limit=args.limit)
            write_new_json(args.output, preview.model_dump(mode='json'))
            summary = dict(rows=len(preview.ids), from_id=preview.from_id, high_water=preview.high_water,
                           fingerprint=preview.fingerprint, mode='preview')
        print(json.dumps(summary, ensure_ascii=False))
    finally:
        await database.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    budget_init = commands.add_parser('budget-init', help='Preview or initialize the single approved CNY10 ledger')
    budget_init.add_argument('--execute', action='store_true')
    commands.add_parser('budget-status', help='Read existing budget; never create or reset it')
    budget_amend=commands.add_parser('budget-extend-attempts',help='Append recognized human 400-attempt approval; money cap unchanged')
    budget_amend.add_argument('--authorization-id',required=True)
    budget_amend.add_argument('--execute',action='store_true')
    corpus_status_parser=commands.add_parser('corpus-status',help='Read verified corpus progress without starting a teacher')
    corpus_status_parser.add_argument('--corpus',type=Path,required=True)
    pilot = commands.add_parser('pilot', help='Prepare the 68-item audit; preview is free')
    pilot.add_argument('--snapshot', type=Path, required=True)
    pilot.add_argument('--output', type=Path, required=True)
    pilot.add_argument('--execute', action='store_true')
    pilot.add_argument('--retry-failed-stage', help='One diagnosed failed checkpoint; never retries in-flight calls')
    pilot.add_argument('--retry-reason', help='Explicit diagnosis, preserved with the prior failed receipt')
    expand=commands.add_parser('expand',help='Expand only after the human pilot receipt; preview is free')
    expand.add_argument('--pilot-receipt',type=Path,required=True)
    expand.add_argument('--snapshot',type=Path,required=True)
    expand.add_argument('--output',type=Path,required=True)
    expand.add_argument('--execute',action='store_true')
    expand.add_argument('--retry-failed-stage')
    expand.add_argument('--retry-reason')
    augment=commands.add_parser('augment',help='Augment only frozen train groups; preview is free')
    augment.add_argument('--dataset',type=Path,required=True)
    augment.add_argument('--output',type=Path,required=True)
    augment.add_argument('--execute',action='store_true')
    augment.add_argument('--retry-failed-stage')
    augment.add_argument('--retry-reason')
    remediate=commands.add_parser('remediate',help='Approved synthetic-only short-input iteration; preview by default')
    remediate.add_argument('--source',type=Path,required=True)
    remediate.add_argument('--output',type=Path,required=True)
    remediate.add_argument('--execute',action='store_true')
    remediate.add_argument('--retry-failed-stage')
    remediate.add_argument('--retry-reason')
    negation=commands.add_parser('prepare-negation',help='Approved synthetic negation data, with an actual human training review gate')
    negation.add_argument('--source',type=Path,required=True)
    negation.add_argument('--output',type=Path,required=True)
    negation.add_argument('--partition',choices=['train','validation','test'],default='train')
    negation.add_argument('--execute',action='store_true')
    negation.add_argument('--retry-failed-stage')
    negation.add_argument('--retry-reason')
    review = commands.add_parser('review-import', help='Validate explicit human decisions, then save a receipt')
    review.add_argument('--pack', type=Path, required=True)
    review.add_argument('--decisions', type=Path, required=True)
    review.add_argument('--output', type=Path, required=True)
    review.add_argument('--execute', action='store_true')
    snapshot = commands.add_parser('snapshot', help='Preview, then export a bounded read-only pool snapshot')
    snapshot.add_argument('--database', choices=['configured'], default='configured')
    snapshot.add_argument('--from-id', type=int, default=1)
    snapshot.add_argument('--to-id', type=int)
    snapshot.add_argument('--limit', type=int, default=100)
    snapshot.add_argument('--preview', action='store_true')
    snapshot.add_argument('--execute', action='store_true')
    snapshot.add_argument('--preview-file', type=Path)
    snapshot.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command.startswith('budget-'):
        from app.topics.budget import APPROVAL_ID, BUDGET_PATH, LIMIT_MICRO, MAX_ATTEMPTS, BudgetLedger, initialize_budget
        if args.command == 'budget-init':
            if not args.execute:
                print(json.dumps(dict(mode='preview', approval_id=APPROVAL_ID,
                    limit_micro=LIMIT_MICRO, maximum_physical_attempts=MAX_ATTEMPTS,
                    path=str(BUDGET_PATH)), ensure_ascii=False))
                return
            initialize_budget(BUDGET_PATH, APPROVAL_ID)
        elif args.command=='budget-extend-attempts':
            from app.topics.budget import amend_budget_attempt_limit,ATTEMPT_EXTENSION_TEXT
            if not args.execute:
                print(json.dumps(dict(mode='preview',proposed_attempt_limit=400,money_limit_micro=LIMIT_MICRO,
                    current=BudgetLedger(BUDGET_PATH,APPROVAL_ID).summary().model_dump()),ensure_ascii=False));return
            amend_budget_attempt_limit(BUDGET_PATH,revision_id=args.authorization_id,approval_text=ATTEMPT_EXTENSION_TEXT)
        print(BudgetLedger(BUDGET_PATH, APPROVAL_ID).summary().model_dump_json())
    elif args.command == 'pilot':
        asyncio.run(pilot_command(args))
    elif args.command == 'expand':
        asyncio.run(expand_command(args))
    elif args.command == 'augment':
        asyncio.run(augment_command(args))
    elif args.command == 'remediate':
        asyncio.run(remediate_command(args))
    elif args.command == 'prepare-negation':
        asyncio.run(negation_command(args))
    elif args.command == 'corpus-status':
        from app.topics.corpus import corpus_status
        from app.topics.budget import APPROVAL_ID,BUDGET_PATH,BudgetLedger
        value=corpus_status(args.corpus)
        print(json.dumps({key:value[key] for key in ('status','raw_samples','independent_groups','positive_groups','multi_groups')}
            |dict(quarantined=len(value['quarantine']),budget_current=BudgetLedger(BUDGET_PATH,APPROVAL_ID).summary().model_dump()),ensure_ascii=False))
    elif args.command == 'review-import':
        review_command(args)
    else:
        asyncio.run(snapshot_command(args))


if __name__ == '__main__':
    main()
