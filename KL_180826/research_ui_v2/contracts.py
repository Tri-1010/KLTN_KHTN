"""Strict contracts for the standalone public V6 study-results release.

The V2 dashboard intentionally accepts only a small aggregate release artifact.  Its
contracts have no extension points: unknown fields, non-portable paths, and unsafe
payload markers fail validation before a UI can render them.
"""

from __future__ import annotations

from datetime import datetime
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


PUBLIC_RELEASE_SCHEMA_VERSION = "v6-public-release-v1"
RUNTIME_BUNDLE_SCHEMA_VERSION = "v6-runtime-bundle-v1"
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SAFE_PATH_SEGMENT_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class PublicReleaseContractError(ValueError):
    """Raised when an aggregate public release violates a safety boundary."""


class StrictPublicModel(BaseModel):
    """Base model for every browser-facing V6 public-release contract."""

    model_config = ConfigDict(extra="forbid", validate_assignment=True)


class BilingualText(StrictPublicModel):
    """A non-empty Vietnamese/English text pair used by the release and UI."""

    vi: str = Field(min_length=1, max_length=2000)
    en: str = Field(min_length=1, max_length=2000)

    @field_validator("vi", "en")
    @classmethod
    def require_non_blank_text(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Bilingual release text must not be blank")
        return normalized


def normalize_portable_json_path(value: str) -> str:
    """Return a strictly portable, root-relative JSON member path.

    Backslashes are rejected rather than normalized.  This keeps a manifest portable
    across platforms and prevents Windows drive-relative and UNC path ambiguities.
    """

    if not isinstance(value, str) or not value:
        raise ValueError("Runtime member path must be a non-empty string")
    if value != value.strip() or "\x00" in value:
        raise ValueError("Runtime member path contains unsafe whitespace or NUL")
    if value.startswith(("\\\\", "//")):
        raise ValueError("Runtime member path must not be a UNC path")
    if "\\" in value:
        raise ValueError("Runtime member path must use portable '/' separators")
    if value.startswith("/") or re.match(r"^[A-Za-z]:", value):
        raise ValueError("Runtime member path must be relative, not absolute")
    if not value.endswith(".json"):
        raise ValueError("Runtime member path must use the approved .json file type")

    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise ValueError("Runtime member path must not contain empty or traversal segments")
    if any(not SAFE_PATH_SEGMENT_PATTERN.fullmatch(part) for part in parts):
        raise ValueError("Runtime member path contains non-portable characters")
    return value


def validate_sha256(value: str) -> str:
    """Require canonical lower-case SHA-256 text."""

    if not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value):
        raise ValueError("SHA-256 must be 64 lower-case hexadecimal characters")
    return value


class ComparativeMetric(StrictPublicModel):
    """Aggregate paired comparison released for one locked study contrast."""

    result_id: Literal["C-A RF BA"]
    contrast: Literal["C-A"]
    model: Literal["Random Forest"]
    metric: Literal["balanced_accuracy"]
    estimate: float
    ci_lower: float
    ci_upper: float
    bh_adjusted_p_value: float = Field(ge=0.0, le=1.0)

    @model_validator(mode="after")
    def confidence_interval_contains_ordered_bounds(self) -> "ComparativeMetric":
        if self.ci_lower > self.ci_upper:
            raise ValueError("Confidence-interval lower bound exceeds upper bound")
        return self


class SourceStatus(StrictPublicModel):
    """Public provenance/status declaration with explicit aggregate-only limits."""

    source_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    status: Literal["locked", "available", "limited"]
    scope: Literal["aggregate_public"]
    label: BilingualText
    note: BilingualText
    contains_raw_records: Literal[False]
    contains_credentials: Literal[False]
    contains_prompts: Literal[False]
    contains_full_local_paths: Literal[False]


class Gate(StrictPublicModel):
    """A pre-specified release gate and its disclosed state."""

    gate_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    claim_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    analysis_state: Literal["confirmation"]
    status: Literal["met", "not_met", "not_assessed"]
    label: BilingualText
    rationale: BilingualText
    source_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")


class Claim(StrictPublicModel):
    """A scoped study statement; it is not a recommendation or causal assertion."""

    claim_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    analysis_state: Literal["primary", "exploratory", "confirmation"]
    status: Literal["supported", "unsupported", "inconclusive", "not_confirmed", "descriptive"]
    title: BilingualText
    statement: BilingualText
    source_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    gate_id: str | None = Field(default=None, pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    result: ComparativeMetric | None = None
    locked: bool


class SubgroupResult(StrictPublicModel):
    """Aggregate subgroup output retained as exploratory context only."""

    subgroup_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    analysis_state: Literal["exploratory"]
    status: Literal["descriptive", "not_estimable", "inconclusive"]
    label: BilingualText
    note: BilingualText
    source_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    result: ComparativeMetric | None = None


class ApprovedPreset(StrictPublicModel):
    """Fixed review context exposed by the non-executing Operate Preview."""

    preset_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    label: BilingualText
    description: BilingualText
    view: Literal["primary", "exploratory", "confirmation", "provenance"]
    claim_ids: list[str] = Field(min_length=1, max_length=12)
    execution: Literal["non_executing"]
    fixed: Literal[True]


class PublicV6ReleaseArtifact(StrictPublicModel):
    """The only aggregate release artifact V2 is permitted to consume."""

    schema_version: Literal[PUBLIC_RELEASE_SCHEMA_VERSION]
    artifact_id: Literal["v6-study-results-public-release"]
    release_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    generated_at_utc: datetime
    aggregate_only: Literal[True]
    research_only: Literal[True]
    record_count: int = Field(ge=1)
    claims: list[Claim] = Field(min_length=1)
    gates: list[Gate] = Field(min_length=1)
    source_statuses: list[SourceStatus] = Field(min_length=1)
    subgroup_results: list[SubgroupResult] = Field(default_factory=list)
    approved_presets: list[ApprovedPreset] = Field(min_length=1)
    limitations: list[BilingualText] = Field(min_length=1)

    @model_validator(mode="after")
    def require_consistent_aggregate_release(self) -> "PublicV6ReleaseArtifact":
        expected_count = (
            len(self.claims)
            + len(self.gates)
            + len(self.source_statuses)
            + len(self.subgroup_results)
            + len(self.approved_presets)
        )
        if self.record_count != expected_count:
            raise ValueError(
                f"Public-release record_count mismatch: declared={self.record_count}, expected={expected_count}"
            )
        _require_unique([claim.claim_id for claim in self.claims], "claim IDs")
        _require_unique([gate.gate_id for gate in self.gates], "gate IDs")
        _require_unique([source.source_id for source in self.source_statuses], "source IDs")
        _require_unique([subgroup.subgroup_id for subgroup in self.subgroup_results], "subgroup IDs")
        _require_unique([preset.preset_id for preset in self.approved_presets], "preset IDs")

        claim_ids = {claim.claim_id for claim in self.claims}
        gate_ids = {gate.gate_id for gate in self.gates}
        source_ids = {source.source_id for source in self.source_statuses}
        for claim in self.claims:
            if claim.source_id not in source_ids:
                raise ValueError(f"Claim {claim.claim_id} references an unknown source")
            if claim.gate_id is not None and claim.gate_id not in gate_ids:
                raise ValueError(f"Claim {claim.claim_id} references an unknown gate")
        for gate in self.gates:
            if gate.claim_id not in claim_ids or gate.source_id not in source_ids:
                raise ValueError(f"Gate {gate.gate_id} has an unresolved release reference")
        for subgroup in self.subgroup_results:
            if subgroup.source_id not in source_ids:
                raise ValueError(f"Subgroup {subgroup.subgroup_id} references an unknown source")
        for preset in self.approved_presets:
            unknown_claims = sorted(set(preset.claim_ids) - claim_ids)
            if unknown_claims:
                raise ValueError(f"Preset {preset.preset_id} references unknown claims: {', '.join(unknown_claims)}")
        return self


class PublicReleaseArtifactReference(StrictPublicModel):
    """Integrity declaration for an aggregate public release runtime artifact."""

    artifact_id: Literal["v6-study-results-public-release"]
    path: str
    sha256: str
    record_count: int = Field(ge=1)
    schema_version: Literal[PUBLIC_RELEASE_SCHEMA_VERSION]
    scope: Literal["aggregate_public"]

    @field_validator("path")
    @classmethod
    def require_portable_path(cls, value: str) -> str:
        return normalize_portable_json_path(value)

    @field_validator("sha256")
    @classmethod
    def require_sha256(cls, value: str) -> str:
        return validate_sha256(value)


class RuntimeMember(StrictPublicModel):
    """A declared, hash-checked member of a V2 runtime bundle."""

    artifact_id: Literal["v6-study-results-public-release"]
    path: str
    sha256: str
    record_count: int = Field(ge=1)
    schema_version: Literal[PUBLIC_RELEASE_SCHEMA_VERSION]

    @field_validator("path")
    @classmethod
    def require_portable_path(cls, value: str) -> str:
        return normalize_portable_json_path(value)

    @field_validator("sha256")
    @classmethod
    def require_sha256(cls, value: str) -> str:
        return validate_sha256(value)


class RuntimeBundle(StrictPublicModel):
    """Strict manifest for a portable public V6 dashboard bundle."""

    schema_version: Literal[RUNTIME_BUNDLE_SCHEMA_VERSION]
    bundle_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    release_id: str = Field(pattern=r"^[A-Za-z0-9][A-Za-z0-9._-]{1,95}$")
    built_at_utc: datetime
    root_policy: Literal["portable-root-contained-json-only"]
    member_count: int = Field(ge=1)
    release_member_path: str
    artifacts: list[PublicReleaseArtifactReference] = Field(min_length=1, max_length=1)
    runtime_members: list[RuntimeMember] = Field(min_length=1, max_length=1)

    @field_validator("release_member_path")
    @classmethod
    def require_portable_release_path(cls, value: str) -> str:
        return normalize_portable_json_path(value)

    @model_validator(mode="after")
    def require_matching_integrity_declarations(self) -> "RuntimeBundle":
        if self.member_count != len(self.runtime_members):
            raise ValueError(
                f"Runtime member_count mismatch: declared={self.member_count}, actual={len(self.runtime_members)}"
            )
        member_paths = [member.path for member in self.runtime_members]
        artifact_paths = [artifact.path for artifact in self.artifacts]
        _require_unique(member_paths, "runtime member paths")
        _require_unique(artifact_paths, "artifact paths")
        if self.release_member_path not in member_paths:
            raise ValueError("release_member_path is not declared as a runtime member")
        if set(member_paths) != set(artifact_paths):
            raise ValueError("Runtime members and artifact declarations do not match")
        by_path = {member.path: member for member in self.runtime_members}
        for artifact in self.artifacts:
            member = by_path[artifact.path]
            if (
                artifact.artifact_id != member.artifact_id
                or artifact.sha256 != member.sha256
                or artifact.record_count != member.record_count
                or artifact.schema_version != member.schema_version
            ):
                raise ValueError(f"Artifact/runtime declaration mismatch for {artifact.path}")
        return self


def _require_unique(values: list[str], label: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"Public release contains duplicate {label}")


FORBIDDEN_PUBLIC_FIELD_MARKERS = frozenset(
    {
        "raw_prediction",
        "raw_predictions",
        "prediction_rows",
        "raw_news",
        "news_records",
        "article_text",
        "credential",
        "secret",
        "api_key",
        "access_token",
        "password",
        "prompt",
        "full_local_path",
        "local_path",
        "file_path",
    }
)
# These explicit false-only status declarations are part of the public schema.  A
# payload field named ``prompt`` remains prohibited; ``contains_prompts: false`` is
# an allowlisted provenance assertion rather than prompt content.
ALLOWED_FALSE_ONLY_PUBLIC_FIELDS = frozenset(
    {
        "contains_raw_records",
        "contains_credentials",
        "contains_prompts",
        "contains_full_local_paths",
    }
)
FORBIDDEN_PUBLIC_VALUE_PATTERN = re.compile(
    r"(?:\b(?:api[_ -]?key|password|bearer)\b|\bsk-[A-Za-z0-9_-]{8,}|[A-Za-z]:[\\/]|\\\\|//)",
    re.IGNORECASE,
)
def assert_public_release_payload_safe(payload: PublicV6ReleaseArtifact | dict[str, Any]) -> PublicV6ReleaseArtifact:
    """Validate strict shape and reject fields/values outside the aggregate public zone."""

    try:
        release = (
            payload
            if isinstance(payload, PublicV6ReleaseArtifact)
            else PublicV6ReleaseArtifact.model_validate(payload)
        )
    except Exception as exc:  # Pydantic exposes a detailed validation chain to callers.
        raise PublicReleaseContractError("Public V6 release violates its strict contract") from exc

    violations = _find_public_safety_violations(release.model_dump(mode="json"))
    if violations:
        raise PublicReleaseContractError(
            "Public V6 release contains prohibited content at " + ", ".join(violations[:5])
        )
    return release


def _find_public_safety_violations(value: Any, path: str = "$") -> list[str]:
    violations: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key).lower()
            nested_path = f"{path}.{key}"
            explicit_false_status = key_text in ALLOWED_FALSE_ONLY_PUBLIC_FIELDS and nested is False
            if not explicit_false_status and any(marker in key_text for marker in FORBIDDEN_PUBLIC_FIELD_MARKERS):
                violations.append(nested_path)
            violations.extend(_find_public_safety_violations(nested, nested_path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            violations.extend(_find_public_safety_violations(nested, f"{path}[{index}]"))
    elif isinstance(value, str) and FORBIDDEN_PUBLIC_VALUE_PATTERN.search(value):
        violations.append(path)
    return violations
