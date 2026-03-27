from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from deps import get_agency_user
from models import User
from services.orchestrator import AGENT_RUNNERS, run_single_agent
from services.usage.context import clear_usage_context, set_usage_context
from services.usage.exceptions import QuotaExceededError
from services.prompts.loader import list_prompt_bundle_ids

router = APIRouter()


class AgentRunRequest(BaseModel):
    input: dict = Field(default_factory=dict)


@router.get("")
def list_agents():
    return {
        "agents": list(AGENT_RUNNERS.keys()),
        "count": len(AGENT_RUNNERS),
        "prompt_bundles": list_prompt_bundle_ids(),
    }


@router.post("/{agent_name}/run")
def run_agent(
    agent_name: str,
    payload: AgentRunRequest,
    user: Optional[User] = Depends(get_agency_user),
):
    try:
        set_usage_context(user_id=user.id if user else None, campaign_id=None)
        return run_single_agent(agent_name, payload.input)
    except QuotaExceededError as exc:
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    finally:
        clear_usage_context()
