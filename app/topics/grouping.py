"""Conservative text/family grouping shared by corpus preparation and split audit."""
from collections import Counter, defaultdict
from dataclasses import dataclass
from difflib import SequenceMatcher
import re
import unicodedata

from app.topics.reviews import digest
from app.topics.types import LabelledSample

GROUPING_VERSION = 'ch10-groups-v1'


def text_key(text):
    value = unicodedata.normalize('NFKC', text).lower()
    for pattern, replacement in [('在哪里|在哪儿|在哪','位置'),('退钱','退款'),
            ('咋办|如何操作','怎么办'),('多长时间','多久')]:
        value = re.sub(pattern, replacement, value)
    return re.sub(r'[^\w\u4e00-\u9fff]', '', value)


def exact_text_key(text):
    return re.sub(r'[^\w\u4e00-\u9fff]', '', unicodedata.normalize('NFKC',text).lower())


def reserved_probe(text):
    value = text_key(text)
    return '买大了想退' in value or SequenceMatcher(None,value,'买大了想退').ratio() >= .82


@dataclass(frozen=True)
class GroupedSamples:
    samples: tuple[LabelledSample, ...]
    groups: dict[str, tuple[str, ...]]
    excluded: tuple[dict, ...]


def group_samples(samples) -> GroupedSamples:
    rows = sorted((LabelledSample.model_validate(row.model_dump()) for row in samples),key=lambda row:row.id)
    if len({row.id for row in rows}) != len(rows):
        raise ValueError('Duplicate sample IDs')
    parents = list(range(len(rows)))
    def find(i):
        while parents[i] != i:
            parents[i] = parents[parents[i]]
            i = parents[i]
        return i
    def join(i,j):
        left,right = find(i),find(j)
        if left != right:
            parents[max(left,right)] = min(left,right)
    families, sources, exact, keys = {}, {}, defaultdict(list), []
    for i,row in enumerate(rows):
        key = text_key(row.text)
        keys.append(key)
        exact_key = exact_text_key(row.text)
        if exact[exact_key]: join(i,exact[exact_key][0])
        exact[exact_key].append(i)
        if row.group_id in families: join(i,families[row.group_id])
        families[row.group_id] = i
        for source in row.source_question_ids:
            if source in sources: join(i,sources[source])
            sources[source] = i
    # Do not drop negations or numbers. Borderline similarities merge families
    # conservatively, never invent a new label or treat a request batch as a family.
    index = defaultdict(set)
    for i,key in enumerate(keys):
        grams = {key[k:k+3] for k in range(max(0,len(key)-2))}
        candidates = Counter(j for gram in grams for j in index[gram])
        for j,shared in candidates.items():
            other = keys[j]
            if find(i)==find(j): continue
            if key == other:
                join(i,j)
            elif (len(key)>=10 and len(other)>=10 and shared>=max(1,(min(len(key),len(other))-2)*.35)
                    and min(len(key),len(other))/max(len(key),len(other))>=.90):
                match = SequenceMatcher(None,key,other,autojunk=False)
                if match.quick_ratio()>=.90 and match.ratio()>=.90: join(i,j)
        for gram in grams: index[gram].add(i)
    probe_roots = {find(i) for i,row in enumerate(rows) if reserved_probe(row.text)}
    excluded, skip, replacements = [], set(), {}
    for indices in exact.values():
        if len({rows[i].labels for i in indices}) > 1:
            for i in indices:
                skip.add(i); excluded.append(dict(sample_id=rows[i].id,reason='conflicting_duplicate'))
        elif len(indices)>1:
            first = min(indices,key=lambda i:(not rows[i].pilot,rows[i].origin!='real',rows[i].id))
            replacements[first] = rows[first].model_copy(update={'source_question_ids':tuple(sorted({
                q for i in indices for q in rows[i].source_question_ids},key=int))})
            for i in indices:
                if i != first:
                    skip.add(i);excluded.append(dict(sample_id=rows[i].id,reason='exact_duplicate'))
    components = defaultdict(list)
    for i,row in enumerate(rows): components[find(i)].append(row.id)
    identities = {root:'grp-'+digest(ids)[:32] for root,ids in components.items()}
    output, groups = [], defaultdict(list)
    for i,row in enumerate(rows):
        if i in skip: continue
        if find(i) in probe_roots:
            excluded.append(dict(sample_id=row.id,reason='reserved_probe_family'));continue
        group = identities[find(i)]
        item = replacements.get(i,row).model_copy(update={'group_id':group})
        output.append(item);groups[group].append(item.id)
    return GroupedSamples(tuple(output),{group:tuple(ids) for group,ids in sorted(groups.items())},
        tuple(sorted(excluded,key=lambda x:x['sample_id'])))
