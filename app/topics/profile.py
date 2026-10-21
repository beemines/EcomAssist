"""Non-secret, three-field configuration for the offline classification path."""
from dataclasses import dataclass
import json
from pathlib import Path

from app.topics.client import _json_unique, _local_url


@dataclass(frozen=True)
class TopicProfile:
    service_url: str
    manifest_path: Path
    runtime_root: Path


def load_profile(path: Path) -> TopicProfile:
    path = path.resolve()
    if path.stat().st_size > 16384:
        raise ValueError('Topic profile exceeds 16KiB')
    value = _json_unique(path.read_bytes())
    if type(value) is not dict or set(value) != {'service_url', 'manifest_path', 'runtime_root'}:
        raise ValueError('Topic profile requires exactly the three approved non-secret fields')
    def local_path(name):
        text = value[name]
        if type(text) is not str or not text.strip() or '\x00' in text:
            raise ValueError('Topic profile path must be nonblank text')
        result = Path(text)
        return (result if result.is_absolute() else path.parent/result).resolve()
    return TopicProfile(_local_url(value['service_url']), local_path('manifest_path'), local_path('runtime_root'))
