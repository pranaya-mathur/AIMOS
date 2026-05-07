import sys
from pathlib import Path
import json

# Add backend directory to python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from services.agents.agent_runner import run_agent
from services.prompts.loader import get_agent_bundle
from dotenv import load_dotenv

def test_performance_brain():
    # Load .env to ensure OpenAI API key is pulled in
    load_dotenv()
    
    # 1. Fetch the strict Advanced 2.0 Agent config we just wrote
    bundle = get_agent_bundle("performance_brain")

    # 2. Fake a terrible campaign output!
    mock_state = {
        "input": "Meta campaign 'Summer Sale 2026' has been running for 6 days.",
        "context": "Industry benchmark ROAS is 3x. Our internal TACoS target is strictly < 25%.",
        "agent_outputs": {
            "current_metrics": {
                "CPC": "₹198",
                "TACoS": "35%",
                "ROAS": "1.4x"
            }
        }
    }

    print("====================================")
    print("🧠 Triggering Performance Brain...")
    print("Testing against bad KPIs: CPC: 198 | TACoS: 35%")
    print("====================================\n")
    
    # 3. Excute the agent
    result = run_agent(
        state=mock_state,
        name=bundle["agent_name"],
        output_key=bundle["output_key"],
        schema=bundle["schema"],
        prompt_template=bundle["task_template"]
    )

    # 4. Print the hyperspecific output
    strategy = result.get("agent_outputs", {}).get("performance_strategy", {})
    print(json.dumps(strategy, indent=2))

if __name__ == "__main__":
    test_performance_brain()
