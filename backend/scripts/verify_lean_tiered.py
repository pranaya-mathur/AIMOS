import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd()))

from services.orchestrator import supervisor_router, ORCHESTRATION_TRACKS
from core.config import TIER_AGENT_PERMISSIONS

def test_strategy_track_authorized():
    print("--- Testing Strategy Track (Authorized) ---")
    authorized = TIER_AGENT_PERMISSIONS["growth"]
    state = {
        "active_track": "strategy",
        "authorized_agents": authorized,
        "history": [],
        "agent_outputs": {},
        "loop_count": 0,
        "iteration_count": 0,
        "next_step": None,
    }
    
    # 1. Entry
    next_node = supervisor_router(state)
    print(f"Entry: {next_node}")
    assert next_node == "competitive_spy"
    
    # 2. After brand_builder
    state["history"] = ["competitive_spy", "business_analyzer", "brand_builder"]
    next_node = supervisor_router(state)
    print(f"After brand_builder: {next_node}")
    # In strategy track, brand_builder is followed by performance_brain
    assert next_node == "performance_brain"
    
    # 3. After performance_brain
    state["history"].append("performance_brain")
    next_node = supervisor_router(state)
    print(f"After performance_brain: {next_node}")
    assert next_node == "growth_planner"

    print("Strategy Track OK")

def test_free_tier_gating():
    print("\n--- Testing Free Tier Gating (Full Track) ---")
    authorized = TIER_AGENT_PERMISSIONS["free"]
    state = {
        "active_track": "full",
        "authorized_agents": authorized,
        "history": ["competitive_spy", "business_analyzer", "brand_builder"],
        "agent_outputs": {},
        "loop_count": 0,
        "iteration_count": 3,
        "next_step": None,
    }
    
    # In 'full' track, brand_builder is followed by 'content_studio'
    # BUT free tier is not authorized for 'content_studio'
    next_node = supervisor_router(state)
    print(f"After brand_builder (Free Tier): {next_node}")
    # It should skip content_studio, benchmarker, campaign, social, leads, sales, engagement, performance, growth
    # and land on business_dashboard
    assert next_node == "business_dashboard"
    
    print("Free Tier Gating OK")

if __name__ == "__main__":
    try:
        test_strategy_track_authorized()
        test_free_tier_gating()
        print("\nALL LEAN & TIERED VERIFICATIONS PASSED")
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
