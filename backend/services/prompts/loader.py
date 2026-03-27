"""
Load agent prompts and schemas from the `prompts/` directory (editable without code changes).

Resolution order:
1. `PROMPTS_DIR` environment variable (set to `/app/prompts` in Docker)
2. Repo-level `prompts/` next to `backend/` (local development)
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def prompts_root() -> Path:
    env = os.getenv("PROMPTS_DIR")
    if env:
        root = Path(env).resolve()
        if root.is_dir():
            return root
        logger.warning("PROMPTS_DIR=%s is not a directory; falling back to dev path", env)
    here = Path(__file__).resolve().parent
    # here == backend/services/prompts → parents[2] == repo root (aimos_enterprise_real)
    dev = (here.parents[2] / "prompts").resolve()
    return dev


@lru_cache(maxsize=1)
def get_system_response_contract() -> str:
    path = prompts_root() / "system" / "response_contract.md"
    if not path.is_file():
        return (
            "Return only valid JSON. No markdown fences. No explanations outside the JSON object."
        )
    text = path.read_text(encoding="utf-8").strip()
    logger.debug("loaded system response contract from %s", path)
    return text


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=32)
def get_agent_bundle(agent_id: str) -> dict[str, Any]:
    """
    Load one agent's config + task template.

    agent_id: directory name under prompts/agents/ (e.g. "business", "paid_media").
    Returns keys: agent_name, output_key, schema, task_template
    """
    base = prompts_root() / "agents" / agent_id
    cfg_path = base / "config.json"
    task_path = base / "task.md"
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Missing agent config: {cfg_path}")
    if not task_path.is_file():
        raise FileNotFoundError(f"Missing agent task template: {task_path}")

    cfg = _load_json(cfg_path)
    required = ("agent_name", "output_key", "schema")
    for key in required:
        if key not in cfg:
            raise ValueError(f"Agent {agent_id}: config.json must include {key!r}")

    task_template = task_path.read_text(encoding="utf-8").strip()
    logger.debug("loaded agent bundle %s from %s", agent_id, base)

    return {
        "agent_name": cfg["agent_name"],
        "output_key": cfg["output_key"],
        "schema": cfg["schema"],
        "task_template": task_template,
    }


def list_prompt_bundle_ids() -> list[str]:
    """Directory names under prompts/agents/ that have config.json + task.md."""
    root = prompts_root() / "agents"
    if not root.is_dir():
        return []
    out: list[str] = []
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p / "config.json").is_file() and (p / "task.md").is_file():
            out.append(p.name)
    return out
