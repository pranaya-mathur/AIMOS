
import logging

from openai import OpenAI

from core.config import get_settings

logger = logging.getLogger(__name__)


def _get_client():
    api_key = get_settings().openai_api_key
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is missing. Add it to your environment before calling AI agents.")
    return OpenAI(api_key=api_key)


def generate_text(prompt):
    client = _get_client()
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    usage = getattr(resp, "usage", None)
    if usage is not None:
        logger.info(
            "openai_usage model=%s prompt_tokens=%s completion_tokens=%s total_tokens=%s",
            getattr(resp, "model", None),
            getattr(usage, "prompt_tokens", None),
            getattr(usage, "completion_tokens", None),
            getattr(usage, "total_tokens", None),
        )
    return resp.choices[0].message.content
