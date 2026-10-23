"""Explicit offline ML commands, using local frozen model files only."""
import argparse
import json
import os
from pathlib import Path


def split_command(args):
    from transformers import AutoTokenizer
    from app.topics.budget import EVIDENCE_ROOT
    from app.topics.corpus import corpus_status
    from app.topics.types import LabelledSample
    from ml.topic_classifier.data import build_splits,write_dataset
    status=corpus_status(args.corpus)
    if status['status']!='complete': raise ValueError('Corpus is incomplete; do not freeze a smaller dataset silently')
    samples=[LabelledSample.model_validate_json(line) for line in (args.corpus/'samples.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    tokenizer=AutoTokenizer.from_pretrained(args.base_dir or EVIDENCE_ROOT/'base',local_files_only=True,trust_remote_code=False)
    manifest=build_splits(samples,tokenizer)
    write_dataset(samples,manifest,args.output)
    audit=dict(manifest_hash=manifest.manifest_hash,original_samples=len(samples),
        retained=sum(len(ids) for ids in manifest.splits.values()),
        sizes={name:len(ids) for name,ids in manifest.splits.items()},label_counts=manifest.label_counts,
        origins=manifest.origins,excluded=manifest.excluded,augmentation='pending')
    with (args.output/'data-audit.json').open('x',encoding='utf-8') as stream:
        json.dump(audit,stream,ensure_ascii=False,indent=2)
    print(json.dumps(audit,ensure_ascii=False))


def augmentation_command(args):
    from transformers import AutoTokenizer
    from app.topics.augmentation import load_augmentations
    from app.topics.budget import EVIDENCE_ROOT
    from app.topics.types import LabelledSample
    from ml.topic_classifier.data import load_dataset,freeze_augmentations
    manifest=load_dataset(args.dataset)
    status,children=load_augmentations(args.augmentations)
    if status['base_manifest_hash']!=manifest.manifest_hash: raise ValueError('Augmentation belongs to another dataset')
    samples=[LabelledSample.model_validate_json(line) for line in (args.corpus/'samples.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()]
    tokenizer=AutoTokenizer.from_pretrained(args.base_dir or EVIDENCE_ROOT/'base',local_files_only=True,trust_remote_code=False)
    result=freeze_augmentations(samples,manifest,children,tokenizer,args.dataset)
    print(json.dumps(dict(manifest_hash=result['manifest_hash'],augmentation=result['augmentation']),ensure_ascii=False))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    commands=parser.add_subparsers(dest='command',required=True)
    split=commands.add_parser('split',help='Freeze grouped 80/10/10 split after corpus preflight')
    split.add_argument('--corpus',type=Path,required=True)
    split.add_argument('--output',type=Path,required=True)
    split.add_argument('--base-dir',type=Path)
    augment=commands.add_parser('freeze-augmentation',help='Audit train-only children without changing held-out splits')
    augment.add_argument('--corpus',type=Path,required=True)
    augment.add_argument('--dataset',type=Path,required=True)
    augment.add_argument('--augmentations',type=Path,required=True)
    augment.add_argument('--base-dir',type=Path)
    iteration=commands.add_parser('freeze-remediation',help='Freeze approved pinned second-iteration data without reshuffling old validation')
    iteration.add_argument('--source',type=Path,required=True)
    iteration.add_argument('--iteration-root',type=Path,required=True)
    iteration.add_argument('--base-dir',type=Path,required=True)
    negation=commands.add_parser('freeze-negation',help='Freeze reviewed training and new independent validation/test without moving old data')
    negation.add_argument('--source',type=Path,required=True)
    negation.add_argument('--iteration-root',type=Path,required=True)
    negation.add_argument('--base-dir',type=Path,required=True)
    training=commands.add_parser('train',help='Full-parameter GPU training after frozen data/augmentation gates')
    training.add_argument('--dataset',type=Path,required=True)
    training.add_argument('--base-dir',type=Path,required=True)
    training.add_argument('--output',type=Path,required=True)
    training.add_argument('--resume',action='store_true',help='Only the same dataset/config and saved checkpoint')
    training.add_argument('--short-sampling-control',action='store_true',help='Approved local control: 30 percent short training draws, unchanged epoch length')
    evaluation=commands.add_parser('evaluate',help='Freeze validation thresholds, then evaluate held-out truth and prepare human review')
    evaluation.add_argument('--dataset',type=Path,required=True)
    evaluation.add_argument('--training',type=Path,required=True)
    evaluation.add_argument('--output',type=Path,required=True)
    evaluation.add_argument('--model-output',type=Path)
    evaluation.add_argument('--review-root',type=Path)
    evaluation.add_argument('--pilot-root',type=Path,help='Explicit unchanged original pilot for a new independently frozen iteration')
    finalize=commands.add_parser('finalize',help='Bind actual human review receipts to unchanged model/evaluation evidence')
    finalize.add_argument('--reports',type=Path,required=True)
    finalize.add_argument('--bundle',type=Path,required=True)
    finalize.add_argument('--review-root',type=Path,required=True)
    serve=commands.add_parser('serve',help='Serve one reviewed local CPU model, no downloads/database access')
    serve.add_argument('--bundle',type=Path,required=True)
    serve.add_argument('--host',choices=['127.0.0.1'],default='127.0.0.1')
    serve.add_argument('--port',type=int,choices=[8103],default=8103)
    args=parser.parse_args()
    # This CLI only consumes the already downloaded fixed model. Doctor owns downloads.
    os.environ['HF_HUB_OFFLINE']='1'
    os.environ['HF_HUB_DISABLE_TELEMETRY']='1'
    if args.command=='freeze-negation':
        from ml.topic_classifier.negation import freeze_negation
        print(json.dumps(freeze_negation(args.source,args.iteration_root,args.base_dir),ensure_ascii=False))
    elif args.command=='freeze-remediation':
        from ml.topic_classifier.remediation import freeze_iteration
        print(json.dumps(freeze_iteration(args.source,args.iteration_root,args.base_dir),ensure_ascii=False))
    elif args.command=='finalize':
        from ml.topic_classifier.artifacts import finalize_run
        print(json.dumps(finalize_run(args.reports,args.bundle,review_root=args.review_root),ensure_ascii=False))
    elif args.command=='serve':
        import uvicorn
        from ml.topic_classifier.service import create_app
        uvicorn.run(create_app(args.bundle),host=args.host,port=args.port,workers=1,access_log=False)
    elif args.command=='split': split_command(args)
    elif args.command=='freeze-augmentation': augmentation_command(args)
    elif args.command=='train':
        from ml.topic_classifier.train import train
        receipt=train(args.dataset,args.base_dir,args.output,resume=args.resume,short_sampling=args.short_sampling_control)
        print(receipt.model_dump_json(indent=2))
    elif args.command=='evaluate':
        from app.topics.review_submission import TopicReviewService
        from ml.topic_classifier.data import load_dataset
        from ml.topic_classifier.artifacts import evaluate_run
        pilot=TopicReviewService(args.pilot_root or args.dataset.parent/'pilot').state()
        scope=json.loads((args.dataset.parent/'corpus/run.json').read_text(encoding='utf-8'))
        manifest=load_dataset(args.dataset,splits=('train','validation'))
        if (pilot is None or pilot.receipt_hash!=scope.get('review_receipt_hash')
                or {row.id for row in pilot.samples}&(set(manifest.splits['validation'])|set(manifest.splits['test']))):
            raise ValueError('Actual frozen human pilot proof is required and its families cannot enter held-out splits')
        result=evaluate_run(args.dataset,args.training,args.output,pilot_receipt_hash=pilot.receipt_hash,
            model_output=args.model_output,review_root=args.review_root)
        print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__': main()
