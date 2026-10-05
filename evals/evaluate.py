"""Evaluate human-labelled cases against the running application's extract API."""

import argparse
import asyncio
import json
from collections.abc import Sequence
from importlib.metadata import version
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import anyio
import httpx
from pydantic import ValidationError

from app.schemas.extract import AfterSalesResult, ExtractRequest


REQUEST_DEADLINE_SECONDS = 75.0
FIELDS = ("order_id", "request_type", "expected_solution")


def valid_response(value) -> bool:
    if not isinstance(value, dict):
        return False
    try:
        AfterSalesResult.model_validate(value)
    except ValidationError:
        return False
    return True


def score_cases(records: Sequence[dict]) -> dict:
    total = len(records)
    correct = dict.fromkeys(FIELDS, 0)
    valid_count = missing_total = missing_correct = source_correct = 0
    failures = []
    for record in records:
        response, expected = record["response"], record["expected"]
        valid = record["status_code"] == 200 and record["error_code"] is None and valid_response(response)
        valid_count += int(valid)
        source_ok = valid and all(response[field] is None or response[field] in record["text"]
                                  for field in ("order_id", "expected_solution"))
        source_correct += int(source_ok)
        mismatches = []
        for field in FIELDS:
            match = valid and response[field] == expected[field]
            correct[field] += int(match)
            if not match:
                mismatches.append(field)
            if expected[field] is None or (field == "request_type" and expected[field] == "unknown"):
                missing_total += 1
                missing_correct += int(match)
        if not valid or mismatches or not source_ok:
            failures.append({"id": record["id"], "error_code": record["error_code"] or
                             ("invalid_response" if not valid else "label_or_source_mismatch"),
                             "mismatched_fields": mismatches, "source_constraint_ok": bool(source_ok)})

    def rate(numerator, denominator):
        return numerator / denominator if denominator else None

    return {"total": total, "valid_count": valid_count, "valid_rate": rate(valid_count, total),
            **{f"{field}_accuracy": rate(correct[field], total) for field in FIELDS},
            "missing_value_total": missing_total, "missing_value_correct": missing_correct,
            "missing_value_accuracy": rate(missing_correct, missing_total),
            "source_constraint_total": total, "source_constraint_correct": source_correct,
            "source_constraint_rate": rate(source_correct, total), "failures": failures}


def identity(*, configured_upstream=None, configured_model=None) -> dict:
    # Explicit CLI declarations only. Never read .env or claim provider-returned identity.
    if configured_upstream:
        parts = urlsplit(configured_upstream)
        hostname = parts.hostname or ""
        if parts.port:
            hostname += f":{parts.port}"
        configured_upstream = urlunsplit((parts.scheme, hostname, parts.path, "", ""))
    return {"configuration_source": "explicit_cli_arguments" if configured_upstream or configured_model else "unknown",
            "configured_upstream": configured_upstream, "configured_model": configured_model,
            "provider_verified": False, "provider_reported_identity": None,
            "versions": {name: version(name) for name in ("httpx", "langchain-openai", "openai")}}


def save_report(output_path: Path, report: dict) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_cases(path: Path) -> list[dict]:
    cases = []
    seen = set()
    for number, line in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        if not line.strip():
            continue
        try:
            case = json.loads(line)
            if set(case) != {"id", "text", "expected"} or not isinstance(case["id"], str) or not case["id"].strip():
                raise ValueError
            if case["id"] in seen or not valid_response(case["expected"]):
                raise ValueError
            ExtractRequest.model_validate({"text": case["text"]})
            if any(case["expected"][field] is not None and case["expected"][field] not in case["text"]
                   for field in ("order_id", "expected_solution")):
                raise ValueError
        except (ValueError, TypeError, KeyError, ValidationError):
            raise ValueError(f"Invalid labelled case at line {number}") from None
        cases.append(case)
        seen.add(case["id"])
    if not cases:
        raise ValueError("Dataset must contain at least one labelled case")
    return cases


async def extract_request(client, base_url, text, *, deadline=REQUEST_DEADLINE_SECONDS) -> dict:
    record = {"status_code": None, "response": None, "error_code": None}
    try:
        with anyio.fail_after(deadline):
            response = await client.post(base_url.rstrip("/") + "/api/extract", json={"text": text}, timeout=deadline)
            record["status_code"] = response.status_code
            if response.status_code != 200:
                record["error_code"] = "http_error"
            else:
                try:
                    value = response.json()
                except ValueError:
                    record["error_code"] = "invalid_json"
                else:
                    if valid_response(value):
                        record["response"] = value
                    else:
                        record["error_code"] = "invalid_schema"
    except (TimeoutError, httpx.TimeoutException):
        record["error_code"] = "timeout"
    except httpx.HTTPError:
        record["error_code"] = "transport_error"
    return record


async def evaluate(base_url: str, cases_path: Path, output_path: Path, *, http_client: httpx.AsyncClient | None = None) -> dict:
    cases = read_cases(cases_path)
    owns_client = http_client is None
    client = http_client if http_client is not None else httpx.AsyncClient(timeout=REQUEST_DEADLINE_SECONDS, trust_env=False)
    records = []
    attempted_count = 0
    first_case_failed = False
    try:
        for case in cases:
            if first_case_failed:
                result = {"status_code": None, "response": None, "error_code": "not_attempted"}
            else:
                attempted_count += 1
                result = await extract_request(client, base_url, case["text"], deadline=REQUEST_DEADLINE_SECONDS)
                if attempted_count == 1 and result["error_code"] is not None:
                    first_case_failed = True
            records.append({**case, **result})
    finally:
        if owns_client:
            await client.aclose()
    report = {"kind": "extract_evaluation", "identity": identity(), "request_count": attempted_count,
              "attempted_count": attempted_count, "not_attempted_count": len(cases) - attempted_count,
              "first_case_json_compatible": records[0]["error_code"] is None,
              "metrics": score_cases(records), "records": records}
    save_report(output_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--cases", type=Path, default=Path("evals/ch01_cases.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("docs/validation/ch01-evaluation.json"))
    parser.add_argument("--configured-upstream")
    parser.add_argument("--configured-model")
    args = parser.parse_args()
    report = asyncio.run(evaluate(args.base_url, args.cases, args.output))
    report["identity"] = identity(configured_upstream=args.configured_upstream, configured_model=args.configured_model)
    save_report(args.output, report)
    print(json.dumps(report["metrics"], ensure_ascii=False))
    # Label mismatches are reported without an invented accuracy threshold.
    return 1 if report["metrics"]["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
