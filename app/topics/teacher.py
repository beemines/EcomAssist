"""Bounded standard-API teacher calls with one authorization per HTTP attempt."""

import asyncio
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
from typing import Sequence
from uuid import uuid4

import httpx
from pydantic import Field, SecretStr, field_validator, model_validator

from app.topics.budget import BudgetLedger, Usage
from app.topics.cleaning import CleanQuestion, clean_question
from app.topics.prompts import PROMPT_VERSION, system_prompt
from app.topics.taxonomy import default_taxonomy
from app.topics.types import LabelledSample, StrictRecord


ENDPOINT = 'https://open.bigmodel.cn/api/paas/v4/chat/completions'
MODEL = 'glm-5.3-flash'
TOTAL_TIMEOUT_SECONDS = 120


class TeacherError(RuntimeError):
    """Safe stage failure; no upstream message, credentials or customer text."""


class GenerationPlan(StrictRecord):
    count: int = Field(ge=1, le=16)
    scenario_labels: tuple[tuple[str, ...], ...]
    taxonomy_hash: str
    scenario_hints: tuple[str, ...] = ()

    @field_validator('scenario_hints', mode='before')
    @classmethod
    def hints(cls,value):
        if (type(value) not in (list,tuple) or any(type(hint) is not str or len(hint)>256 for hint in value)):
            raise ValueError('Scene hints must be bounded strings')
        result=[]
        for hint in value:
            checked=clean_question(hint,sample_id='scene-hint')
            if checked.quarantine_reasons or any('redacted' in edit for edit in checked.edits):
                raise ValueError('Scene hints cannot contain possible personal data')
            result.append(checked.text)
        return tuple(result)

    @field_validator('scenario_labels', mode='before')
    @classmethod
    def labels(cls, value):
        if type(value) not in (list, tuple):
            raise ValueError('Expected scenario arrays')
        return tuple(default_taxonomy().canonical_labels(labels) for labels in value)

    @model_validator(mode='after')
    def count_and_version(self):
        if (len(self.scenario_labels) != self.count or self.taxonomy_hash != default_taxonomy().digest
                or self.scenario_hints and len(self.scenario_hints)!=self.count):
            raise ValueError('Scenario count or taxonomy identity mismatch')
        return self


class GeneratedQuestion(StrictRecord):
    id: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    text: str = Field(min_length=1, max_length=512)
    family_id: str = Field(min_length=1, max_length=128, pattern=r'^[A-Za-z0-9][A-Za-z0-9_.:-]*$')
    requested_labels: tuple[str, ...]

    @field_validator('requested_labels', mode='before')
    @classmethod
    def labels(cls, value):
        return default_taxonomy().canonical_labels(value)


class Prelabel(StrictRecord):
    id: str = Field(min_length=1, max_length=128)
    cleaned_text: str = Field(min_length=1, max_length=512)
    labels: tuple[str, ...]
    notes: str = Field(max_length=1024)

    @field_validator('labels', mode='before')
    @classmethod
    def checked_labels(cls, value):
        return default_taxonomy().canonical_labels(value)


def _strict_json(raw):
    def pairs(items):
        value = {}
        for key, item in items:
            if key in value:
                raise ValueError('Duplicate JSON key')
            value[key] = item
        return value
    return json.loads(raw, object_pairs_hook=pairs)


def _items(value, expected):
    if type(value) is not dict or set(value) != {'items'} or type(value['items']) is not list:
        raise ValueError('Expected only an items array')
    rows = value['items']
    if (len(rows) != len(expected) or any(type(row) is not dict or type(row.get('id')) is not str for row in rows)
            or len({row['id'] for row in rows}) != len(rows) or {row['id'] for row in rows} != set(expected)):
        raise ValueError('Teacher output IDs do not match the request')
    mapping = {row['id']: row for row in rows}
    return [mapping[identifier] for identifier in expected]


def _private_text_safe(value: str, identifier: str) -> bool:
    checked = clean_question(value, sample_id=identifier)
    return (not checked.quarantine_reasons and not any('redacted' in edit for edit in checked.edits)
            and checked.text == value)


def parse_prelabels(value, samples: Sequence[CleanQuestion]) -> tuple[Prelabel, ...]:
    """Normalize the provider's unambiguous text alias, preserving exact inputs."""
    expected = {sample.sample_id: sample.text for sample in samples}
    canonical = []
    for row in _items(value, expected):
        if set(row) == {'id', 'text', 'labels', 'notes'}:
            row = {'cleaned_text': row['text']} | {key: item for key, item in row.items() if key != 'text'}
        canonical.append(Prelabel.model_validate(row))
    rows = tuple(canonical)
    if any(row.cleaned_text != expected[row.id] for row in rows):
        raise ValueError('Prelabel must not alter the question')
    return rows


def parse_generated(value, expected) -> tuple[GeneratedQuestion, ...]:
    rows = tuple(GeneratedQuestion.model_validate(row) for row in _items(value, expected))
    for row in rows:
        cleaned = clean_question(row.text, sample_id=row.id)
        if (row.family_id != expected[row.id]['family_id']
                or list(row.requested_labels) != expected[row.id]['requested_labels']
                or cleaned.quarantine_reasons or any('redacted' in edit for edit in cleaned.edits)):
            raise ValueError('Generated item changed scenario or contains possible personal data')
    return tuple(row.model_copy(update={'text': clean_question(row.text, sample_id=row.id).text}) for row in rows)


class TeacherClient:
    def __init__(self, ledger: BudgetLedger, *, api_key: SecretStr, transport=None, evidence_dir: Path | None = None):
        if not isinstance(api_key, SecretStr) or not api_key.get_secret_value().strip():
            raise ValueError('A private API key is required')
        self.ledger, self._key = ledger, api_key
        self._http = httpx.AsyncClient(transport=transport or httpx.AsyncHTTPTransport(retries=0),
            follow_redirects=False, trust_env=False, timeout=httpx.Timeout(60, connect=10, write=30, pool=5))
        self._lock = asyncio.Lock()
        self.last_receipt = None
        self._evidence_dir = evidence_dir

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._http.aclose()

    async def _http_response(self, payload):
        async with self._http.stream('POST', ENDPOINT, content=payload,
                headers={'Authorization': 'Bearer ' + self._key.get_secret_value(), 'Content-Type': 'application/json'}) as response:
            body = bytearray()
            async for chunk in response.aiter_bytes():
                body.extend(chunk)
                if len(body) > 2 * 1024 * 1024:
                    raise TeacherError('teacher_response_too_large')
            return response.status_code, bytes(body)

    async def _call(self, stage, items, parse):
        if not 1 <= len(items) <= 16:
            raise ValueError('Teacher batch must contain 1..16 items')
        prompt = system_prompt(stage)
        payload = json.dumps(dict(model=MODEL, thinking={'type': 'enabled'}, reasoning_effort='low',
            max_tokens=8192, stream=False, response_format={'type': 'json_object'},
            messages=[dict(role='system', content=prompt),
                      dict(role='user', content=json.dumps({'items': items}, ensure_ascii=False, separators=(',', ':')))]),
            ensure_ascii=False, separators=(',', ':')).encode('utf-8')
        if len(payload) > 65536:
            raise ValueError('Teacher request exceeds the fixed 64KiB limit')
        payload_hash = hashlib.sha256(payload).hexdigest()
        async with self._lock:
            deadline = asyncio.get_running_loop().time() + TOTAL_TIMEOUT_SECONDS
            for retry in range(2):
                reservation = self.ledger.reserve(stage, payload_hash)
                attempt_id = reservation.attempt_id
                self.last_receipt = dict(attempt_id=attempt_id, payload_hash=payload_hash,
                    prompt_hash=hashlib.sha256(prompt.encode('utf-8')).hexdigest(),
                    prompt_version=PROMPT_VERSION, model=MODEL, request_id=None)
                try:
                    async with asyncio.timeout(max(0, deadline - asyncio.get_running_loop().time())):
                        status, raw = await self._http_response(payload)
                except (httpx.TransportError, TimeoutError) as exc:
                    self.ledger.mark_unknown(attempt_id, 'network_failure')
                    self.ledger.record_outcome(attempt_id, success=False)
                    if retry == 0 and asyncio.get_running_loop().time() < deadline:
                        continue
                    raise TeacherError('teacher_network_failure') from None
                except BaseException:
                    self.ledger.mark_unknown(attempt_id, 'cancelled_or_transport_failure')
                    self.ledger.record_outcome(attempt_id, success=False)
                    raise
                try:
                    body = _strict_json(raw)
                except (ValueError, UnicodeDecodeError):
                    body = None
                settled = False
                if type(body) is dict and type(body.get('usage')) is dict:
                    usage = body['usage']
                    try:
                        details = usage.get('completion_tokens_details')
                        if details is not None and type(details) is not dict:
                            raise ValueError('Invalid reasoning usage')
                        validated = Usage(prompt_tokens=usage['prompt_tokens'], completion_tokens=usage['completion_tokens'],
                            total_tokens=usage['total_tokens'], reasoning_tokens=(details or {}).get('reasoning_tokens'),
                            reasoning_included=True)
                    except (ValueError, KeyError, TypeError):
                        pass
                    else:
                        self.ledger.settle(attempt_id, validated)
                        settled = True
                if not settled:
                    self.ledger.mark_unknown(attempt_id, 'missing_or_invalid_usage')
                if status != 200 or not settled:
                    self.ledger.record_outcome(attempt_id, success=False)
                    if status in (500, 502, 503, 504) and retry == 0 and asyncio.get_running_loop().time() < deadline:
                        continue
                    raise TeacherError('teacher_http_failure' if status != 200 else 'teacher_usage_unverifiable')
                request_id = body.get('id')
                if type(request_id) is str and re.fullmatch(r'[A-Za-z0-9_.:-]{1,128}', request_id):
                    self.last_receipt['request_id'] = request_id
                try:
                    if (type(body.get('choices')) is not list or len(body['choices']) != 1
                            or body['choices'][0]['finish_reason'] != 'stop'
                            or type(body['choices'][0]['message']['content']) is not str):
                        raise ValueError('Incomplete completion')
                    result = parse(_strict_json(body['choices'][0]['message']['content']))
                except (ValueError, TypeError, KeyError) as exc:
                    self.ledger.record_outcome(attempt_id, success=False)
                    if self._evidence_dir is not None:
                        from app.topics.snapshot import write_new_json
                        choice = body.get('choices', [])
                        choice = choice[0] if type(choice) is list and choice and type(choice[0]) is dict else {}
                        message = choice.get('message')
                        message = message if type(message) is dict else {}
                        diagnostic = dict(attempt_id=attempt_id, receipt=self.last_receipt.copy(),
                            finish_reason=choice.get('finish_reason'), content=message.get('content'),
                            error_type=type(exc).__name__, problem=str(exc))
                        path = self._evidence_dir / f'{attempt_id}.json'
                        write_new_json(path, diagnostic)
                        self.last_receipt['diagnostic_file'] = str(path.resolve())
                    raise TeacherError('teacher_structured_output_invalid') from None
                self.ledger.record_outcome(attempt_id, success=True)
                return result

    async def label(self, samples: Sequence[CleanQuestion]) -> tuple[Prelabel, ...]:
        samples = tuple(samples)
        if (not 1 <= len(samples) <= 16 or any(not isinstance(sample, CleanQuestion) for sample in samples)
                or len({sample.sample_id for sample in samples}) != len(samples)
                or any(sample.quarantine_reasons or not sample.text or len(sample.text) > 512
                       or not _private_text_safe(sample.text, sample.sample_id) for sample in samples)):
            raise ValueError('Only unique, locally cleaned, unquarantined samples may be labelled')
        def parse(value):
            return parse_prelabels(value, samples)
        return await self._call('label', [dict(id=sample.sample_id, text=sample.text) for sample in samples], parse)

    async def generate(self, plan: GenerationPlan) -> tuple[GeneratedQuestion, ...]:
        nonce = uuid4().hex
        items = [dict(id=f'syn-{nonce}-{i}', family_id=f'family-{nonce}-{i}', requested_labels=list(labels))
                 for i, labels in enumerate(plan.scenario_labels)]
        for item,hint in zip(items,plan.scenario_hints):
            if not _private_text_safe(hint,item['id']): raise ValueError('Scene hint needs local privacy safety')
            item['scenario_hint']=hint
        expected = {item['id']: item for item in items}
        def parse(value):
            return parse_generated(value, expected)
        return await self._call('generate', items, parse)

    async def augment(self, samples: Sequence[LabelledSample]) -> tuple[LabelledSample, ...]:
        samples = tuple(samples)
        if (not 1 <= len(samples) <= 16 or any(not isinstance(sample, LabelledSample) for sample in samples)
                or any(not _private_text_safe(sample.text, sample.id) for sample in samples)):
            raise ValueError('Only safe training samples may reach augmentation')
        expected = {sample.id: sample for sample in samples}
        if len(expected) != len(samples):
            raise ValueError('Augmentation IDs must be unique')
        def protected(value):
            return Counter(re.findall(r'\d+(?:\.\d+)?|[A-Za-z]+|不要|不想|不能|不退|不修|只想|只要|退|换|修', value))
        def parse(value):
            result = []
            for row in _items(value, expected):
                if set(row) != {'id', 'text'} or type(row['text']) is not str:
                    raise ValueError('Invalid augmentation fields')
                parent = expected[row['id']]
                cleaned = clean_question(row['text'], sample_id=parent.id)
                if (cleaned.quarantine_reasons or any('redacted' in edit for edit in cleaned.edits)
                        or cleaned.text == parent.text or protected(cleaned.text) != protected(parent.text)):
                    raise ValueError('Augmentation changed protected meaning or personal-data safety')
                result.append(LabelledSample(**(parent.model_dump() | {'id': parent.id + '-aug', 'text': cleaned.text})))
            return tuple(result)
        return await self._call('augment', [dict(id=sample.id, text=sample.text, labels=list(sample.labels))
                                          for sample in samples], parse)


def configured_teacher(settings, ledger: BudgetLedger, *, evidence_dir: Path | None = None) -> TeacherClient:
    """Only the approved standard provider profile may supply the private key."""
    if (str(settings.llm_base_url).rstrip('/') != ENDPOINT.rsplit('/chat/completions', 1)[0]
            or settings.llm_model != MODEL):
        raise ValueError('Teacher requires the approved standard GLM endpoint and model')
    return TeacherClient(ledger, api_key=settings.llm_api_key, evidence_dir=evidence_dir)
