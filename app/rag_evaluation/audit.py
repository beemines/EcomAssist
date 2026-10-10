"""只保存可公开的冻结证据、准确金标和实际排序；不参与生成输入。"""

from collections.abc import Mapping
import copy
from dataclasses import asdict
import hashlib
import json
import math
import re

from app.knowledge.types import ChunkDraft, validate_id

PROVENANCE_FIELDS = ('dataset_fingerprint', 'corpus_hash', 'cases_hash', 'annotation_hash')


def _require(condition, message):
    """失败只报告安全字段原因，不回显输入。"""
    if not condition:
        raise ValueError(message)


def _object(value, fields):
    """新审计对象采用严格字段集合，不能夹带请求或私有模型元数据。"""
    _require(isinstance(value, Mapping) and set(value) == set(fields), '审计字段不符合白名单')
    return copy.deepcopy(dict(value))


def _text(value):
    """来源和要点身份只接受非空文本。"""
    return isinstance(value, str) and bool(value.strip())


def _hash(value):
    """来源摘要只接受完整SHA256，不能借其公开任意地址或文本。"""
    return isinstance(value, str) and re.fullmatch('[0-9a-f]{64}', value) is not None


def _digest(value):
    """来源映射的规范内容摘要，同时绑定逻辑、物理身份及全部原文。"""
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
        separators=(',', ':'), allow_nan=False).encode('utf-8')).hexdigest()


def build_source_map(dataset, id_map):
    """由已核验冻结数据和实际准备返回的主键创建单份运行来源映射。"""
    _require(set(id_map) == {chunk.chunk_key for chunk in dataset.chunks}, '来源映射块集合不完整')
    value = dict(audit_version=1, dataset_id=dataset.dataset_id,
        provenance=dict(zip(PROVENANCE_FIELDS, (dataset.fingerprint, dataset.corpus_hash,
            dataset.cases_hash, dataset.annotation_hash))),
        sources=[dict(chunk_key=chunk.chunk_key, chunk_id=id_map[chunk.chunk_key],
            document=chunk.document, ordinal=chunk.ordinal, draft=asdict(chunk.draft)) for chunk in dataset.chunks])
    value['source_map_id'] = _digest(value)
    return validate_source_map(value)


def validate_source_map(value, config=None):
    """验证单份有界来源对象；完整原文保留且摘要/配置出处必须一致。"""
    result = _object(value, ('audit_version', 'dataset_id', 'provenance', 'sources', 'source_map_id'))
    _require(type(result['audit_version']) is int and result['audit_version'] == 1, '未知来源审计版本')
    _require(result['dataset_id'] == 'merchant-rag-300-v1' and _hash(result['source_map_id']), '来源身份非法')
    provenance = _object(result['provenance'], PROVENANCE_FIELDS)
    _require(all(_hash(value) for value in provenance.values()), '来源出处摘要非法')
    if config is not None:
        _require(config['dataset_id'] == result['dataset_id'] and
            all(config.get('provenance', {}).get(key) == provenance[key] for key in PROVENANCE_FIELDS),
            '来源与运行出处不一致')
    sources = result['sources']
    _require(isinstance(sources, list) and 0 < len(sources) <= 50, '来源数量非法')
    keys, ids = set(), set()
    for original in sources:
        source = _object(original, ('chunk_key', 'chunk_id', 'document', 'ordinal', 'draft'))
        validate_id(source['chunk_id'])
        _require(_text(source['chunk_key']) and _text(source['document']) and
            type(source['ordinal']) is int and source['ordinal'] >= 0, '来源标识非法')
        _require(source['chunk_key'] not in keys and source['chunk_id'] not in ids, '来源身份重复')
        draft = _object(source['draft'], tuple(ChunkDraft.__dataclass_fields__))
        ChunkDraft(**draft)
        _require(_text(draft['answer']), '来源原文为空')
        keys.add(source['chunk_key'])
        ids.add(source['chunk_id'])
    _require(result['source_map_id'] == _digest({k: v for k, v in result.items() if k != 'source_map_id'}),
        '来源内容摘要不匹配')
    return result


def validate_audit(value, row):
    """局部验证要点和排序；旧记录明确null，不能自动补捕获值。"""
    if value is None:
        return None
    result = _object(value, ('audit_version', 'source_map_id', 'gold_groups', 'answer_points',
        'candidate_ranking', 'final_ranking'))
    _require(type(result['audit_version']) is int and result['audit_version'] == 1 and
        _hash(result['source_map_id']), '逐题审计版本或映射身份非法')
    groups = result['gold_groups']
    _require(isinstance(groups, list) and len(groups) == len(row['mapped_groups']), '逻辑金标组不完整')
    for logical, physical in zip(groups, row['mapped_groups']):
        group = _object(logical, ('group_id', 'alternatives'))
        _require(group['group_id'] == physical['group_id'] and isinstance(group['alternatives'], list)
            and len(group['alternatives']) == len(physical['alternatives']), '逻辑金标结构不匹配')
        for bundle, mapped in zip(group['alternatives'], physical['alternatives']):
            _require(isinstance(bundle, list) and len(bundle) == len(mapped) and
                all(_text(key) for key in bundle) and len(set(bundle)) == len(bundle), '逻辑金标组合非法')
    points = result['answer_points']
    _require(isinstance(points, list) and bool(points) != row['should_refuse'], '标准要点缺失或越界')
    seen = set()
    for original in points:
        point = _object(original, ('point_id', 'text', 'condition', 'aliases'))
        _require(_text(point['point_id']) and point['point_id'] not in seen and _text(point['text']) and
            (point['condition'] is None or _text(point['condition'])) and isinstance(point['aliases'], list) and
            all(_text(alias) for alias in point['aliases']), '标准要点非法')
        seen.add(point['point_id'])
    if row['point_verdicts'] is not None:
        _require([p['point_id'] for p in points] == [p['point_id'] for p in row['point_verdicts']], '裁判要点与原标准不一致')
    candidate_kind = {'dense': 'cosine', 'bm25': 'bm25', 'hybrid': 'rrf', 'hybrid_rerank': 'rrf'}[row['strategy']]
    for field, ids_field, kind in (('candidate_ranking', 'candidate_ids', candidate_kind),
            ('final_ranking', 'final_ids', 'rerank' if row['strategy'] == 'hybrid_rerank' else candidate_kind)):
        ranking, ids = result[field], row[ids_field]
        if ids is None:
            _require(ranking is None, '未完成检索含排序审计')
            continue
        _require(isinstance(ranking, list) and len(ranking) == len(ids), '排序审计不完整')
        for original, identifier in zip(ranking, ids):
            hit = _object(original, ('chunk_id', 'score', 'score_kind'))
            validate_id(hit['chunk_id'])
            _require(hit['chunk_id'] == identifier and type(hit['score']) in (int, float) and
                math.isfinite(hit['score']) and hit['score_kind'] == kind, '排序身份或分数非法')
    return result


def validate_audit_sources(row, source_map):
    """跨边界核对每个金标、候选、最终证据均可在运行原文映射中解析。"""
    audit = row.get('audit')
    if audit is None:
        return
    _require(source_map is not None and audit['source_map_id'] == source_map['source_map_id'], '逐题来源映射缺失或不匹配')
    by_key = {source['chunk_key']: source['chunk_id'] for source in source_map['sources']}
    ids = set(by_key.values())
    for logical, physical in zip(audit['gold_groups'], row['mapped_groups']):
        _require([[by_key.get(key) for key in bundle] for bundle in logical['alternatives']] == physical['alternatives'],
            '逻辑物理金标映射不一致')
    _require(all(identifier in ids for field in ('candidate_ids', 'final_ids') for identifier in row[field] or []),
        '排序来源不在冻结映射')
