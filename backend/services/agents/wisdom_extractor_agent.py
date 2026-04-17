from services.agents.agent_runner import run_agent
from services.prompts.loader import get_agent_bundle

_bundle = get_agent_bundle("wisdom_extractor")

def run(state):
    """
    Extracts strategic insights from the completed orchestration state.
    """
    # 2.0 Feature: Pass Decision Logs (Aborts/Overrides) to the agent
    decision_logs = state.get("decision_logs", [])
    
    # Enrich the input with the final history
    enhanced_input = {
        **state.get("input", {}),
        "decision_logs": decision_logs,
        "history_path": state.get("history", [])
    }
    
    return run_agent(
        {**state, "input": enhanced_input},
        name=_bundle["agent_name"],
        output_key=_bundle["output_key"],
        schema=_bundle["schema"],
        prompt_template=_bundle["task_template"],
    )
