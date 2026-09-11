from __future__ import annotations

from copy import deepcopy
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

KLTN_ROOT = Path(__file__).resolve().parents[1]
if str(KLTN_ROOT) not in sys.path:
    sys.path.insert(0, str(KLTN_ROOT))

from research_ui_v2.contracts import (
    PublicReleaseContractError,
    PublicV6ReleaseArtifact,
    RuntimeBundle,
    assert_public_release_payload_safe,
    normalize_portable_json_path,
)
from research_ui_v2.fixtures.public_release import LOCKED_H2_RESULT, public_release_fixture


@pytest.mark.parametrize(
    "unsafe_path",
    [
        "/public_release.json",
        "C:/public_release.json",
        "C:\\public_release.json",
        "\\\\server\\share\\public_release.json",
        "//server/share/public_release.json",
        "../public_release.json",
        "nested/../public_release.json",
        "nested\\public_release.json",
        "public_release.csv",
        "public_release.json.exe",
        " public_release.json",
    ],
)
def test_portable_runtime_path_rejects_absolute_unc_traversal_and_unsafe_types(unsafe_path: str):
    with pytest.raises(ValueError):
        normalize_portable_json_path(unsafe_path)


def test_strict_public_release_contract_accepts_fixture_and_locked_unsupported_h2():
    release = assert_public_release_payload_safe(public_release_fixture())
    h2 = next(claim for claim in release.claims if claim.claim_id == "H2-semantic-comparison")

    assert h2.analysis_state == "confirmation"
    assert h2.status == "unsupported"
    assert h2.result is not None
    assert h2.result.model_dump() == LOCKED_H2_RESULT
    assert h2.result.estimate == -0.0042486
    assert h2.result.ci_lower == -0.0112006
    assert h2.result.ci_upper == 0.0018953
    assert h2.result.bh_adjusted_p_value == 0.229977
    assert all(status.contains_prompts is False for status in release.source_statuses)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda payload: payload.__setitem__("unexpected", True),
        lambda payload: payload["claims"][0].__setitem__("raw_predictions", []),
        lambda payload: payload["source_statuses"][0].__setitem__("contains_prompts", True),
        lambda payload: payload["source_statuses"][0].__setitem__("system_prompt", "hidden"),
        lambda payload: payload["source_statuses"][0]["note"].__setitem__("en", "Bearer secret-token"),
        lambda payload: payload["source_statuses"][0]["note"].__setitem__("en", "C:/private/release.json"),
        lambda payload: payload["source_statuses"][0]["note"].__setitem__("en", "audit path=C:\\Users\\User\\restricted\\source.json"),
        lambda payload: payload["source_statuses"][0]["note"].__setitem__("en", "review (C:\\Users\\User\\restricted\\source.json)"),
        lambda payload: payload.__setitem__("record_count", 999),
    ],
)
def test_public_release_contract_rejects_extra_private_or_mismatched_content(mutation):
    payload = public_release_fixture()
    mutation(payload)

    with pytest.raises((PublicReleaseContractError, ValidationError)):
        assert_public_release_payload_safe(payload)


def test_runtime_bundle_rejects_hash_count_and_schema_mismatch():
    digest = "a" * 64
    valid = {
        "schema_version": "v6-runtime-bundle-v1",
        "bundle_id": "fixture-runtime",
        "release_id": "fixture-release",
        "built_at_utc": "2026-09-05T00:00:00Z",
        "root_policy": "portable-root-contained-json-only",
        "member_count": 1,
        "release_member_path": "public_release.json",
        "artifacts": [
            {
                "artifact_id": "v6-study-results-public-release",
                "path": "public_release.json",
                "sha256": digest,
                "record_count": 7,
                "schema_version": "v6-public-release-v1",
                "scope": "aggregate_public",
            }
        ],
        "runtime_members": [
            {
                "artifact_id": "v6-study-results-public-release",
                "path": "public_release.json",
                "sha256": digest,
                "record_count": 7,
                "schema_version": "v6-public-release-v1",
            }
        ],
    }
    assert RuntimeBundle.model_validate(valid).member_count == 1

    for field, value in (("sha256", "b" * 64), ("record_count", 8), ("schema_version", "wrong-v1")):
        invalid = deepcopy(valid)
        invalid["artifacts"][0][field] = value
        with pytest.raises(ValidationError):
            RuntimeBundle.model_validate(invalid)


def test_runtime_bundle_rejects_multiple_members_and_unsafe_member_path():
    digest = "a" * 64
    payload = {
        "schema_version": "v6-runtime-bundle-v1",
        "bundle_id": "fixture-runtime",
        "release_id": "fixture-release",
        "built_at_utc": "2026-09-05T00:00:00Z",
        "root_policy": "portable-root-contained-json-only",
        "member_count": 2,
        "release_member_path": "../public_release.json",
        "artifacts": [],
        "runtime_members": [],
    }
    with pytest.raises(ValidationError):
        RuntimeBundle.model_validate(payload)

    multi = {
        **payload,
        "member_count": 2,
        "release_member_path": "public_release.json",
        "artifacts": [
            {
                "artifact_id": "v6-study-results-public-release",
                "path": name,
                "sha256": digest,
                "record_count": 7,
                "schema_version": "v6-public-release-v1",
                "scope": "aggregate_public",
            }
            for name in ("public_release.json", "extra.json")
        ],
        "runtime_members": [
            {
                "artifact_id": "v6-study-results-public-release",
                "path": name,
                "sha256": digest,
                "record_count": 7,
                "schema_version": "v6-public-release-v1",
            }
            for name in ("public_release.json", "extra.json")
        ],
    }
    with pytest.raises(ValidationError):
        RuntimeBundle.model_validate(multi)


def test_release_models_forbid_unknown_fields_directly():
    payload = public_release_fixture()
    payload["claims"][0]["unknown"] = "no"
    with pytest.raises(ValidationError):
        PublicV6ReleaseArtifact.model_validate(payload)
