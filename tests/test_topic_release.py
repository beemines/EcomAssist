"""Outer release integrity is independent of the core model hash."""
import json,hashlib
import pytest
from tests.test_topic_manifest import model_files
from app.topics.reviews import digest

def test_service_release_requires_verified_evidence_and_does_not_change_core(tmp_path):
    from app.topics.manifest import verify_release
    model_files(tmp_path)
    with pytest.raises(ValueError):verify_release(tmp_path)

@pytest.mark.parametrize('name',['../outside','model.safetensors','unexpected.json'])
def test_release_rejects_non_evidence_paths(tmp_path,name):
    from app.topics.manifest import ReleaseManifest
    fields=dict(schema_version=1,model_version='1'*64,human_status='reviewed',
        files={name:dict(sha256='2'*64,bytes=1)})
    with pytest.raises(ValueError):ReleaseManifest(**fields,release_hash=digest(fields))

def test_distribution_does_not_activate_an_unreviewed_core(tmp_path):
    from types import SimpleNamespace
    from app.topics.statistics import TopicStatisticsService
    path,_=model_files(tmp_path)
    service=TopicStatisticsService(None,SimpleNamespace(manifest_path=path),None)
    with pytest.raises(ValueError):service._identity()
