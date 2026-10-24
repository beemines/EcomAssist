"""Deterministic data quotas; no inference or business-label prediction."""
from collections import Counter
import math
from app.topics.reviews import digest

VERSION='bounded-coverage-selection-v1'


def select_exact(rows,*,target,minima,multi_fraction,pinned_ids=()):
    if target<1 or any(n<0 or n>target for n in minima.values()) or not 0<=multi_fraction<=1:
        raise ValueError('Impossible exact data quota')
    candidates=tuple(sorted(rows,key=lambda r:digest(r.id)))
    by_group={}
    for row in candidates:by_group.setdefault(row.group_id,row)
    pins=set(pinned_ids);present={r.id for r in candidates}
    if not pins<=present or len(pins)>target:raise ValueError('Pinned data seed disappeared')
    chosen=[r for r in candidates if r.id in pins]
    if len({r.group_id for r in chosen})!=len(chosen):raise ValueError('Pinned seeds share a family')
    used={r.group_id for r in chosen};remaining=[r for r in by_group.values() if r.group_id not in used]
    counts=Counter(label for row in chosen for label in row.labels);multi=sum(len(r.labels)>1 for r in chosen)
    required_multi=math.ceil(target*multi_fraction)
    while remaining and len(chosen)<target:
        def gain(row):return sum(counts[label]<minima.get(label,0) for label in row.labels)+int(len(row.labels)>1 and multi<required_multi)
        best=max(remaining,key=gain)
        if not gain(best):break
        remaining.remove(best);chosen.append(best);counts.update(best.labels);multi+=len(best.labels)>1
    chosen.extend(remaining[:max(0,target-len(chosen))])
    return tuple(chosen),candidates


def candidate_rows(path,status,selected):
    from pathlib import Path
    from app.topics.types import LabelledSample
    if 'candidate_samples_hash' not in status:return tuple(selected)
    file=Path(path)/'qualified-candidates.jsonl'
    if file.is_symlink():raise ValueError('Invalid candidate file')
    content=file.read_text(encoding='utf-8')
    if digest(content)!=status['candidate_samples_hash']:raise ValueError('Frozen candidate content changed')
    rows=tuple(LabelledSample.model_validate_json(line) for line in content.splitlines())
    mapping={r.id:r for r in rows}
    if len(mapping)!=len(rows) or any(mapping.get(r.id)!=r for r in selected):raise ValueError('Selected candidate membership changed')
    return rows
