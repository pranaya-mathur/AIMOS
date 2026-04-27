from services.agents.agent_runner import run_agent
from services.prompts.loader import get_agent_bundle

_bundle = get_agent_bundle("wisdom_extractor")

def run(state):
    """
    Extracts strategic insights from the completed orchestration state.
    """
    history = state.get("history", [])
    agent_outputs = state.get("agent_outputs", {})
    
    # Enrich the input with the full orchestration context
    enhanced_input = {
        **state.get("input", {}),
        "orchestration_history": history,
        "refinement_context": state.get("refinement_context"),
        "loop_count": state.get("loop_count", 0)
    }
    
    return run_agent(
        {**state, "input": enhanced_input},
        name=_bundle["agent_name"],
        output_key=_bundle["output_key"],
        schema=_bundle["schema"],
        prompt_template=_bundle["task_template"],
    )
