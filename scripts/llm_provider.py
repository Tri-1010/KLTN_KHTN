"""Provider-neutral LLM helpers for decision-support scripts.

Loads local .env values without external dependencies and wraps Anthropic/Gemini
SDK calls behind a small normalized interface. Do not log or persist secret values.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-8"
DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
SUPPORTED_PROVIDERS = {"anthropic", "gemini", "deepseek"}
UI_MODEL_ALLOWLIST = {
    "anthropic": (DEFAULT_ANTHROPIC_MODEL,),
    "gemini": (DEFAULT_GEMINI_MODEL,),
    "deepseek": (DEFAULT_DEEPSEEK_MODEL,),
}


class ProviderConfigError(RuntimeError):
    """Raised when provider config, SDK dependency, or credentials are missing."""


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_env_file(root: Path, env_file: Path | None = None) -> dict[str, str]:
    """Load simple KEY=value env file without overriding existing env vars."""
    path = env_file or (root / ".env")
    loaded: dict[str, str] = {}
    if not path.exists():
        return loaded
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if not key:
            continue
        value = strip_quotes(value)
        loaded[key] = value
        if key not in os.environ:
            os.environ[key] = value
    return loaded


def resolve_provider(cli_provider: str | None = None) -> str:
    provider = (cli_provider or os.environ.get("LLM_PROVIDER") or "").strip().lower()
    if not provider:
        if os.environ.get("GEMINI_API_KEY"):
            provider = "gemini"
        elif os.environ.get("ANTHROPIC_API_KEY"):
            provider = "anthropic"
        elif os.environ.get("DEEPSEEK_API_KEY"):
            provider = "deepseek"
        else:
            provider = "anthropic"
    if provider not in SUPPORTED_PROVIDERS:
        raise ProviderConfigError(f"Unsupported LLM provider `{provider}`. Use one of: {', '.join(sorted(SUPPORTED_PROVIDERS))}.")
    return provider


def resolve_model(provider: str, cli_model: str | None = None) -> str:
    if cli_model:
        return cli_model
    if provider == "gemini":
        return os.environ.get("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
    if provider == "deepseek":
        return os.environ.get("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL
    return os.environ.get("ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL


def provider_sdk_name(provider: str) -> str:
    if provider == "gemini":
        return "google-genai"
    if provider == "deepseek":
        return "requests"
    return "anthropic-python"


def provider_thinking(provider: str) -> Any:
    return {"type": "adaptive"} if provider == "anthropic" else "not_sent"


def provider_temperature(provider: str) -> int | str:
    """Return temperature actually included in provider requests."""
    return 0 if provider == "deepseek" else "not_sent"


def artifact_ref(root: Path, path: Path | str) -> str:
    """Return portable repo-relative path for artifact metadata."""
    artifact_path = Path(path)
    try:
        return artifact_path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return artifact_path.as_posix()


def make_llm_client(provider: str) -> tuple[Any, Any]:
    if provider == "anthropic":
        try:
            import anthropic
        except ModuleNotFoundError as exc:
            raise ProviderConfigError("Missing dependency `anthropic`. Install requirements or run offline mode.") from exc
        return anthropic.Anthropic(), anthropic

    if provider == "gemini":
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ProviderConfigError("Missing `GEMINI_API_KEY`. Add it to .env or process environment, or run offline mode.")
        try:
            from google import genai
        except ModuleNotFoundError as exc:
            raise ProviderConfigError("Missing dependency `google-genai`. Install requirements or run offline mode.") from exc
        return genai.Client(api_key=api_key), genai

    if provider == "deepseek":
        api_key = os.environ.get("DEEPSEEK_API_KEY")
        if not api_key:
            raise ProviderConfigError("Missing `DEEPSEEK_API_KEY`. Add it to .env or process environment, or run offline mode.")
        try:
            import requests
        except ModuleNotFoundError as exc:
            raise ProviderConfigError("Missing dependency `requests`. Install requirements or run offline mode.") from exc
        return {
            "api_key": api_key,
            "base_url": (os.environ.get("DEEPSEEK_BASE_URL") or DEFAULT_DEEPSEEK_BASE_URL).rstrip("/"),
            "timeout": float(os.environ.get("DEEPSEEK_TIMEOUT", "120")),
        }, requests

    raise ProviderConfigError(f"Unsupported LLM provider `{provider}`.")


def is_auth_error(provider: str, exc: Exception, provider_module: Any | None = None) -> bool:
    if provider == "anthropic" and provider_module is not None:
        auth_types = []
        for name in ("AuthenticationError", "PermissionDeniedError"):
            typ = getattr(provider_module, name, None)
            if typ is not None:
                auth_types.append(typ)
        if auth_types and isinstance(exc, tuple(auth_types)):
            return True
    if isinstance(exc, ProviderConfigError):
        return True
    message = str(exc).lower()
    auth_markers = (
        "no active credentials",
        "missing `gemini_api_key`",
        "invalid api key",
        "invalid x-api-key",
        "api key not valid",
        "authentication",
        "permission denied",
        "unauthorized",
        "401",
        "403",
    )
    return any(marker in message for marker in auth_markers)


def anthropic_text(response: Any) -> str:
    """Extract assistant text from Anthropic SDK or 9router/OpenAI-compatible response."""
    content = getattr(response, "content", None)
    if content:
        text_parts = []
        for block in content:
            if getattr(block, "type", None) == "text":
                text_parts.append(getattr(block, "text", ""))
            elif isinstance(block, dict) and block.get("type") == "text":
                text_parts.append(str(block.get("text", "")))
        text = "\n".join(part for part in text_parts if part).strip()
        if text:
            return text

    data = None
    if hasattr(response, "model_dump"):
        data = response.model_dump()
    elif hasattr(response, "to_dict"):
        data = response.to_dict()

    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            choice_content = message.get("content")
            if isinstance(choice_content, str):
                return choice_content.strip()
            if isinstance(choice_content, list):
                parts = []
                for item in choice_content:
                    if isinstance(item, dict):
                        parts.append(str(item.get("text") or item.get("content") or ""))
                text = "\n".join(part for part in parts if part).strip()
                if text:
                    return text

    return ""


def response_usage(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value if isinstance(value, dict) else str(value or "")


def _finish_reason_text(value: Any) -> str:
    """Normalize SDK enum/string finish reasons without depending on enum classes."""
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        name = getattr(value, "name", None)
        enum_value = getattr(value, "value", None)
        text = name if isinstance(name, str) and name else enum_value if isinstance(enum_value, str) else str(value)
    return text.rsplit(".", 1)[-1].strip()


def _gemini_finish_reason(response: Any) -> str:
    candidates = getattr(response, "candidates", None) or []
    if candidates:
        candidate = candidates[0]
        value = candidate.get("finish_reason") if isinstance(candidate, dict) else getattr(candidate, "finish_reason", None)
        return _finish_reason_text(value)
    return _finish_reason_text(getattr(response, "finish_reason", None))


def _normalize_finish_reason(value: Any) -> str:
    reason = _finish_reason_text(value)
    return re.sub(r"[^A-Z0-9]+", "", reason.upper())


def _raise_if_truncated(provider: str, finish_reason: Any) -> str:
    reason = _finish_reason_text(finish_reason)
    normalized = _normalize_finish_reason(reason)
    token_limit_reasons = {"MAXTOKEN", "MAXTOKENS", "TOKENLIMIT", "TOKENLIMITREACHED", "LENGTH"}
    context_limit_reasons = {
        "MODELCONTEXTWINDOWEXCEEDED",
        "CONTEXTWINDOWEXCEEDED",
        "CONTEXTLENGTHEXCEEDED",
        "MAXCONTEXTLENGTH",
        "MAXCONTEXTWINDOW",
    }
    if normalized in token_limit_reasons:
        raise RuntimeError(f"{provider.capitalize()} response truncated at token limit (finish_reason={reason})")
    if normalized in context_limit_reasons:
        raise RuntimeError(f"{provider.capitalize()} response truncated at context window limit (finish_reason={reason})")
    return reason


def _sanitize_anthropic_schema(value: Any) -> Any:
    """Copy JSON Schema while removing numeric constraints unsupported by Anthropic."""
    if isinstance(value, dict):
        return {
            key: _sanitize_anthropic_schema(item)
            for key, item in value.items()
            if key not in {"minimum", "maximum"}
        }
    if isinstance(value, list):
        return [_sanitize_anthropic_schema(item) for item in value]
    return value


def _fallback_contents(system_prompt: str, user_prompt: str) -> str:
    return (
        "<SYSTEM_INSTRUCTIONS>\n"
        f"{system_prompt}\n"
        "</SYSTEM_INSTRUCTIONS>\n\n"
        "<USER_CONTENT>\n"
        f"{user_prompt}\n"
        "</USER_CONTENT>"
    )


def _gemini_generate_content(
    client: Any,
    provider_module: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    config: dict[str, Any],
) -> Any:
    """Call Gemini while preserving system instructions across SDK compatibility fallbacks."""
    types = getattr(provider_module, "types", None)
    generate_config = getattr(types, "GenerateContentConfig", None) if types is not None else None
    try:
        config_obj = generate_config(**config) if generate_config is not None else config
        return client.models.generate_content(model=model, contents=user_prompt, config=config_obj)
    except TypeError:
        fallback_config = {key: value for key, value in config.items() if key != "system_instruction"}
        contents = _fallback_contents(system_prompt, user_prompt)
        try:
            config_obj = generate_config(**fallback_config) if generate_config is not None else fallback_config
            return client.models.generate_content(model=model, contents=contents, config=config_obj)
        except TypeError as exc:
            raise RuntimeError("Gemini SDK rejected required generation config after system-prompt fallback") from exc


def _deepseek_chat(
    client: dict[str, Any],
    requests_module: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    response_format: dict[str, str] | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    if response_format is not None:
        body["response_format"] = response_format

    response = requests_module.post(
        f"{client['base_url']}/chat/completions",
        headers={
            "Authorization": f"Bearer {client['api_key']}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=client.get("timeout", 120),
    )
    try:
        payload = response.json()
    except ValueError:
        payload = {"raw_text": response.text}
    if response.status_code >= 400:
        message = payload.get("error", payload) if isinstance(payload, dict) else payload
        raise RuntimeError(f"DeepSeek API error {response.status_code}: {message}")
    if not isinstance(payload, dict):
        raise RuntimeError("DeepSeek API returned non-object JSON")
    return payload


def _deepseek_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    message = choices[0].get("message") or {}
    content = message.get("content")
    return content.strip() if isinstance(content, str) else ""


def _json_schema_prompt(schema: dict[str, Any]) -> str:
    required = schema.get("required") if isinstance(schema, dict) else None
    required_text = ", ".join(str(item) for item in required) if isinstance(required, list) else ""
    return (
        "Return exactly one JSON object. Do not wrap it in markdown. "
        "Conform to this JSON Schema exactly. Include every required key"
        f"{f': {required_text}' if required_text else ''}. "
        "If evidence is limited, choose the best valid value from the schema instead of omitting the key.\n"
        f"JSON Schema:\n{json.dumps(schema, ensure_ascii=False, sort_keys=True)}"
    )


def call_generate(
    provider: str,
    client: Any,
    provider_module: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    effort: str,
) -> dict[str, Any]:
    if provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            thinking={"type": "adaptive"},
            output_config={"effort": effort},
            messages=[{"role": "user", "content": user_prompt}],
        )
        stop_reason = getattr(response, "stop_reason", None)
        if stop_reason == "refusal":
            raise RuntimeError(f"Claude refusal: {getattr(response, 'stop_details', None)}")
        stop_reason = _raise_if_truncated("Anthropic", stop_reason)
        text = anthropic_text(response)
        if not text:
            raise RuntimeError("LLM response contained no text block")
        return {
            "text": text,
            "request_id": getattr(response, "_request_id", ""),
            "response_model": getattr(response, "model", model),
            "stop_reason": stop_reason,
            "usage": response_usage(getattr(response, "usage", None)),
        }

    if provider == "deepseek":
        payload = _deepseek_chat(client, provider_module, model, system_prompt, user_prompt, max_tokens)
        choice = (payload.get("choices") or [{}])[0]
        stop_reason = _raise_if_truncated("DeepSeek", choice.get("finish_reason"))
        text = _deepseek_text(payload)
        if not text:
            raise RuntimeError("DeepSeek response contained no text")
        return {
            "text": text,
            "request_id": payload.get("id", ""),
            "response_model": payload.get("model", model),
            "stop_reason": stop_reason,
            "usage": response_usage(payload.get("usage")),
        }

    config = {
        "system_instruction": system_prompt,
        "max_output_tokens": max_tokens,
    }
    response = _gemini_generate_content(client, provider_module, model, system_prompt, user_prompt, config)
    stop_reason = _raise_if_truncated("Gemini", _gemini_finish_reason(response))
    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("LLM response contained no text")
    return {
        "text": text,
        "request_id": getattr(response, "request_id", ""),
        "response_model": getattr(response, "model_version", model) or model,
        "stop_reason": stop_reason,
        "usage": response_usage(getattr(response, "usage_metadata", None)),
    }


def call_score(
    provider: str,
    client: Any,
    provider_module: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    effort: str,
    schema: dict[str, Any],
) -> dict[str, Any]:
    if provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            thinking={"type": "adaptive"},
            output_config={
                "effort": effort,
                "format": {"type": "json_schema", "schema": _sanitize_anthropic_schema(schema)},
            },
            messages=[{"role": "user", "content": user_prompt}],
        )
        stop_reason = getattr(response, "stop_reason", None)
        if stop_reason == "refusal":
            raise RuntimeError(f"Claude refusal while scoring: {getattr(response, 'stop_details', None)}")
        _raise_if_truncated("Anthropic", stop_reason)
        text = anthropic_text(response)
        if not text:
            raise RuntimeError("Scorer response contained no text")
        return {
            "parsed": json.loads(text),
            "request_id": getattr(response, "_request_id", ""),
            "response_model": getattr(response, "model", model),
        }

    if provider == "deepseek":
        schema_prompt = f"{user_prompt}\n\n{_json_schema_prompt(schema)}"
        payload = _deepseek_chat(
            client,
            provider_module,
            model,
            system_prompt,
            schema_prompt,
            max_tokens,
            response_format={"type": "json_object"},
        )
        choice = (payload.get("choices") or [{}])[0]
        _raise_if_truncated("DeepSeek", choice.get("finish_reason"))
        text = _deepseek_text(payload)
        if not text:
            raise RuntimeError("DeepSeek scorer response contained no text")
        return {
            "parsed": json.loads(text),
            "request_id": payload.get("id", ""),
            "response_model": payload.get("model", model),
        }

    config = {
        "system_instruction": system_prompt,
        "max_output_tokens": max_tokens,
        "response_mime_type": "application/json",
    }
    response = _gemini_generate_content(client, provider_module, model, system_prompt, user_prompt, config)
    _raise_if_truncated("Gemini", _gemini_finish_reason(response))
    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("Scorer response contained no text")
    return {
        "parsed": json.loads(text),
        "request_id": getattr(response, "request_id", ""),
        "response_model": getattr(response, "model_version", model) or model,
    }
