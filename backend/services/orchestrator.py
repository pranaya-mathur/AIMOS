from typing import Optional
from langgraph.graph import StateGraph
from sqlalchemy.orm import Session
from db import SessionLocal
from services.usage.quotas import assert_can_consume_tokens
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


def enforce_quota_wrapper(runner, user_id: str):
    """
    Middleware-like wrapper to check token quota before each agent execution.
    Fails the campaign in real-time if the cap is already reached.
    """
    def wrapped(state: dict):
        if not user_id:
            return runner(state)
        
        db = SessionLocal()
        try:
            assert_can_consume_tokens(db, user_id)
        finally:
            db.close()
        return runner(state)
    return wrapped


def build(user_id: Optional[str] = None):
    g = StateGraph(dict)

    for agent_name, runner in AGENT_ORDER:
        # Wrap runner with real-time quota validator
        node_func = enforce_quota_wrapper(runner, user_id) if user_id else runner
        g.add_node(agent_name, node_func)

    g.set_entry_point(AGENT_ORDER[0][0])
    for idx in range(len(AGENT_ORDER) - 1):
        g.add_edge(AGENT_ORDER[idx][0], AGENT_ORDER[idx + 1][0])

    return g.compile()


def run_agents(data, user_id: Optional[str] = None):
    initial_input = dict(data)
    
    # Inject Brand Context if user_id is provided (AIM-014 to AIM-021)
    if user_id:
        db = SessionLocal()
        try:
            from models import Brand
            brand = db.query(Brand).filter(Brand.user_id == user_id).first()
            if brand:
                # Add a 'brand' key to the input so agents can use it
                initial_input["brand_profile"] = {
                    "name": brand.name,
                    "category": brand.category,
                    "description": brand.description,
                    "target_audience": brand.target_audience,
                    "marketing_goal": brand.marketing_goal,
                    "monthly_budget": float(brand.monthly_budget) if brand.monthly_budget else None,
                    "business_type": brand.business_type,
                    "industry": brand.industry,
                    "product_details": brand.product_details,
                    "pricing_range": brand.pricing_range
                }
        finally:
            db.close()

    return build(user_id).invoke({"input": initial_input, "agent_outputs": {}})


def run_single_agent(agent_name: str, data: dict):
    if agent_name not in AGENT_RUNNERS:
        raise ValueError(f"Unknown agent '{agent_name}'")
    initial_state = {"input": data, "agent_outputs": {}}
    return AGENT_RUNNERS[agent_name](initial_state)
