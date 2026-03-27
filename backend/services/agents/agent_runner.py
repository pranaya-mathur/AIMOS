import json

from services.integrations.openai_service import generate_text
from services.prompts.loader import get_system_response_contract


def _extract_json_block(raw_text: str):
    if not raw_text:
        return None

    start = raw_text.find("{")
    end = raw_text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None

    candidate = raw_text[start : end + 1]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def run_agent(state: dict, *, name: str, output_key: str, schema: dict, prompt_template: str):
    input_payload = state.get("input", {})
    context = state.get("agent_outputs", {})

    prompt = prompt_template.format(input=input_payload, context=context)
    schema_hint = json.dumps(schema, indent=2)
    contract = get_system_response_contract()
    full_prompt = (
        f"You are the {name} agent for an enterprise marketing system.\n"
        f"{contract}\n\n"
        f"Required JSON schema shape:\n{schema_hint}\n\n"
        f"Task:\n{prompt}"
    )

    raw = generate_text(full_prompt)
    parsed = _extract_json_block(raw)

    if parsed is None:
        parsed = {"raw_text": raw}

    state.setdefault("agent_outputs", {})
    state["agent_outputs"][name] = parsed
    state[output_key] = parsed
    state["last_agent"] = name
    return state
