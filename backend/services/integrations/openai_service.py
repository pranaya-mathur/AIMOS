
from openai import OpenAI

from core.config import get_settings


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
    return resp.choices[0].message.content
