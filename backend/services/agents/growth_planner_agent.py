from services.agents.agent_runner import run_agent
from services.prompts.loader import get_agent_bundle

_bundle = get_agent_bundle("growth_planner")

def run(state):
    """
    Analyzes campaign metrics and memory to generate the next cycle's growth strategy.
    """
    
    # Optionally enrich the state input
    enhanced_input = {
        **state.get("input", {}),
        "campaign_metrics": state.get("agent_outputs", {}).get("current_metrics", {}),
        "brand_wisdom": state.get("agent_outputs", {}).get("brand_wisdom", [])
    }
    
    return run_agent(
        {**state, "input": enhanced_input},
        name=_bundle["agent_name"],
        output_key=_bundle["output_key"],
        schema=_bundle["schema"],
        prompt_template=_bundle["task_template"],
    )
