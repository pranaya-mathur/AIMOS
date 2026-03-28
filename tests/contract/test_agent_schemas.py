import pytest
import os
import json
from pathlib import Path

# Agents as defined in the BRD
AGENT_NAMES = [
    "business_analyzer", "brand_builder", "content_studio", "campaign_builder",
    "social_media_manager", "lead_capture", "sales_agent", "customer_engagement",
    "analytics_engine", "optimization_engine", "growth_planner", "business_dashboard"
]

@pytest.mark.parametrize("agent_name", AGENT_NAMES)
def test_agent_config_contract(agent_name):
    """
    Ensures that every enterprise agent has a valid config.json 
    with a properly defined output schema.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    config_path = project_root / "prompts" / "agents" / agent_name / "config.json"
    
    assert config_path.exists(), f"Missing config.json for {agent_name}"
    
    with open(config_path, "r") as f:
        data = json.load(f)
        
    assert "agent_name" in data, f"Missing agent_name field in {agent_name} config"
    assert "schema" in data, f"Missing schema contract for {agent_name}"
    assert isinstance(data["schema"], dict), f"schema must be a JSON object for {agent_name}"
    
    # Contract: Every agent must at least specify its own name or identifier in the config
    assert data["agent_name"] == agent_name

@pytest.mark.parametrize("agent_name", AGENT_NAMES)
def test_agent_task_description_exists(agent_name):
    """
    Ensures that every agent has a task.md file defining its logic.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    task_path = project_root / "prompts" / "agents" / agent_name / "task.md"
    
    assert task_path.exists(), f"Missing task.md for {agent_name}"
    assert task_path.stat().st_size > 0, f"Empty task description for {agent_name}"

def test_system_response_contract_exists():
    """
    Ensures the global JSON response contract for all agents is present.
    """
    project_root = Path(__file__).resolve().parent.parent.parent
    contract_path = project_root / "prompts" / "system" / "response_contract.md"
    
    assert contract_path.exists()
    assert "JSON" in contract_path.read_text()
