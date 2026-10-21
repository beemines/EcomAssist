"""One versioned source defines the label order in both Python environments."""

from dataclasses import dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re


DEFAULT_PATH = Path(__file__).resolve().parents[2] / 'config/topic-taxonomy.json'


@dataclass(frozen=True)
class TopicDefinition:
    id: int
    name: str
    boundary: str


@dataclass(frozen=True)
class Taxonomy:
    version: str
    digest: str
    topics: tuple[TopicDefinition, ...]

    @property
    def ordered_names(self) -> tuple[str, ...]:
        return tuple(topic.name for topic in self.topics)

    def canonical_labels(self, labels, *, allow_empty: bool = False) -> tuple[str, ...]:
        if type(labels) not in (list, tuple) or any(type(label) is not str for label in labels):
            raise ValueError('Labels must be an explicit sequence of names')
        if len(set(labels)) != len(labels) or (not labels and not allow_empty):
            raise ValueError('Labels must be nonempty and unique')
        names = self.ordered_names
        if any(label not in names for label in labels):
            raise ValueError('Unknown topic label')
        if names[-1] in labels and len(labels) > 1:
            raise ValueError('Other is mutually exclusive with business labels')
        return tuple(name for name in names if name in labels)

    def encode(self, labels) -> tuple[int, ...]:
        checked = self.canonical_labels(labels)
        return tuple(int(name in checked) for name in self.ordered_names)


def _no_duplicate_keys(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate taxonomy JSON key')
        value[key] = item
    return value


def load_taxonomy(path: Path) -> Taxonomy:
    value = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=_no_duplicate_keys)
    if (type(value) is not dict or set(value) != {'schema_version', 'version', 'topics'}
            or type(value['schema_version']) is not int or value['schema_version'] != 1
            or type(value['version']) is not str
            or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,95}', value['version'])
            or type(value['topics']) is not list or len(value['topics']) != 17):
        raise ValueError('Invalid taxonomy document')
    topics = []
    for index, topic in enumerate(value['topics']):
        if (type(topic) is not dict or set(topic) != {'id', 'name', 'boundary'}
                or type(topic['id']) is not int or topic['id'] != index
                or any(type(topic[key]) is not str or not topic[key].strip()
                       or topic[key] != topic[key].strip() for key in ('name', 'boundary'))):
            raise ValueError('Invalid taxonomy entry')
        topics.append(TopicDefinition(**topic))
    if len({topic.name for topic in topics}) != 17 or topics[-1].name != '其他':
        raise ValueError('Taxonomy names must be unique and Other must be last')
    digest = hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                      separators=(',', ':')).encode('utf-8')).hexdigest()
    return Taxonomy(value['version'], digest, tuple(topics))


@lru_cache(maxsize=1)
def default_taxonomy() -> Taxonomy:
    return load_taxonomy(DEFAULT_PATH)
