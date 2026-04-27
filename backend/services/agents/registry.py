import logging
from typing import Dict, List, Optional, Callable
from services.agents.agent_runner import run_agent
from services.prompts.loader import get_agent_bundle

logger = logging.getLogger(__name__)

# Hardened 2.0 Context Mapping: Defines what each agent needs to "see"
# This prevents token bloat by pruning the context window.
AGENT_DEPENDENCIES: Dict[str, List[str]] = {
    "business_analyzer": [],
    "brand_builder": ["business_analyzer"],
    "content_studio": ["brand_builder", "business_analyzer", "competitive_spy"],
    "predictive_benchmarker": ["content_studio", "brand_builder", "business_analyzer"],
    "campaign_builder": ["predictive_benchmarker", "content_studio", "brand_builder"],
    "social_media_manager": ["campaign_builder", "brand_builder"],
    "lead_capture": ["campaign_builder", "brand_builder"],
    "sales_agent": ["lead_capture", "brand_builder"],
    "customer_engagement": ["sales_agent", "lead_capture"],
    "performance_brain": ["business_analyzer", "brand_builder", "content_studio", "campaign_builder"],
    "growth_planner": ["performance_brain", "business_analyzer", "brand_builder"],
    "wisdom_extractor": ["performance_brain", "growth_planner", "business_analyzer", "brand_builder", "content_studio", "campaign_builder"],
    "competitive_spy": [] # Specialized logic
}

class AgentRegistry:
    """
    Centralized Factory for Agent Runners.
    Consolidates 10+ boilerplate files into a dynamic execution service.
    """
    
    _specialized_runners: Dict[str, Callable] = {}

    @classmethod
    def register_specialized(cls, name: str, runner: Callable):
        cls._specialized_runners[name] = runner

    @classmethod
    def get_runner(cls, name: str) -> Callable:
        # Check if we have a specialized implementation (e.g. Competitive Spy with Persistence)
        if name in cls._specialized_runners:
            return cls._specialized_runners[name]
        
        # Standard Boilerplate Runner
        def dynamic_runner(state: dict):
            _bundle = get_agent_bundle(name)
            dependencies = AGENT_DEPENDENCIES.get(name)
            
            return run_agent(
                state,
                name=_bundle["agent_name"],
                output_key=_bundle["output_key"],
                schema=_bundle["schema"],
                prompt_template=_bundle["task_template"],
                context_filter=dependencies # Selective Pruning
            )
        
        return dynamic_runner

# Initialize the registry with specialized logic
# We import them here to avoid circular dependencies in some setups,
# or simply keep them as local specialized runners.
def _init_registry():
    from services.agents.competitive_spy_agent import run as run_spy
    from services.agents.wisdom_extractor_agent import run as run_wisdom
    
    AgentRegistry.register_specialized("competitive_spy", run_spy)
    AgentRegistry.register_specialized("wisdom_extractor", run_wisdom)

_init_registry()
