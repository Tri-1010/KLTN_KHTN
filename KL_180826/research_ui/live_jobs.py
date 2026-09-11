"""Confirmed, isolated live-LLM jobs for EvidenceTrace analyst mode.

No job is scheduled automatically. Callers must pass a validated request with
``confirmed_external_call=True``; credentials stay in environment variables.
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import threading
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from scripts import generate_llm_decision_cards as generator
from scripts import score_decision_cards as scorer
from scripts.llm_provider import (
    call_generate,
    call_score,
    load_env_file,
    make_llm_client,
    provider_sdk_name,
    provider_temperature,
    provider_thinking,
    resolve_model,
)

from .contracts import LiveJobRequest, LiveJobStatus, normalize_initial_prompt_pack
from .policy import assert_initial_payload_safe
from .repository import BundleRepository
from .run_catalog import repo_root


PREVIEW_TTL = timedelta(minutes=10)
MAX_PREVIEWS = 256
_LIVE_JOB_LOCK = threading.Lock()
_PREVIEW_LOCK = threading.RLock()
_PREVIEWS: dict[str, dict[str, Any]] = {}


def _sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _purge_previews_locked(now: datetime) -> None:
    expired = [nonce for nonce, preview in _PREVIEWS.items() if preview["expires_at"] < now]
    for nonce in expired:
        del _PREVIEWS[nonce]


class LiveJobError(RuntimeError):
    """Raised for invalid or failed live research jobs."""


class LiveJobService:
    """Run one confirmed, bounded generation/scoring job in an isolated directory."""

    def __init__(
        self,
        root: Path | None = None,
        max_cards: int = 2,
        bundle_repository: BundleRepository | None = None,
        session_binding: str | None = None,
    ):
        self.root = root or repo_root()
        self.max_cards = max_cards
        self.bundle_repository = bundle_repository
        self._session_binding_digest = _sha256(session_binding or uuid.uuid4().hex)

    def _preview_digest(self, scope: dict[str, Any]) -> str:
        binding = {"scope": scope, "session_binding_sha256": self._session_binding_digest}
        return _sha256(json.dumps(binding, ensure_ascii=False, sort_keys=True, separators=(",", ":")))

    def preview(self, request: LiveJobRequest) -> dict[str, Any]:
        scope = self._scope_for_request(request)
        digest = self._preview_digest(scope)
        now = _utcnow()
        with _PREVIEW_LOCK:
            _purge_previews_locked(now)
            for nonce, preview in _PREVIEWS.items():
                if (
                    preview["digest"] == digest
                    and preview["scope"] == scope
                    and preview["session_binding_digest"] == self._session_binding_digest
                ):
                    return {
                        **scope,
                        "preview_digest": digest,
                        "preview_nonce": nonce,
                        "expires_at_utc": preview["expires_at"].isoformat(),
                    }
            while len(_PREVIEWS) >= MAX_PREVIEWS:
                oldest_nonce = min(_PREVIEWS, key=lambda key: _PREVIEWS[key]["created_at"])
                del _PREVIEWS[oldest_nonce]
            nonce = uuid.uuid4().hex
            expires_at = now + PREVIEW_TTL
            _PREVIEWS[nonce] = {
                "digest": digest,
                "created_at": now,
                "expires_at": expires_at,
                "scope": scope,
                "session_binding_digest": self._session_binding_digest,
            }
        return {
            **scope,
            "preview_digest": digest,
            "preview_nonce": nonce,
            "expires_at_utc": expires_at.isoformat(),
        }

    def _scope_for_request(self, request: LiveJobRequest) -> dict[str, Any]:
        variants = ["ml_only", "full_evidence"] if request.variant == "both" else [request.variant]
        selected_count = len(request.decision_ids) * len(variants)
        if selected_count > self.max_cards:
            raise LiveJobError(f"Live job limit is {self.max_cards} cards; requested {selected_count}")
        details: list[dict[str, Any]] = []
        for variant in variants:
            packs = self._load_packs(variant)
            for decision_id in request.decision_ids:
                pack = packs.get(decision_id)
                if pack is None:
                    raise LiveJobError(f"Decision ID unavailable in {variant} prompt-safe pack: {decision_id}")
                assert_initial_payload_safe(pack)
                prompt, _, pack_hash = generator.prompt_for_pack(pack)
                details.append(
                    {
                        "decision_id": decision_id,
                        "variant": variant,
                        "pack_sha256": pack_hash,
                        "prompt_sha256": generator.sha256_text(generator.SYSTEM_PROMPT + "\n" + prompt),
                        "technical_cutoff": pack.get("decision_date"),
                        "technical_field_count": len(pack.get("technical_snapshot") or {}),
                        "technical_driver_count": len(pack.get("top_drivers") or []),
                        "external_fireant_ingested": False,
                    }
                )
        return {
            "cards_requested": selected_count,
            "details": details,
            "provider": request.provider,
            "model": request.model,
            "score": request.score,
            "research_only": True,
            "outcome_leakage_check": "passed",
        }

    def run(self, request: LiveJobRequest) -> LiveJobStatus:
        if not request.confirmed_external_call:
            raise LiveJobError("Explicit external-call confirmation is required")
        nonce = request.preview_nonce or ""
        now = _utcnow()
        with _PREVIEW_LOCK:
            _purge_previews_locked(now)
            preview = _PREVIEWS.get(nonce)
            if preview is None or preview["digest"] != request.preview_digest:
                raise LiveJobError("Live-job preview is missing, expired, or does not match this request")
        current_scope = self._scope_for_request(request)
        current_digest = self._preview_digest(current_scope)
        if (
            current_digest != preview["digest"]
            or current_scope != preview["scope"]
            or preview["session_binding_digest"] != self._session_binding_digest
        ):
            raise LiveJobError("Live-job request, session, or prompt-safe pack changed after displayed preview")
        if not _LIVE_JOB_LOCK.acquire(blocking=False):
            raise LiveJobError("Another live LLM job is already running")
        try:
            with _PREVIEW_LOCK:
                _purge_previews_locked(_utcnow())
                current_preview = _PREVIEWS.get(nonce)
                if current_preview is None or current_preview != preview:
                    raise LiveJobError("Live-job preview is missing, expired, or already consumed")
                del _PREVIEWS[nonce]
            authorized_preview = {
                **preview["scope"],
                "preview_digest": preview["digest"],
                "preview_nonce": nonce,
                "expires_at_utc": preview["expires_at"].isoformat(),
            }
            return self._run_confirmed(request, authorized_preview)
        finally:
            _LIVE_JOB_LOCK.release()

    def _run_confirmed(self, request: LiveJobRequest, preview: dict[str, Any]) -> LiveJobStatus:
        job_id = f"live-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{uuid.uuid4().hex[:8]}"
        run_dir = self.root / "reports" / "decision_support" / "generated" / "runs" / job_id
        run_dir.mkdir(parents=True, exist_ok=False)
        created = datetime.now(timezone.utc)
        load_env_file(self.root)
        model = resolve_model(request.provider, request.model)
        manifest: dict[str, Any] = {
            "run_id": job_id,
            "status": "running",
            "provider": request.provider,
            "sdk": provider_sdk_name(request.provider),
            "requested_model": model,
            "thinking": provider_thinking(request.provider),
            "temperature": provider_temperature(request.provider),
            "outcome_removed_from_prompt": True,
            "preview": preview,
            "cards": [],
            "scores": [],
            "failures": [],
            "created_at_utc": created.isoformat(timespec="seconds"),
        }
        try:
            client, provider_module = make_llm_client(request.provider)
            for item in preview["details"]:
                pack = self._load_packs(item["variant"])[item["decision_id"]]
                prompt, _, pack_hash = generator.prompt_for_pack(pack)
                prompt_hash = generator.sha256_text(generator.SYSTEM_PROMPT + "\n" + prompt)
                if pack_hash != item["pack_sha256"] or prompt_hash != item["prompt_sha256"]:
                    raise LiveJobError(f"Prompt-safe pack changed after preview: {item['decision_id']}")
                result = call_generate(request.provider, client, provider_module, model, generator.SYSTEM_PROMPT, prompt, generator.DEFAULT_MAX_TOKENS, generator.DEFAULT_EFFORT)
                card_type = generator.VARIANT_TO_CARD_TYPE[item["variant"]]
                card = {
                    "card_id": f"{job_id}:{card_type}:{item['decision_id']}",
                    "decision_id": item["decision_id"],
                    "card_type": card_type,
                    "card_markdown": result["text"],
                    "provider": request.provider,
                    "requested_model": model,
                    "response_model": result["response_model"],
                    "request_id": result["request_id"],
                    "generated_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "pack_sha256": pack_hash,
                    "prompt_sha256": prompt_hash,
                    "stop_reason": result.get("stop_reason"),
                    "usage": result.get("usage"),
                    "response_vendor": _response_vendor(request.provider, result["response_model"]),
                }
                manifest["cards"].append(card)
                if request.score:
                    manifest["scores"].append(self._score_card(card, pack, client, provider_module, model, request.provider))
            _write_jsonl(run_dir / "cards.jsonl", manifest["cards"])
            _write_scores(run_dir / "rubric_scores.csv", manifest["scores"])
            manifest["status"] = "completed"
        except Exception as exc:
            manifest["status"] = "failed"
            manifest["failures"].append({"stage": "live_generation_or_scoring", "error": str(exc)})
        finally:
            manifest["completed_at_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
            (run_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        return LiveJobStatus(
            job_id=job_id,
            state="completed" if manifest["status"] == "completed" else "failed",
            run_directory=str(run_dir.relative_to(self.root)),
            message="Live research run completed" if manifest["status"] == "completed" else manifest["failures"][-1]["error"],
            created_at_utc=created,
            completed_at_utc=datetime.now(timezone.utc),
        )

    def _load_packs(self, variant: str) -> dict[str, dict[str, Any]]:
        mode = "ml_only" if variant == "ml_only" else "full_evidence"
        if self.bundle_repository is not None:
            return {
                str(candidate["decision_id"]): normalize_initial_prompt_pack(
                    self.bundle_repository.initial(str(candidate["decision_id"]), mode), mode
                )
                for candidate in self.bundle_repository.candidates()
            }
        filename = "evidence_packs_ml_only.json" if mode == "ml_only" else "evidence_packs_initial.json"
        path = self.root / "reports" / "decision_support" / "generated" / filename
        packs = json.loads(path.read_text(encoding="utf-8"))
        provenance = {
            "name": filename,
            "path": path.relative_to(self.root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "zone": "initial",
            "record_count": len(packs),
            "provenance_status": "normalized_from_canonical_prompt_pack",
        }
        return {
            str(pack["decision_id"]): normalize_initial_prompt_pack(pack, mode, provenance)
            for pack in packs
        }

    def _score_card(self, card: dict[str, Any], pack: dict[str, Any], client: Any, provider_module: Any, model: str, provider: str) -> dict[str, Any]:
        score_prompt, prompt_hash = scorer.build_prompt(pack, card)
        response = call_score(provider, client, provider_module, model, scorer.SYSTEM_PROMPT, score_prompt, scorer.DEFAULT_MAX_TOKENS, scorer.DEFAULT_EFFORT, scorer.RUBRIC_SCHEMA)
        normalized = scorer.normalize_score(response["parsed"])
        return {
            "card_id": card["card_id"],
            "decision_id": card["decision_id"],
            "card_type": card["card_type"],
            **normalized,
            "provider": provider,
            "model": response["response_model"],
            "request_id": response["request_id"],
            "scored_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "prompt_sha256": prompt_hash,
        }


def _response_vendor(provider: str, response_model: str) -> str:
    if provider == "anthropic" and re.search(r"gpt-|openai", response_model, flags=re.IGNORECASE):
        return "openai-vendor-via-router"
    return {"anthropic": "anthropic", "gemini": "google", "deepseek": "deepseek"}[provider]


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def _write_scores(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
