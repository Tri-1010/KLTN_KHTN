"""Provider-neutral LLM helpers for research scripts.

Loads local environment values without persisting credentials and normalizes the
Anthropic, Gemini, DeepSeek, and restricted loopback-router response shapes.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

DEFAULT_ANTHROPIC_MODEL = "claude-opus-4-8"
DEFAULT_GEMINI_MODEL = "gemini-2.5-pro"
DEFAULT_DEEPSEEK_MODEL = "deepseek-chat"
DEFAULT_DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"

# The V6 confirmation protocol allows this historic alias only. It is deliberately
# not an arbitrary model selector: the local OpenAI-compatible endpoint must stay
# on loopback and the requested alias must stay in this immutable allowlist.
DEFAULT_LOCAL_ROUTER_MODEL = "claude-opus"
LOCAL_ROUTER_MODEL_ALLOWLIST = (DEFAULT_LOCAL_ROUTER_MODEL,)
LOCAL_ROUTER_URL_ENV = "URL_LOCAL"
LOCAL_ROUTER_API_KEY_ENV = "API_LOCAL"

SUPPORTED_PROVIDERS = {"anthropic", "gemini", "deepseek", "local_router"}
UI_MODEL_ALLOWLIST = {
    "anthropic": (DEFAULT_ANTHROPIC_MODEL,),
    "gemini": (DEFAULT_GEMINI_MODEL,),
    "deepseek": (DEFAULT_DEEPSEEK_MODEL,),
    "local_router": LOCAL_ROUTER_MODEL_ALLOWLIST,
}


class ProviderConfigError(RuntimeError):
    """Raised when provider configuration, credentials, or endpoint policy fails."""


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def load_env_file(root: Path, env_file: Path | None = None) -> dict[str, str]:
    """Load simple KEY=value settings without overriding existing environment values."""
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
        raise ProviderConfigError(
            f"Unsupported LLM provider `{provider}`. Use one of: {', '.join(sorted(SUPPORTED_PROVIDERS))}."
        )
    return provider


def resolve_model(provider: str, cli_model: str | None = None) -> str:
    if provider == "local_router":
        model = cli_model or os.environ.get("LOCAL_ROUTER_MODEL") or DEFAULT_LOCAL_ROUTER_MODEL
        if model not in LOCAL_ROUTER_MODEL_ALLOWLIST:
            raise ProviderConfigError("Local router model is not approved by the V6 confirmation protocol")
        return model
    if cli_model:
        return cli_model
    if provider == "gemini":
        return os.environ.get("GEMINI_MODEL") or DEFAULT_GEMINI_MODEL
    if provider == "deepseek":
        return os.environ.get("DEEPSEEK_MODEL") or DEFAULT_DEEPSEEK_MODEL
    return os.environ.get("ANTHROPIC_MODEL") or DEFAULT_ANTHROPIC_MODEL


def _loopback_router_url(value: str | None = None) -> str:
    """Validate an HTTP loopback OpenAI-compatible base URL without credentials."""
    raw = (value or os.environ.get(LOCAL_ROUTER_URL_ENV) or "").strip().rstrip("/")
    if not raw:
        raise ProviderConfigError(f"Missing `{LOCAL_ROUTER_URL_ENV}` for the local router")
    parsed = urlparse(raw)
    if parsed.scheme != "http" or parsed.hostname not in {"localhost", "127.0.0.1"}:
        raise ProviderConfigError("Local router URL must use http://localhost or http://127.0.0.1")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ProviderConfigError("Local router URL must not include credentials, query, or fragment")
    if parsed.path.rstrip("/") not in {"", "/v1"}:
        raise ProviderConfigError("Local router URL path must be empty or /v1")
    return raw


def local_router_endpoint_host(value: str | None = None) -> str:
    """Return host[:port] provenance only; no URL path or credential is exposed."""
    parsed = urlparse(_loopback_router_url(value))
    return f"{parsed.hostname}:{parsed.port}" if parsed.port else str(parsed.hostname)


def provider_sdk_name(provider: str) -> str:
    if provider == "gemini":
        return "google-genai"
    if provider in {"deepseek", "local_router"}:
        return "requests"
    return "anthropic-python"


def provider_thinking(provider: str) -> Any:
    return {"type": "adaptive"} if provider == "anthropic" else "not_sent"


def provider_temperature(provider: str) -> int | str:
    """Return the temperature actually sent to the provider."""
    return 0 if provider in {"deepseek", "local_router"} else "not_sent"


def provider_route_provenance(provider: str, response_model: str | None = None) -> dict[str, str]:
    """Return safe route metadata suitable for manifests; never include a secret."""
    if provider == "local_router":
        return {
            "api_provider": "local_router",
            "endpoint_host": local_router_endpoint_host(),
            "model_vendor": "unknown_local_router",
            "route_mode": "openai_compatible_loopback",
            "response_model": response_model or "",
        }
    return {
        "api_provider": provider,
        "endpoint_host": "default",
        "model_vendor": "unknown",
        "route_mode": "native",
        "response_model": response_model or "",
    }


def artifact_ref(root: Path, path: Path | str) -> str:
    """Return a portable repo-relative artifact reference when available."""
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
            "provider": "deepseek",
        }, requests

    if provider == "local_router":
        api_key = os.environ.get(LOCAL_ROUTER_API_KEY_ENV)
        if not api_key:
            raise ProviderConfigError(f"Missing `{LOCAL_ROUTER_API_KEY_ENV}` for the local router")
        try:
            import requests
        except ModuleNotFoundError as exc:
            raise ProviderConfigError("Missing dependency `requests`. Install requirements or run offline mode.") from exc
        return {
            "api_key": api_key,
            "base_url": _loopback_router_url(),
            "timeout": float(os.environ.get("LOCAL_ROUTER_TIMEOUT", "120")),
            "provider": "local_router",
            "endpoint_host": local_router_endpoint_host(),
        }, requests

    raise ProviderConfigError(f"Unsupported LLM provider `{provider}`.")


def is_auth_error(provider: str, exc: Exception, provider_module: Any | None = None) -> bool:
    if provider == "anthropic" and provider_module is not None:
        auth_types = [
            typ
            for name in ("AuthenticationError", "PermissionDeniedError")
            if (typ := getattr(provider_module, name, None)) is not None
        ]
        if auth_types and isinstance(exc, tuple(auth_types)):
            return True
    if isinstance(exc, ProviderConfigError):
        return True
    message = str(exc).lower()
    return any(marker in message for marker in (
        "no active credentials", "missing `gemini_api_key`", "invalid api key", "invalid x-api-key",
        "api key not valid", "authentication", "permission denied", "unauthorized", "401", "403",
    ))


def anthropic_text(response: Any) -> str:
    """Extract assistant text from Anthropic SDK or compatible response objects."""
    content = getattr(response, "content", None)
    if content:
        parts = []
        for block in content:
            if getattr(block, "type", None) == "text":
                parts.append(getattr(block, "text", ""))
            elif isinstance(block, dict) and block.get("type") == "text":
                parts.append(str(block.get("text", "")))
        text = "\n".join(part for part in parts if part).strip()
        if text:
            return text
    data = response.model_dump() if hasattr(response, "model_dump") else response.to_dict() if hasattr(response, "to_dict") else None
    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices:
            content_value = (choices[0].get("message") or {}).get("content")
            if isinstance(content_value, str):
                return content_value.strip()
    return ""


def response_usage(value: Any) -> Any:
    if hasattr(value, "to_dict"):
        return value.to_dict()
    if hasattr(value, "model_dump"):
        return value.model_dump()
    return value if isinstance(value, dict) else str(value or "")


def _finish_reason_text(value: Any) -> str:
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
    return re.sub(r"[^A-Z0-9]+", "", _finish_reason_text(value).upper())


def _raise_if_truncated(provider: str, finish_reason: Any) -> str:
    reason = _finish_reason_text(finish_reason)
    normalized = _normalize_finish_reason(reason)
    if normalized in {"MAXTOKEN", "MAXTOKENS", "TOKENLIMIT", "TOKENLIMITREACHED", "LENGTH"}:
        raise RuntimeError(f"{provider} response truncated at token limit (finish_reason={reason})")
    if normalized in {"MODELCONTEXTWINDOWEXCEEDED", "CONTEXTWINDOWEXCEEDED", "CONTEXTLENGTHEXCEEDED", "MAXCONTEXTLENGTH", "MAXCONTEXTWINDOW"}:
        raise RuntimeError(f"{provider} response truncated at context window limit (finish_reason={reason})")
    return reason


def _sanitize_anthropic_schema(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: _sanitize_anthropic_schema(item) for key, item in value.items() if key not in {"minimum", "maximum"}}
    if isinstance(value, list):
        return [_sanitize_anthropic_schema(item) for item in value]
    return value


def _fallback_contents(system_prompt: str, user_prompt: str) -> str:
    return f"<SYSTEM_INSTRUCTIONS>\n{system_prompt}\n</SYSTEM_INSTRUCTIONS>\n\n<USER_CONTENT>\n{user_prompt}\n</USER_CONTENT>"


def _gemini_generate_content(client: Any, provider_module: Any, model: str, system_prompt: str, user_prompt: str, config: dict[str, Any]) -> Any:
    types = getattr(provider_module, "types", None)
    generate_config = getattr(types, "GenerateContentConfig", None) if types is not None else None
    try:
        config_object = generate_config(**config) if generate_config is not None else config
        return client.models.generate_content(model=model, contents=user_prompt, config=config_object)
    except TypeError:
        fallback_config = {key: value for key, value in config.items() if key != "system_instruction"}
        try:
            config_object = generate_config(**fallback_config) if generate_config is not None else fallback_config
            return client.models.generate_content(model=model, contents=_fallback_contents(system_prompt, user_prompt), config=config_object)
        except TypeError as exc:
            raise RuntimeError("Gemini SDK rejected required generation config after system-prompt fallback") from exc


def _openai_compatible_chat(
    client: dict[str, Any],
    requests_module: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    response_format: dict[str, str] | None = None,
) -> dict[str, Any]:
    provider = str(client.get("provider") or "deepseek")
    if provider == "local_router":
        validated = _loopback_router_url(str(client.get("base_url") or ""))
        if validated != str(client.get("base_url") or "").rstrip("/"):
            raise ProviderConfigError("Local router client URL changed after validation")
        if model not in LOCAL_ROUTER_MODEL_ALLOWLIST:
            raise ProviderConfigError("Local router model is not approved by the V6 confirmation protocol")
    body: dict[str, Any] = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
    }
    if response_format is not None:
        body["response_format"] = response_format
    response = requests_module.post(
        f"{client['base_url']}/chat/completions",
        headers={"Authorization": f"Bearer {client['api_key']}", "Content-Type": "application/json"},
        json=body,
        timeout=client.get("timeout", 120),
        allow_redirects=False,
    )
    if 300 <= response.status_code < 400:
        label = "Local router" if provider == "local_router" else "DeepSeek"
        raise RuntimeError(f"{label} API refused redirect status {response.status_code}")
    try:
        payload = response.json()
    except ValueError:
        payload = {"error_type": "non_json_response"}
    if response.status_code >= 400:
        message = payload.get("error", payload) if isinstance(payload, dict) else "provider_error"
        if isinstance(message, dict):
            message = {key: message.get(key) for key in ("type", "code", "message") if key in message}
        label = "Local router" if provider == "local_router" else "DeepSeek"
        raise RuntimeError(f"{label} API error {response.status_code}: {message}")
    if not isinstance(payload, dict):
        raise RuntimeError("OpenAI-compatible API returned non-object JSON")
    return payload


def _deepseek_chat(
    client: dict[str, Any],
    requests_module: Any,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    response_format: dict[str, str] | None = None,
) -> dict[str, Any]:
    return _openai_compatible_chat(client, requests_module, model, system_prompt, user_prompt, max_tokens, response_format)


def _deepseek_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices") or []
    if not choices:
        return ""
    content = (choices[0].get("message") or {}).get("content")
    return content.strip() if isinstance(content, str) else ""


def _json_schema_prompt(schema: dict[str, Any]) -> str:
    required = schema.get("required") if isinstance(schema, dict) else None
    required_text = ", ".join(str(item) for item in required) if isinstance(required, list) else ""
    return (
        "Return exactly one JSON object. Do not wrap it in markdown. Conform to this JSON Schema exactly. "
        f"Include every required key{f': {required_text}' if required_text else ''}. "
        "If evidence is limited, choose the best valid value from the schema instead of omitting the key.\n"
        f"JSON Schema:\n{json.dumps(schema, ensure_ascii=False, sort_keys=True)}"
    )


def call_generate(provider: str, client: Any, provider_module: Any, model: str, system_prompt: str, user_prompt: str, max_tokens: int, effort: str) -> dict[str, Any]:
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
        return {"text": text, "request_id": getattr(response, "_request_id", ""), "response_model": getattr(response, "model", model), "stop_reason": stop_reason, "usage": response_usage(getattr(response, "usage", None))}

    if provider in {"deepseek", "local_router"}:
        payload = _openai_compatible_chat(client, provider_module, model, system_prompt, user_prompt, max_tokens)
        choice = (payload.get("choices") or [{}])[0]
        label = "Local router" if provider == "local_router" else "DeepSeek"
        stop_reason = _raise_if_truncated(label, choice.get("finish_reason"))
        text = _deepseek_text(payload)
        if not text:
            raise RuntimeError(f"{label} response contained no text")
        result = {"text": text, "request_id": payload.get("id", ""), "response_model": payload.get("model", model), "stop_reason": stop_reason, "usage": response_usage(payload.get("usage"))}
        if provider == "local_router":
            result["route_provenance"] = provider_route_provenance(provider, str(payload.get("model") or model))
        return result

    config = {"system_instruction": system_prompt, "max_output_tokens": max_tokens}
    response = _gemini_generate_content(client, provider_module, model, system_prompt, user_prompt, config)
    stop_reason = _raise_if_truncated("Gemini", _gemini_finish_reason(response))
    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("LLM response contained no text")
    return {"text": text, "request_id": getattr(response, "request_id", ""), "response_model": getattr(response, "model_version", model) or model, "stop_reason": stop_reason, "usage": response_usage(getattr(response, "usage_metadata", None))}


def call_score(provider: str, client: Any, provider_module: Any, model: str, system_prompt: str, user_prompt: str, max_tokens: int, effort: str, schema: dict[str, Any]) -> dict[str, Any]:
    if provider == "anthropic":
        response = client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system_prompt,
            thinking={"type": "adaptive"},
            output_config={"effort": effort, "format": {"type": "json_schema", "schema": _sanitize_anthropic_schema(schema)}},
            messages=[{"role": "user", "content": user_prompt}],
        )
        stop_reason = getattr(response, "stop_reason", None)
        if stop_reason == "refusal":
            raise RuntimeError(f"Claude refusal while scoring: {getattr(response, 'stop_details', None)}")
        _raise_if_truncated("Anthropic", stop_reason)
        text = anthropic_text(response)
        if not text:
            raise RuntimeError("Scorer response contained no text")
        return {"parsed": json.loads(text), "request_id": getattr(response, "_request_id", ""), "response_model": getattr(response, "model", model), "stop_reason": stop_reason, "usage": response_usage(getattr(response, "usage", None))}

    if provider in {"deepseek", "local_router"}:
        payload = _openai_compatible_chat(
            client,
            provider_module,
            model,
            system_prompt,
            f"{user_prompt}\n\n{_json_schema_prompt(schema)}",
            max_tokens,
            response_format={"type": "json_object"},
        )
        choice = (payload.get("choices") or [{}])[0]
        label = "Local router" if provider == "local_router" else "DeepSeek"
        stop_reason = _raise_if_truncated(label, choice.get("finish_reason"))
        text = _deepseek_text(payload)
        if not text:
            raise RuntimeError(f"{label} scorer response contained no text")
        result = {"parsed": json.loads(text), "request_id": payload.get("id", ""), "response_model": payload.get("model", model), "stop_reason": stop_reason, "usage": response_usage(payload.get("usage"))}
        if provider == "local_router":
            result["route_provenance"] = provider_route_provenance(provider, str(payload.get("model") or model))
        return result

    config = {"system_instruction": system_prompt, "max_output_tokens": max_tokens, "response_mime_type": "application/json"}
    response = _gemini_generate_content(client, provider_module, model, system_prompt, user_prompt, config)
    stop_reason = _gemini_finish_reason(response)
    _raise_if_truncated("Gemini", stop_reason)
    text = (getattr(response, "text", "") or "").strip()
    if not text:
        raise RuntimeError("Scorer response contained no text")
    return {"parsed": json.loads(text), "request_id": getattr(response, "request_id", ""), "response_model": getattr(response, "model_version", model) or model, "stop_reason": stop_reason, "usage": response_usage(getattr(response, "usage_metadata", None))}
