from typing import Optional, TypedDict, Annotated, List
import operator
from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session
from db import SessionLocal
from services.usage.quotas import assert_can_consume_tokens
from services.agents.registry import AgentRegistry

# BRD v2 Lean: spy → analyzer → brand → content → benchmarker → campaign → social → leads → sales → engagement → performance → growth → dashboard
AGENT_ORDER = [
    ("competitive_spy", AgentRegistry.get_runner("competitive_spy")),
    ("business_analyzer", AgentRegistry.get_runner("business_analyzer")),
    ("brand_builder", AgentRegistry.get_runner("brand_builder")),
    ("content_studio", AgentRegistry.get_runner("content_studio")),
    ("predictive_benchmarker", AgentRegistry.get_runner("predictive_benchmarker")),
    ("campaign_builder", AgentRegistry.get_runner("campaign_builder")),
    ("social_media_manager", AgentRegistry.get_runner("social_media_manager")),
    ("lead_capture", AgentRegistry.get_runner("lead_capture")),
    ("sales_agent", AgentRegistry.get_runner("sales_agent")),
    ("customer_engagement", AgentRegistry.get_runner("customer_engagement")),
    ("performance_brain", AgentRegistry.get_runner("performance_brain")),
    ("growth_planner", AgentRegistry.get_runner("growth_planner")),
    ("business_dashboard", AgentRegistry.get_runner("business_dashboard")),
    ("wisdom_extractor", AgentRegistry.get_runner("wisdom_extractor")),
]

ORCHESTRATION_TRACKS = {
    "full": [a[0] for a in AGENT_ORDER],
    "strategy": ["competitive_spy", "business_analyzer", "brand_builder", "performance_brain", "growth_planner", "business_dashboard"],
    "creative": ["brand_builder", "content_studio", "predictive_benchmarker", "campaign_builder", "business_dashboard"],
    "launch": ["campaign_builder", "social_media_manager", "lead_capture", "sales_agent", "business_dashboard"]
}

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
    loop_count: int
    authorized_agents: List[str]
    active_track: str



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
    
    # 2.0 Predictive Guardrail: If benchmarker finds critical quality issues, force refinement or pause
    forecast = (state.get("agent_outputs") or {}).get("predictive_benchmarker")
    if forecast and isinstance(forecast, dict) and state.get("history", [])[-1] == "predictive_benchmarker":
        score = forecast.get("confidence_score", 100)
        
        # Scenario A: REJECT & LOOP BACK (The "9/10 Architecture" Power move)
        # If score is suboptimal (< 60) and we haven't looped too much, force Business Analyzer to retry
        if score < 60 and state.get("loop_count", 0) < config.get("max_loops", 2):
            state["loop_count"] = state.get("loop_count", 0) + 1
            state["refinement_context"] = (
                f"REJECTED by Benchmarker (Score: {score}%). "
                f"Issues: {', '.join(forecast.get('red_flags', []))}. "
                f"Tips: {', '.join(forecast.get('improvement_tips', []))}"
            )
            return "business_analyzer"

        # Scenario B: CRITICAL FAILURE & PAUSE
        # If score < 40, we force a manual review before proceeding to campaign_builder
        if score < 40:
            state["status_signal"] = "PAUSE"
            state["refinement_context"] = f"CRITICAL: Performance Confidence too low ({score}%). Analyst Notes: {forecast.get('performance_outlook')}"
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

    # Default Flow Logic: Track + Authorization Checks
    track_name = state.get("active_track", "full")
    track_agents = ORCHESTRATION_TRACKS.get(track_name, ORCHESTRATION_TRACKS["full"])
    authorized = state.get("authorized_agents", [])
    
    history = state.get("history", [])
    last_agent = history[-1] if history else None
    
    # 1. Resolve starting point
    if not last_agent:
        # Skip unauthorized at entry
        for agent in track_agents:
            if agent in authorized:
                return agent
        return "business_dashboard"

    # 2. Find next agent in the specific track
    try:
        current_idx = track_agents.index(last_agent)
        remaining = track_agents[current_idx + 1:]
        
        for next_candidate in remaining:
            # Skip if not authorized by tier
            if next_candidate in authorized:
                return next_candidate
            
    except ValueError:
        # If last_agent is not in this track, fallback to dashboard
        pass

    if last_agent == "wisdom_extractor" or last_agent == "business_dashboard":
        return END

    return "business_dashboard"


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
                    "loop_count": s.get("loop_count", 0),
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
                from models import Brand, User
                from core.config import TIER_AGENT_PERMISSIONS
                subscription_tier = user_row.subscription_tier if user_row else "free"
                authorized_agents = TIER_AGENT_PERMISSIONS.get(subscription_tier, TIER_AGENT_PERMISSIONS["free"])

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
        "loop_count": 0,
        "authorized_agents": authorized_agents if 'authorized_agents' in locals() else TIER_AGENT_PERMISSIONS["free"],
        "active_track": initial_input.get("track", "full"),
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
