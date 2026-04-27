import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd()))

from services.governance.guards import scrub_pii
from services.orchestrator import supervisor_router, AgentState
from services.integrations.search_service import SearchService

def test_pii_scrubber():
    print("--- Testing PII Scrubber ---")
    data = {
        "text": "Contact me at pranaya@example.com or 123-456-7890.",
        "secret": "sk_test_51MzXk0SBy0Xz8XzXzXzXzX",
        "nested": {
            "email": "test@test.com"
        }
    }
    scrubbed = scrub_pii(data)
    print(f"Original: {data}")
    print(f"Scrubbed: {scrubbed}")
    assert "<EMAIL_MASKED>" in scrubbed["text"]
    assert "<PHONE_MASKED>" in scrubbed["text"]
    assert "<SECRET_KEY_MASKED>" in scrubbed["secret"]
    assert "<EMAIL_MASKED>" in scrubbed["nested"]["email"]
    print("PII Scrubber OK")

def test_search_fallback():
    print("\n--- Testing Search Fallback ---")
    results = SearchService.search("competitors for AI")
    print(f"Search results count: {len(results)}")
    assert len(results) > 0
    print("Search Service Fallback OK")

def test_reject_loop():
    print("\n--- Testing Reject Loop ---")
    # Mock state where benchmarker just finished with low score
    state = {
        "history": ["business_analyzer", "brand_builder", "content_studio", "predictive_benchmarker"],
        "agent_outputs": {
            "predictive_benchmarker": {
                "confidence_score": 45,
                "red_flags": ["Tone is off", "Budget misaligned"],
                "improvement_tips": ["Add more emojis", "Reduce target CPV"]
            }
        },
        "loop_count": 0,
        "iteration_count": 4,
        "orchestration_config": {"max_loops": 2, "max_iterations": 10},
        "next_step": None,
        "refinement_context": None
    }
    
    next_node = supervisor_router(state)
    print(f"Low score (<60) router result: {next_node}")
    assert next_node == "business_analyzer"
    assert state["loop_count"] == 1
    assert "REJECTED" in state["refinement_context"]
    
    # Test second loop
    state["history"].append("predictive_benchmarker")
    next_node = supervisor_router(state)
    print(f"Second low score result: {next_node}")
    assert next_node == "business_analyzer"
    assert state["loop_count"] == 2
    
    # Test loop limit
    state["history"].append("predictive_benchmarker")
    # If we already hit max_loops (2), it should proceed linearly (default next)
    # The supervisor router doesn't have a explicit "default next" for linear flow yet because we use conditional edges
    # But for this test, let's see what it does.
    next_node = supervisor_router(state)
    print(f"After max loops result: {next_node}")
    assert next_node != "business_analyzer" 
    
    print("Reject Loop Logic OK")

if __name__ == "__main__":
    try:
        test_pii_scrubber()
        test_search_fallback()
        test_reject_loop()
        print("\nALL VERIFICATIONS PASSED")
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {e}")
        sys.exit(1)
