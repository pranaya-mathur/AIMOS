# Prompts (modular)

Edit agent behavior **without changing Python**:

- `system/response_contract.md` — global JSON / formatting rules for all agents.
- `agents/<agent_id>/config.json` — `agent_name`, `output_key`, and JSON `schema` (shape hints for the model).
- `agents/<agent_id>/task.md` — **BRD-style playbook** (role, responsibilities, quality bar). At the **end** only, use placeholders `{input}` and `{context}` (filled by `agent_runner` as **indented JSON** via `json.dumps(..., indent=2)`); do not add other `{…}` braces in the file or `.format()` will break.

`agent_id` matches the folder name. BRD v2 folders: `business_analyzer`, `brand_builder`, `content_studio`, `campaign_builder`, `social_media_manager`, `lead_capture`, `sales_agent`, `customer_engagement`, `analytics_engine`, `optimization_engine`, `growth_planner`, `business_dashboard`.

At runtime, `PROMPTS_DIR` points here (see `Dockerfile`; locally the loader resolves the repo `prompts/` folder).
