import pytest
from unittest.mock import patch, MagicMock
import json
import os

# Mocking the backend environment before imports if necessary
os.environ["AUTH_DISABLED"] = "1"

# We need to ensure the backend is in the path
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from services.agents.agent_runner import run_agent

@pytest.fixture
def mock_openai():
    with patch("services.agents.agent_runner.generate_text") as mock:
        yield mock

@pytest.fixture
def mock_contract():
    with patch("services.agents.agent_runner.get_system_response_contract") as mock:
        mock.return_value = "Always return valid JSON."
        yield mock

def test_run_agent_basic(mock_openai, mock_contract):
    """Verify that run_agent correctly calls OpenAI and parses JSON."""
    mock_openai.return_value = '{"analysis": "good"}'
    
    state = {"input": {"data": "test"}}
    result_state = run_agent(
        state,
        name="test_agent",
        output_key="test_out",
        schema={"type": "object", "properties": {"analysis": {"type": "string"}}},
        prompt_template="Analyze this: {input}"
    )
    
    assert result_state["agent_outputs"]["test_agent"] == {"analysis": "good"}
    assert result_state["test_out"] == {"analysis": "good"}
    mock_openai.assert_called_once()
    # Check if name is in the prompt
    args, _ = mock_openai.call_args
    assert "test_agent" in args[0]

def test_run_agent_with_vertical(mock_openai, mock_contract):
    """Verify that industry vertical instructions are injected."""
    mock_openai.return_value = '{"recommendation": "sell house"}'
    
    # We need to mock os.path.exists and open for the vertical file
    with patch("os.path.exists") as mock_exists, \
         patch("builtins.open", MagicMock(return_value=MagicMock(__enter__=lambda s: MagicMock(read=lambda: "Real Estate Special Rules")))):
        
        mock_exists.return_value = True
        
        state = {"input": {"industry_vertical": "Real_Estate"}}
        run_agent(
            state,
            name="advisor",
            output_key="adv_out",
            schema={},
            prompt_template="Advise me: {input}"
        )
        
        args, _ = mock_openai.call_args
        assert "Real Estate Special Rules" in args[0]
        assert "Industry Vertical Expertise" in args[0]

def test_run_agent_invalid_json_retry(mock_openai, mock_contract):
    """Verify that invalid JSON from AI is handled (currently it might raise or we might add retry)."""
    mock_openai.return_value = "Not JSON at all"
    
    state = {"input": {}}
    run_agent(
        state,
        name="error_agent",
        output_key="err_out",
        schema={},
        prompt_template="Broken: {input}"
    )
    # The current implementation returns {"raw_text": raw} if parsing fails
    assert state["agent_outputs"]["error_agent"] == {"raw_text": "Not JSON at all"}
