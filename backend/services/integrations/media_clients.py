from __future__ import annotations

import logging
import os
import time
from dataclasses import dataclass
from typing import Callable, Optional, Union, Any

import httpx

from core.config import get_settings
from services.integrations.media_store import get_webhook_result

logger = logging.getLogger(__name__)


class MediaProviderError(RuntimeError):
    pass


def _require_env(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise MediaProviderError(f"{key} is missing. Add it to your environment.")
    return value


def _poll_until_complete(*, status_url: str, headers: dict, timeout_sec: int = 180, interval_sec: int = 5):
    started = time.time()
    with httpx.Client(timeout=30.0) as client:
        while time.time() - started < timeout_sec:
            resp = client.get(status_url, headers=headers)
            resp.raise_for_status()
            payload = resp.json()

            status = str(payload.get("status", "")).lower()
            if status in {"completed", "done", "success", "ready"}:
                return payload
            if status in {"failed", "error", "cancelled"}:
                raise MediaProviderError(f"Remote job failed with status: {status}")

            time.sleep(interval_sec)

    raise MediaProviderError("Timed out while waiting for media provider job completion.")


def _request_with_retry(method: str, url: str, *, headers: dict, json_payload: Optional[dict] = None, max_attempts: int = 4):
    backoff = 1.0
    last_error = None
    with httpx.Client(timeout=30.0) as client:
        for attempt in range(max_attempts):
            try:
                resp = client.request(method, url, headers=headers, json=json_payload)
                if resp.status_code in {429, 500, 502, 503, 504}:
                    raise httpx.HTTPStatusError(
                        f"Retryable HTTP status {resp.status_code}",
                        request=resp.request,
                        response=resp,
                    )
                resp.raise_for_status()
                return resp
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_error = exc
                if attempt == max_attempts - 1:
                    break
                time.sleep(backoff)
                backoff = min(backoff * 2, 8.0)
    raise MediaProviderError(f"Request failed after retries: {last_error}")


def _extract_asset_url(payload: dict):
    for key in ("asset_url", "url", "video_url", "audio_url", "download_url"):
        if payload.get(key):
            return payload.get(key)
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("url", "asset_url", "video_url", "audio_url"):
            if data.get(key):
                return data.get(key)
    return None


def _normalize_response(provider: str, payload: dict):
    status = str(payload.get("status", "unknown")).lower()
    external_job_id = payload.get("job_id") or payload.get("id")
    asset_url = _extract_asset_url(payload)
    return {
        "provider": provider,
        "status": status,
        "external_job_id": external_job_id,
        "asset_url": asset_url,
        "raw": payload,
    }


def _build_adcreative_payload(payload: dict) -> dict:
    normalized = dict(payload or {})
    normalized.setdefault("ad_type", "social")
    normalized.setdefault("platform", "meta")
    return normalized


def _build_pictory_payload(payload: dict) -> dict:
    normalized = dict(payload or {})
    if normalized.get("script") and not normalized.get("text"):
        normalized["text"] = normalized["script"]
    normalized.setdefault("aspect_ratio", "16:9")
    return normalized


def _build_elevenlabs_payload(payload: dict) -> dict:
    normalized = dict(payload or {})
    normalized.setdefault(
        "voice_settings",
        {"stability": 0.5, "similarity_boost": 0.75},
    )
    return normalized


def _wait_for_webhook_or_poll(*, provider: str, request_id: Optional[str], status_url: str, headers: dict):
    started = time.time()
    timeout_sec = 180
    while time.time() - started < timeout_sec:
        if request_id:
            webhook_payload = get_webhook_result(provider, request_id)
            if webhook_payload:
                return webhook_payload
        time.sleep(2)
        try:
            return _poll_until_complete(status_url=status_url, headers=headers, timeout_sec=30, interval_sec=3)
        except MediaProviderError:
            continue
    raise MediaProviderError("Timed out waiting for webhook or polling completion.")


@dataclass(frozen=True)
class MediaProviderSpec:
    name: str
    api_key_env: str
    base_url_env: str
    default_base: str
    submit_path: str
    status_path_format: str
    build_payload: Callable[[dict], dict]
    auth_kind: str


def _auth_headers(spec: MediaProviderSpec, api_key: str) -> dict[str, str]:
    if spec.auth_kind == "bearer":
        return {"Authorization": f"Bearer {api_key}"}
    return {"xi-api-key": api_key}


def _mock_auth_headers(spec: MediaProviderSpec) -> dict[str, str]:
    if spec.auth_kind == "bearer":
        return {"Authorization": "Bearer mock"}
    return {"xi-api-key": "mock"}


_SPECS: dict[str, MediaProviderSpec] = {
    "adcreative": MediaProviderSpec(
        name="adcreative",
        api_key_env="ADCREATIVE_API_KEY",
        base_url_env="ADCREATIVE_BASE_URL",
        default_base="https://api.adcreative.ai",
        submit_path="/v1/creatives",
        status_path_format="/v1/creatives/{job_id}",
        build_payload=_build_adcreative_payload,
        auth_kind="bearer",
    ),
    "pictory": MediaProviderSpec(
        name="pictory",
        api_key_env="PICTORY_API_KEY",
        base_url_env="PICTORY_BASE_URL",
        default_base="https://api.pictory.ai",
        submit_path="/v1/videos",
        status_path_format="/v1/videos/{job_id}",
        build_payload=_build_pictory_payload,
        auth_kind="bearer",
    ),
    "elevenlabs": MediaProviderSpec(
        name="elevenlabs",
        api_key_env="ELEVENLABS_API_KEY",
        base_url_env="ELEVENLABS_BASE_URL",
        default_base="https://api.elevenlabs.io",
        submit_path="/v1/generate",
        status_path_format="/v1/generate/{job_id}",
        build_payload=_build_elevenlabs_payload,
        auth_kind="xi_api",
    ),
}


def _run_media(spec: MediaProviderSpec, payload: dict, request_id: Optional[str]) -> dict:
    settings = get_settings()
    base_url = os.getenv(spec.base_url_env, spec.default_base).rstrip("/")

    if settings.mock_media_enabled:
        submit_data = {"job_id": f"mock-{spec.name}-{int(time.time())}", "status": "processing"}
        headers = _mock_auth_headers(spec)
        logger.info("media.mock_submit provider=%s request_id=%s", spec.name, request_id)
    else:
        api_key = _require_env(spec.api_key_env)
        headers = _auth_headers(spec, api_key)
        request_payload = spec.build_payload(payload)
        url = f"{base_url}{spec.submit_path}"
        logger.info("media.submit provider=%s url=%s request_id=%s", spec.name, url, request_id)
        submit_resp = _request_with_retry("POST", url, json_payload=request_payload, headers=headers)
        submit_data = submit_resp.json()

    job_id = submit_data.get("job_id") or submit_data.get("id")
    if not job_id:
        return _normalize_response(spec.name, submit_data)

    status_url = f"{base_url}{spec.status_path_format.format(job_id=job_id)}"
    result = _wait_for_webhook_or_poll(
        provider=spec.name,
        request_id=request_id,
        status_url=status_url,
        headers=headers,
    )
    logger.info("media.complete provider=%s request_id=%s", spec.name, request_id)
    return _normalize_response(spec.name, result)


def create_adcreative(payload: dict, request_id: Optional[str] = None) -> dict:
    return _run_media(_SPECS["adcreative"], payload, request_id)


def create_pictory_video(payload: dict, request_id: Optional[str] = None) -> dict:
    return _run_media(_SPECS["pictory"], payload, request_id)


def create_elevenlabs_voiceover(payload: dict, request_id: Optional[str] = None) -> dict:
    return _run_media(_SPECS["elevenlabs"], payload, request_id)
