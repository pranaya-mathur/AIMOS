from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from deps import get_agency_user
from models import User
from services.orchestrator import AGENT_RUNNERS, run_single_agent
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
    del user  # auth enforced by dependency (None when AUTH_DISABLED)
    try:
        return run_single_agent(agent_name, payload.input)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
