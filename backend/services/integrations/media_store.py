import json

from redis import Redis

from core.config import get_settings


def _redis_client() -> Redis:
    return Redis.from_url(get_settings().redis_url, decode_responses=True)


def save_webhook_result(provider: str, request_id: str, payload: dict, ttl_sec: int = 3600):
    key = f"media:webhook:{provider}:{request_id}"
    client = _redis_client()
    client.setex(key, ttl_sec, json.dumps(payload))


def get_webhook_result(provider: str, request_id: str):
    key = f"media:webhook:{provider}:{request_id}"
    client = _redis_client()
    raw = client.get(key)
    if not raw:
        return None
    return json.loads(raw)
