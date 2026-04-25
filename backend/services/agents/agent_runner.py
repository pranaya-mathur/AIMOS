import json
import os

from services.integrations.openai_service import generate_text
from services.prompts.loader import get_system_response_contract


def _pretty_json_block(value) -> str:
    """Serialize prompt payload for task templates (indent=2, UTF-8, non-JSON values via str)."""
    if value is None:
        return "null"
    try:
        return json.dumps(value, indent=2, ensure_ascii=False, default=str)
    except TypeError:
        return json.dumps(str(value), indent=2, ensure_ascii=False)


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


from services.governance.guards import scrub_pii


def run_agent(state: dict, *, name: str, output_key: str, schema: dict, prompt_template: str, context_filter: list[str] = None):
    # 2.0 Governance: Scrub input for PII before it hits the LLM
    input_payload = scrub_pii(state.get("input", {}))
    
    # 2.0 Context Pruning: Only pass authorized agent outputs to save tokens
    full_history = state.get("agent_outputs", {})
    if context_filter:
        context = {k: v for k, v in full_history.items() if k in context_filter}
    else:
        context = full_history
        
    context = scrub_pii(context)

    prompt = prompt_template.format(
        input=_pretty_json_block(input_payload),
        context=_pretty_json_block(context),
    )
    schema_hint = json.dumps(schema, indent=2)
    contract = get_system_response_contract()
    # Vertical Specialization
    vertical = input_payload.get("industry_vertical")
    vertical_prompt = ""
    if vertical:
        v_path = os.path.join(os.getcwd(), "prompts", "verticals", f"{vertical.lower()}.md")
        if os.path.exists(v_path):
            try:
                with open(v_path, "r", encoding="utf-8") as f:
                    vertical_prompt = f"\n\n### Industry Vertical Expertise ({vertical}):\n{f.read()}"
            except Exception:
                pass

    full_prompt = (
        f"You are the {name} agent for an enterprise marketing system.\n"
        f"{contract}\n\n"
        f"Required JSON schema shape:\n{schema_hint}\n\n"
        f"Task:\n{prompt}"
        f"{vertical_prompt}"
    )

    raw = generate_text(full_prompt)
    parsed = _extract_json_block(raw)

    if parsed is None:
        parsed = {"raw_text": raw}

    # 2.0 Governance: Scrub output for PII before persisting
    parsed = scrub_pii(parsed)

    state.setdefault("agent_outputs", {})
    state["agent_outputs"][name] = parsed
    state[output_key] = parsed
    state["last_agent"] = name
    return state
