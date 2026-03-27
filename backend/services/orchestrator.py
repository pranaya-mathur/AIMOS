
from langgraph.graph import StateGraph
from services.agents import (
    analytics_engine_agent,
    brand_builder_agent,
    business_analyzer_agent,
    business_dashboard_agent,
    campaign_builder_agent,
    content_studio_agent,
    customer_engagement_agent,
    growth_planner_agent,
    lead_capture_agent,
    optimization_engine_agent,
    sales_agent_agent,
    social_media_manager_agent,
)

# BRD v2 order: strategy → brand → content → paid → social → leads → sales → engagement → analytics → optimization → growth → dashboard
AGENT_ORDER = [
    ("business_analyzer", business_analyzer_agent.run),
    ("brand_builder", brand_builder_agent.run),
    ("content_studio", content_studio_agent.run),
    ("campaign_builder", campaign_builder_agent.run),
    ("social_media_manager", social_media_manager_agent.run),
    ("lead_capture", lead_capture_agent.run),
    ("sales_agent", sales_agent_agent.run),
    ("customer_engagement", customer_engagement_agent.run),
    ("analytics_engine", analytics_engine_agent.run),
    ("optimization_engine", optimization_engine_agent.run),
    ("growth_planner", growth_planner_agent.run),
    ("business_dashboard", business_dashboard_agent.run),
]

AGENT_RUNNERS = {name: runner for name, runner in AGENT_ORDER}


def build():
    g = StateGraph(dict)

    for agent_name, runner in AGENT_ORDER:
        g.add_node(agent_name, runner)

    g.set_entry_point(AGENT_ORDER[0][0])
    for idx in range(len(AGENT_ORDER) - 1):
        g.add_edge(AGENT_ORDER[idx][0], AGENT_ORDER[idx + 1][0])

    return g.compile()


def run_agents(data):
    return build().invoke({"input": data, "agent_outputs": {}})


def run_single_agent(agent_name: str, data: dict):
    if agent_name not in AGENT_RUNNERS:
        raise ValueError(f"Unknown agent '{agent_name}'")
    initial_state = {"input": data, "agent_outputs": {}}
    return AGENT_RUNNERS[agent_name](initial_state)
