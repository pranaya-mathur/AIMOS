# Prompt Customization Guide

The AIMOS pipeline uses 12 specialized AI agents. Each agent's behavior is controlled by a directory in `prompts/agents/<agent_name>/`.

## 📂 Directory Structure
*   **`task.md`**: The system instructions (Persona, Responsibilities, Quality bar).
*   **`config.json`**: The output schema (JSON keys) and agent metadata.

---

## 🛠️ How to Customize

### 1. Changing Agent "Personality"
To change how an agent speaks or its strategic focus, edit the `task.md` file.

**Example: Making the `sales_agent` more "Aggressive/Direct"**
*   **Original**: "Help identify the best sales approach for the prospect."
*   **New**: "Adopt a high-urgency, results-first persona. Focus on direct ROI, objection handling, and immediate closing tactics (CTA)."

### 2. Adding Custom Metadata
To add a new data field to an agent's output, update the `schema` in `config.json`.

**Example: Adding `target_revenue_lift` to `business_analyzer`**
1. Open `prompts/agents/business_analyzer/config.json`.
2. Add `"target_revenue_lift": "string"` to the `schema` object.
3. Update `task.md` to include instructions: "8. **Revenue Lift**: Estimate the percentage increase in revenue this strategy could achieve."

---

## 💡 Best Practices

*   **Be Specific**: Instead of "Make it look creative," use "Focus on abstract metaphors and vibrant storytelling hooks."
*   **Input Context**: Always keep the `{input}` and `{context}` variables at the bottom of `task.md`.
*   **No Markdown in output**: Agents must return raw JSON only. Ensure the `config.json` schema reflects the keys precisely.
*   **Hot-Reload**: Thanks to the Docker volume mounts, you can edit these files and re-run your `POST` request immediately to see the change in output.
