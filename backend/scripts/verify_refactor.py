import sys
import os
from unittest.mock import MagicMock, patch

# Add backend to sys.path
sys.path.append(os.path.join(os.getcwd()))

from services.orchestrator import supervisor_router, AGENT_ORDER
from services.agents.registry import AgentRegistry

def test_registry_resolution():
    print("--- Testing Registry Resolution ---")
    for name, _ in [("business_analyzer", "dynamic"), ("competitive_spy", "specialized")]:
        runner = AgentRegistry.get_runner(name)
        print(f"Runner for {name}: {runner}")
        assert runner is not None
    print("Registry Resolution OK")

def test_context_pruning_logic():
    print("\n--- Testing Context Pruning Logic ---")
    from services.agents.agent_runner import run_agent
    
    state = {
        "input": {"topic": "AI"},
        "agent_outputs": {
            "business_analyzer": {"strategic_fit": "High"},
            "brand_builder": {"voice": "Bold"},
            "secret_agent": {"p": "don't pass this"}
        }
    }
    
    # Mocking generate_text to capture the prompt
    with patch("services.agents.agent_runner.generate_text") as mock_gen:
        mock_gen.return_value = '{"test": "ok"}'
        
        # Test pruning: only pass brand_builder
        run_agent(
            state,
            name="test_agent",
            output_key="test_out",
            schema={},
            prompt_template="Input: {input} Context: {context}",
            context_filter=["brand_builder"]
        )
        
        full_prompt = mock_gen.call_args[0][0]
        print(f"Prompt with pruning: ... {full_prompt[full_prompt.find('Context:'):]} ...")
        
        assert "Bold" in full_prompt
        assert "strategic_fit" not in full_prompt
        assert "secret_agent" not in full_prompt
        
    print("Context Pruning OK")

if __name__ == "__main__":
    try:
        test_registry_resolution()
        test_context_pruning_logic()
        print("\nALL REFACTOR VERIFICATIONS PASSED")
    except Exception as e:
        print(f"\nVERIFICATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
