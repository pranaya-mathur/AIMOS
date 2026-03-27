from services.agents.agent_runner import run_agent
from services.prompts.loader import get_agent_bundle

_bundle = get_agent_bundle("content_studio")


def run(state):
    return run_agent(
        state,
        name=_bundle["agent_name"],
        output_key=_bundle["output_key"],
        schema=_bundle["schema"],
        prompt_template=_bundle["task_template"],
    )
