from typing import Optional, TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
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
    predictive_benchmarker_agent,
    sales_agent_agent,
    social_media_manager_agent,
    competitive_spy_agent,
    wisdom_extractor_agent,
)

# BRD v2 order: spy → strategy → brand → content → paid → social → leads → sales → engagement → analytics → optimization → growth → dashboard
AGENT_ORDER = [
    ("competitive_spy", competitive_spy_agent.run),
    ("business_analyzer", business_analyzer_agent.run),
    ("brand_builder", brand_builder_agent.run),
    ("content_studio", content_studio_agent.run),
    ("predictive_benchmarker", predictive_benchmarker_agent.run),
    ("campaign_builder", campaign_builder_agent.run),
    ("social_media_manager", social_media_manager_agent.run),
    ("lead_capture", lead_capture_agent.run),
    ("sales_agent", sales_agent_agent.run),
    ("customer_engagement", customer_engagement_agent.run),
    ("analytics_engine", analytics_engine_agent.run),
    ("optimization_engine", optimization_engine_agent.run),
    ("growth_planner", growth_planner_agent.run),
    ("business_dashboard", business_dashboard_agent.run),
    ("wisdom_extractor", wisdom_extractor_agent.run),
]

AGENT_RUNNERS = {name: runner for name, runner in AGENT_ORDER}


class AgentState(TypedDict):
    input: dict
    agent_outputs: Annotated[dict, operator.ior]
    # Hardened 2.0 Orchestration Fields
    iteration_count: int
    next_step: Optional[str]
    refinement_context: Optional[str]
    history: List[str]
    # Configuration
    orchestration_config: dict # { "max_iterations": 3, "manual_intervention": True }
    status_signal: Optional[str] # None | "PAUSE"
    # Phase 2 Context
    seller_profile: Optional[dict]
    competitor_intel: Optional[List[dict]]
    historical_wisdom: Optional[List[dict]]
    product_catalog: Optional[List[dict]]


def supervisor_router(state: AgentState):
    """
    Hardened 2.0 Smart Router.
    Decides if we should transition to the next agent, loop back, or end.
    """
    config = state.get("orchestration_config", {"max_iterations": 3, "manual_intervention": True})
    
    if state.get("iteration_count", 0) >= config["max_iterations"]:
        if state.get("history", []) and state.get("history")[-1] == "business_dashboard":
            return END
        return "business_dashboard"  # Safety governor: exit 

    next_agent = state.get("next_step")
    
    # 2.0 Predictive Guardrail: If benchmarker finds critical quality issues, pause immediately
    forecast = (state.get("agent_outputs") or {}).get("predictive_benchmarker")
    if forecast and isinstance(forecast, dict):
        score = forecast.get("confidence_score", 100)
        # If score < 40, we force a manual review before proceeding to campaign_builder
        if score < 40 and state.get("last_agent") == "predictive_benchmarker":
            state["status_signal"] = "PAUSE"
            state["refinement_context"] = f"CRITICAL: Low Performance Confidence ({score}%). Analyst Notes: {forecast.get('performance_outlook')}"
            return END

    if next_agent and next_agent in AGENT_RUNNERS:
        # Hardened 2.0 Autopilot Gate (Option B)
        # Check if the optimization was low risk enough to bypass manual approval
        is_autopilot_eligible = False
        if config.get("autopilot_enabled") and last_agent == "optimization_engine":
             rules = (state.get("agent_outputs") or {}).get("optimization_engine") or {}
             directives = rules.get("directives", [])
             if directives:
                 # Logic: If ALL directives are low risk and high confidence
                 risk_ok = all(d.get("risk_score", 100) < 20 for d in directives)
                 conf_ok = all(d.get("confidence", 0) > 90 for d in directives)
                 
                 # Hardened 2.0 Phase 1.4: Financial Hard Cap
                 max_amount = config.get("autopilot_max_shift_amount", 100.0)
                 amount_ok = all(d.get("amount_value", 1000000.0) < max_amount for d in directives)
                 
                 if risk_ok and conf_ok and amount_ok:
                     is_autopilot_eligible = True

        if is_autopilot_eligible:
             # Progress autonomously
             state["status_signal"] = "AUTOPILOT_APPLY"
             return next_agent

        # Check for Manual Intervention before looping back
        if config.get("manual_intervention"):
             # Flag the state for a pause and exit the current execution
             state["status_signal"] = "PAUSE"
             return END
        return next_agent

    # Default linear progression if no specific next_step is set
    history = state.get("history", [])
    last_agent = history[-1] if history else None
    
    if not last_agent:
        return AGENT_ORDER[0][0]

    for idx, (name, _) in enumerate(AGENT_ORDER):
        if name == last_agent:
            if idx + 1 < len(AGENT_ORDER):
                return AGENT_ORDER[idx + 1][0]
            break

    if last_agent == "wisdom_extractor":
        return END

    return "wisdom_extractor"


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
    g = StateGraph(AgentState)

    for agent_name, runner in AGENT_ORDER:
        # Wrap runner with real-time quota validator
        node_func = enforce_quota_wrapper(runner, user_id) if user_id else runner

        # 2.0 Logic: Update history and iterations
        def make_node(name=agent_name, func=node_func):
            def node_func_with_metadata(s: AgentState):
                # We expect the agent to return a dict of updates
                result = func(s)
                return {
                    **result,
                    "iteration_count": s.get("iteration_count", 0) + 1,
                    "history": s.get("history", []) + [name]
                }
            return node_func_with_metadata

        g.add_node(agent_name, make_node())

    g.set_entry_point(AGENT_ORDER[0][0])

    # Replace linear edges with conditional supervisor routing
    for agent_name, _ in AGENT_ORDER:
        g.add_conditional_edges(
            agent_name,
            supervisor_router,
            {name: name for name, _ in AGENT_ORDER} | {"business_dashboard": "business_dashboard", END: END}
        )

    return g.compile()


def run_agents(data, user_id: Optional[str] = None):
    initial_input = dict(data)
    
    orchestration_config = {"max_iterations": 3, "manual_intervention": True}
    
    # Inject Brand Context if user_id is provided (AIM-014 to AIM-021)
    if user_id:
        db = SessionLocal()
        try:
            from models import Brand, Organization, User
            brand = db.query(Brand).filter(Brand.user_id == user_id).first()
            user_row = db.query(User).filter(User.id == user_id).first()
            if user_row and user_row.organization_id:
                org = db.query(Organization).filter(Organization.id == user_row.organization_id).first()
                if org:
                    orchestration_config = {
                        "max_iterations": org.max_orchestration_iterations or 30,
                        "manual_intervention": org.manual_intervention_enabled
                    }

            if brand:
                # Add a 'brand_profile' key to the input so agents can use it (AIM-014 to AIM-021)
                initial_input["brand_profile"] = {
                    "identities": {
                        "name": brand.name,
                        "category": brand.category,
                        "description": brand.description,
                    },
                    "strategy": {
                        "target_audience": brand.target_audience,
                        "primary_goal": brand.primary_goal,
                        "monthly_budget": float(brand.monthly_budget) if brand.monthly_budget else None,
                        "pricing_range": brand.pricing_range,
                        "business_type": brand.business_type,
                        "industry": brand.industry,
                    },
                    "assets": {
                        "logo_url": brand.logo_url,
                        "website_url": brand.website_url,
                        "social_links": brand.social_links,
                    },
                    "ai_brand_kit": brand.ai_generated_kit, # High-fidelity Narrative, Voice, Colors
                    "analysis_report": brand.analysis_report,
                    "product_details": brand.product_details,
                }
            if brand:
                from models import CompetitorIntel
                competitors = db.query(CompetitorIntel).filter(CompetitorIntel.brand_id == brand.id).all()
                competitor_data = [
                    {"name": c.competitor_name, "url": c.competitor_url, "positioning": c.positioning} 
                    for c in competitors
                ]
            if brand:
                from models import BrandWisdom
                wisdom_logs = db.query(BrandWisdom).filter(BrandWisdom.brand_id == brand.id).order_by(BrandWisdom.created_at.desc()).limit(5).all()
                wisdom_data = [
                    {"type": w.insight_type, "insight": w.content, "impact": w.impact_score}
                    for w in wisdom_logs
                ]
            if brand:
                from models import Product
                active_products = db.query(Product).filter(
                    Product.brand_id == brand.id,
                    Product.is_sync_enabled == True
                ).limit(20).all()
                product_data = [
                    {"id": p.external_id, "title": p.title, "price": str(p.price), "stock": p.inventory_quantity}
                    for p in active_products
                ]
        finally:
            db.close()

    return build(user_id).invoke({
        "input": initial_input,
        "agent_outputs": {},
        "iteration_count": 0,
        "history": [],
        "next_step": None,
        "refinement_context": None,
        "orchestration_config": orchestration_config,
        "status_signal": None,
        "seller_profile": initial_input.get("brand_profile"),
        "competitor_intel": competitor_data if 'competitor_data' in locals() else [],
        "historical_wisdom": wisdom_data if 'wisdom_data' in locals() else [],
        "product_catalog": product_data if 'product_data' in locals() else []
    })


def run_single_agent(agent_name: str, data: dict):
    if agent_name not in AGENT_RUNNERS:
        raise ValueError(f"Unknown agent '{agent_name}'")
    
    runner = AGENT_RUNNERS[agent_name]
    initial_state = {"input": data, "agent_outputs": {}}
    
    # 2.0 Hardened: Logic reflects full agent execution including schema enforcement
    result_state = runner(initial_state)
    return result_state.get(agent_name) or result_state.get("agent_outputs", {}).get(agent_name)
def resume_agents(saved_state: dict, user_id: Optional[str] = None):
    """
    Hardened 2.0 Resumption entry point.
    Continues execution of the graph using the provided state.
    """
    # LangGraph invoke will pick up from the 'next_step' node if we provide it.
    # However, for a simpler resume, we just re-invoke the compiled graph with the hydrated state.
    # The supervisor_router will automatically route to 'next_step' because it's priority #1.
    return build(user_id).invoke(saved_state)
