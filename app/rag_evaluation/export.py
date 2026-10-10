"""固定落点的公开报告导出；聚合上限独立于单条检查点，不截断证据。"""

import json
import os
from pathlib import Path
import tempfile

from app.rag_evaluation.report import public_report
from app.rag_evaluation.store import StoreError, canonical_root, guarded_path, public_run_metadata, validate_manifest

MAX_EXPORT_BYTES = 128 * 1024 * 1024


def report_envelope(manifest: dict, records: list[dict]) -> dict:
    """公开报告与独立安全运行元数据组合，私有原文和资源归属从不进入导出。"""
    checked = validate_manifest(manifest)
    config = checked['config']
    result = public_report(dict(schema_version=2, records=records, run_id=checked['run_id'],
        dataset_id=config['dataset_id'], fingerprint=config['fingerprint'], scope=config['scope']))
    result['run'] = public_run_metadata(checked)
    return result


def _markdown(report: dict) -> str:
    """Markdown包含汇总及全部公开逐题产物，不用省略号替代真实证据。"""
    lines = ['# RAG 评估报告', '', f"运行：{report['run_id']}", '',
             f"状态：{report['run']['state']}；范围：{report['scope']}", '',
             '## 运行信息与汇总', '', '```json',
             json.dumps({key: value for key, value in report.items() if key != 'records'},
                        ensure_ascii=False, indent=2, allow_nan=False), '```', '', '## 逐题结果']
    for row in report['records']:
        lines.extend(['', f"### {row['eval_id']} / {row['strategy']}", '', '````json',
                      json.dumps(row, ensure_ascii=False, indent=2, allow_nan=False), '````'])
    return '\n'.join(lines) + '\n'


def publish_reports(root: Path, manifest: dict, records: list[dict]) -> None:
    """两种完整文件分别同目录fsync/replace，任一失败阻止后续终态发布。"""
    root = canonical_root(root)
    report = report_envelope(manifest, records)
    run_id = report['run_id']
    contents = {'report.json': json.dumps(report, ensure_ascii=False, separators=(',', ':'), allow_nan=False),
                'report.md': _markdown(report)}
    encoded = {name: value.encode('utf-8') for name, value in contents.items()}
    if any(len(value) > MAX_EXPORT_BYTES for value in encoded.values()):
        raise StoreError('完整聚合报告超过128MiB上限')
    for name, content in encoded.items():
        temporary = None
        try:
            path = guarded_path(root, run_id, name)
            descriptor, temporary_name = tempfile.mkstemp(prefix='.report-', suffix='.tmp', dir=path.parent)
            temporary = Path(temporary_name)
            with os.fdopen(descriptor, 'wb') as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            guarded_path(root, run_id, name)
            os.replace(temporary, path)
        except OSError as exc:
            raise StoreError('聚合报告原子发布失败') from exc
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
