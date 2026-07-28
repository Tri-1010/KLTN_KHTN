"""Validated UI-facing contracts for EvidenceTrace artifacts."""

from __future__ import annotations

from datetime import date, datetime
import re
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from scripts.llm_provider import UI_MODEL_ALLOWLIST
from .policy import INITIAL_TECHNICAL_FEATURES, assert_initial_payload_safe, display_signal_label

Zone = Literal["select", "initial", "monitor", "update", "review", "semantic", "evaluation", "provenance"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ArtifactReference(StrictModel):
    name: str
    path: str
    sha256: str = Field(min_length=64, max_length=64)
    zone: Zone
    record_count: int | None = Field(default=None, ge=0)
    schema_version: str | None = None
    generated_at_utc: datetime | None = None
    provenance_status: str | None = None


class RuntimeMember(StrictModel):
    path: str
    sha256: str = Field(min_length=64, max_length=64)

    @field_validator("path")
    @classmethod
    def require_relative_json_path(cls, value: str) -> str:
        path = value.replace("\\", "/")
        if path.startswith("/") or re.match(r"^[A-Za-z]:", path) or ".." in path.split("/") or not path.endswith(".json"):
            raise ValueError("Runtime member path must be a relative JSON path")
        return path


class DatasetManifest(StrictModel):
    dataset_id: str
    bundle_version: str
    built_at_utc: datetime
    research_only: bool = True
    live_data: bool = False
    source_artifacts: list[ArtifactReference]
    runtime_members: list[RuntimeMember] = Field(default_factory=list)
    monitor_as_of_date: date
    leakage_validation_passed: bool
    validation_report_path: str

    @model_validator(mode="after")
    def runtime_member_paths_are_unique(self) -> "DatasetManifest":
        paths = [member.path for member in self.runtime_members]
        if len(paths) != len(set(paths)):
            raise ValueError("Runtime member paths must be unique")
        return self


class MLSignal(StrictModel):
    model_name: str
    pred_proba_up: float = Field(ge=0, le=1)
    pred_label: int
    rank_in_period: int = Field(ge=1)
    source_signal_class: str
    display_status: str


class TechnicalDriver(StrictModel):
    feature: str
    value: float | None = None
    direction: str
    explanation: str


class NewsEvidence(StrictModel):
    evidence_id: str
    published_at: str
    source: str
    title: str
    article_summary: str | None = None
    key_facts: list[dict[str, Any]] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)
    event_type: str | None = None
    match_confidence: str | None = None
    evidence_span: str | None = None
    url: str | None = None
    content_hash: str | None = None
    extraction_status: str | None = None

    @field_validator("url")
    @classmethod
    def require_https_url(cls, value: str | None) -> str | None:
        if value is not None and not value.startswith("https://"):
            raise ValueError("Evidence URL must use https")
        return value


class DataQuality(StrictModel):
    news_coverage: str | None = None
    ticker_matching_confidence: str | None = None
    full_text_coverage: int | None = Field(default=None, ge=0)
    summary_coverage: int | None = Field(default=None, ge=0)
    key_fact_coverage: int | None = Field(default=None, ge=0)
    missing_fields: list[str] = Field(default_factory=list)


class InitialDecisionDetail(StrictModel):
    decision_id: str
    snapshot_mode: Literal["full_evidence", "ml_only"]
    ticker: str
    decision_date: str
    period_id: str
    holding_horizon: str
    ml_signal: MLSignal
    technical_snapshot: dict[str, float | None]
    top_drivers: list[TechnicalDriver]
    news_evidence: list[NewsEvidence] = Field(default_factory=list)
    data_quality_flags: DataQuality
    guardrails: dict[str, Any]
    provenance: ArtifactReference

    @field_validator("technical_snapshot")
    @classmethod
    def require_canonical_technical_features(cls, value: dict[str, float | None]) -> dict[str, float | None]:
        unknown = sorted(set(value) - INITIAL_TECHNICAL_FEATURES)
        if unknown:
            raise ValueError(f"Unknown technical_snapshot fields: {', '.join(unknown)}")
        return value

    @field_validator("top_drivers")
    @classmethod
    def require_canonical_driver_features(cls, value: list[TechnicalDriver]) -> list[TechnicalDriver]:
        unknown = sorted({driver.feature for driver in value} - INITIAL_TECHNICAL_FEATURES)
        if unknown:
            raise ValueError(f"Unknown top-driver features: {', '.join(unknown)}")
        return value


def normalize_initial_prompt_pack(
    pack: dict[str, Any],
    snapshot_mode: Literal["full_evidence", "ml_only"],
    provenance: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project a canonical producer pack into the exact prompt-safe UI contract."""
    source_signal = pack.get("ml_signal") or {}
    news: list[NewsEvidence] = []
    if snapshot_mode == "full_evidence":
        for raw in pack.get("news_evidence") or []:
            key_facts = [
                {
                    key: fact[key]
                    for key in ("fact_id", "fact", "evidence_quote", "fact_type", "direction", "confidence")
                    if key in fact
                }
                for fact in raw.get("key_facts") or []
                if isinstance(fact, dict)
            ]
            news.append(
                NewsEvidence(
                    evidence_id=str(raw["evidence_id"]),
                    published_at=str(raw["published_at"]),
                    source=str(raw.get("source") or "unknown"),
                    title=str(raw.get("title") or "Untitled evidence"),
                    article_summary=raw.get("article_summary") or raw.get("summary"),
                    key_facts=key_facts,
                    risk_flags=[str(flag) for flag in raw.get("risk_flags") or []],
                    event_type=raw.get("event_type"),
                    match_confidence=raw.get("match_confidence"),
                    evidence_span=raw.get("evidence_span") or raw.get("full_text_excerpt"),
                    url=raw.get("url") or None,
                    content_hash=raw.get("content_hash") or None,
                    extraction_status=raw.get("extraction_status") or None,
                )
            )
    quality = pack.get("data_quality_flags") or {}
    normalized_quality = {
        key: quality[key]
        for key in (
            "news_coverage",
            "ticker_matching_confidence",
            "full_text_coverage",
            "summary_coverage",
            "key_fact_coverage",
            "missing_fields",
        )
        if key in quality
    }
    guardrails = pack.get("guardrails") or {}
    normalized_guardrails = {
        key: guardrails[key]
        for key in (
            "full_text_excerpt_chars",
            "initial_prompt_safe",
            "news_cutoff",
            "news_evidence_excluded",
            "no_post_decision_data",
            "not_investment_advice",
        )
        if key in guardrails
    }
    detail = InitialDecisionDetail(
        decision_id=str(pack["decision_id"]),
        snapshot_mode=snapshot_mode,
        ticker=str(pack["ticker"]),
        decision_date=str(pack["decision_date"]),
        period_id=str(pack["period_id"]),
        holding_horizon=str(pack.get("holding_horizon") or "Unavailable"),
        ml_signal=MLSignal(
            model_name=str(source_signal.get("model_name") or "Unavailable"),
            pred_proba_up=float(source_signal["pred_proba_up"]),
            pred_label=int(source_signal["pred_label"]),
            rank_in_period=int(source_signal["rank_in_period"]),
            source_signal_class=str(source_signal.get("source_signal_class") or source_signal.get("signal_class") or "Unavailable"),
            display_status=str(source_signal.get("display_status") or display_signal_label(source_signal.get("signal_class"))),
        ),
        technical_snapshot={str(key): value for key, value in (pack.get("technical_snapshot") or {}).items()},
        top_drivers=[TechnicalDriver(**driver) for driver in pack.get("top_drivers") or []],
        news_evidence=news,
        data_quality_flags=DataQuality(**normalized_quality),
        guardrails=normalized_guardrails,
        provenance=ArtifactReference.model_validate(pack.get("provenance") or provenance),
    )
    normalized = detail.model_dump(mode="json")
    assert_initial_payload_safe(normalized)
    return normalized


class SelectCandidate(StrictModel):
    decision_id: str
    ticker: str
    period_id: str
    decision_date: str
    display_status: str
    pred_proba_up: float = Field(ge=0, le=1)
    rank_in_period: int = Field(ge=1)
    data_quality: DataQuality
    monitoring_available: bool
    review_available: bool


class SemanticConsensusDetail(StrictModel):
    news_id: str
    ticker: str
    article_date: str
    consensus_method: str
    agreement_level: str
    analysis_eligible: bool
    consensus_direction: str
    consensus_materiality: str
    consensus_event_type: str
    evidence_span: str | None = None
    disagreement_fields: list[str] = Field(default_factory=list)
    quality_flags: list[str] = Field(default_factory=list)
    requires_human_review: bool
    review_flags: list[str] = Field(default_factory=list)
    artifact_schema_version: str


class MonitoringEvent(StrictModel):
    event_id: str
    news_id: str | None = None
    decision_id: str
    ticker: str
    decision_date: str
    event_date: str
    action: Literal["Watch", "Review Required"]
    reason: str
    source: str
    title: str
    event_type: str | None = None
    risk_flags: list[str] = Field(default_factory=list)
    match_confidence: str | None = None
    article_summary: str | None = None
    url: str | None = None
    content_hash: str | None = None
    consensus_join_status: Literal["joined", "not_found", "ambiguous"]
    semantic_quality: SemanticConsensusDetail | None = None


class UpdateDetail(StrictModel):
    decision_id: str
    as_of: str
    initial_reference: dict[str, Any]
    monitoring_events: list[MonitoringEvent]
    workflow_state: Literal["Initial", "Watch", "Review Required"]
    proposed_analyst_questions: list[str]
    persisted: bool = False


class ReviewDetail(StrictModel):
    decision_id: str
    holding_period_complete: bool
    review_date: str | None = None
    initial_snapshot_reference: dict[str, Any]
    monitoring_summary: dict[str, Any]
    post_hoc_outcome: dict[str, Any] | None = None
    review_narrative: str | None = None
    provenance: dict[str, Any]


class CardRecord(StrictModel):
    card_id: str
    decision_id: str
    card_type: Literal["rule_based_baseline", "llm_ml_only", "llm_full_evidence"]
    producer_run_id: str
    provider: str
    requested_model: str | None = None
    response_model: str | None = None
    vendor: str | None = None
    generated_at_utc: str | None = None
    prompt_sha256: str | None = None
    pack_sha256: str | None = None
    body_markdown: str


class EvaluationRecord(StrictModel):
    card_id: str
    decision_id: str
    card_type: Literal["rule_based_baseline", "llm_ml_only", "llm_full_evidence"]
    evaluation_run_id: str
    judge_provider: str
    judge_model: str | None = None
    faithfulness: int = Field(ge=1, le=5)
    hallucination_control: int = Field(ge=1, le=5)
    ml_explanation: int = Field(ge=1, le=5)
    risk_awareness: int = Field(ge=1, le=5)
    monitoring_usefulness: int = Field(ge=1, le=5)
    clarity_usefulness: int = Field(ge=1, le=5)
    overall: int = Field(ge=1, le=5)
    major_issue: str | None = None
    major_hallucination_count: int = Field(ge=0)
    missing_evidence_ref_count: int = Field(ge=0)


class EvaluationBundle(StrictModel):
    evaluation_run_id: str
    card_count: int = Field(ge=0)
    rubric_warning: str
    records: list[EvaluationRecord]
    provenance: ArtifactReference


class FreshInformationRequest(StrictModel):
    decision_id: str = Field(min_length=1, max_length=128)
    provider: Literal["anthropic", "gemini", "deepseek"]
    model: str = Field(min_length=1, max_length=128)
    source_ids: list[Literal["vnexpress_business", "cafef_market"]] = Field(min_length=1, max_length=2)
    max_articles_per_source: int = Field(default=8, ge=1, le=10)
    confirmed_external_call: bool = False
    preview_digest: str | None = Field(default=None, min_length=64, max_length=64)
    preview_nonce: str | None = Field(default=None, min_length=16, max_length=128)

    @model_validator(mode="after")
    def model_is_allowlisted(self) -> "FreshInformationRequest":
        if self.model not in UI_MODEL_ALLOWLIST[self.provider]:
            raise ValueError(f"Model `{self.model}` is not allowlisted for provider `{self.provider}`")
        return self


class FreshNewsArticle(StrictModel):
    fresh_evidence_id: str
    source_id: str
    source_url: str
    title: str
    published_at: str | None = None
    fetched_at_utc: datetime
    excerpt: str
    url_sha256: str = Field(min_length=64, max_length=64)
    content_sha256: str = Field(min_length=64, max_length=64)


class FreshSourceAttempt(StrictModel):
    source_id: str
    url: str
    state: Literal["completed", "failed", "skipped"]
    articles_found: int = Field(ge=0)
    error: str | None = None


class FreshInformationResult(StrictModel):
    run_id: str
    state: Literal["completed", "partial", "failed"]
    decision_id: str
    ticker: str
    snapshot_id: str
    retrieved_at_utc: datetime
    result_markdown: str | None = None
    cited_evidence_ids: list[str] = Field(default_factory=list)
    run_directory: str


class LiveJobRequest(StrictModel):
    decision_ids: list[str] = Field(min_length=1, max_length=25)
    variant: Literal["ml_only", "full_evidence", "both"]
    provider: Literal["anthropic", "gemini", "deepseek"]
    model: str = Field(min_length=1, max_length=128)
    score: bool = True
    confirmed_external_call: bool = False
    preview_digest: str | None = Field(default=None, min_length=64, max_length=64)
    preview_nonce: str | None = Field(default=None, min_length=16, max_length=128)

    @model_validator(mode="after")
    def model_is_allowlisted(self) -> "LiveJobRequest":
        if self.model not in UI_MODEL_ALLOWLIST[self.provider]:
            raise ValueError(f"Model `{self.model}` is not allowlisted for provider `{self.provider}`")
        return self


class LiveJobStatus(StrictModel):
    job_id: str
    state: Literal["awaiting_confirmation", "queued", "running", "completed", "failed", "cancelled"]
    run_directory: str
    message: str
    created_at_utc: datetime
    completed_at_utc: datetime | None = None


class LiveRunManifest(StrictModel):
    run_id: str
    status: str
    provider: str
    requested_model: str
    response_model: str | None = None
    response_vendor: str | None = None
    outcome_removed_from_prompt: bool
    cards_generated: int = Field(ge=0)
    failures: list[dict[str, Any]] = Field(default_factory=list)
    artifacts: list[ArtifactReference] = Field(default_factory=list)
