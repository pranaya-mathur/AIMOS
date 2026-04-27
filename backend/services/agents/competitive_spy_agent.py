import uuid
from db import SessionLocal
from models import CompetitorIntel, Brand
from services.agents.agent_runner import run_agent
from services.prompts.loader import get_agent_bundle
from services.integrations.search_service import SearchService


def run(state):
    _bundle = get_agent_bundle("competitive_spy")
    
    # 2.0 Feature: Dynamic External Search
    brand_profile = state.get("seller_profile") or {}
    brand_name = brand_profile.get("identities", {}).get("name")
    industry = brand_profile.get("strategy", {}).get("industry")
    
    query = f"top competitors for {brand_name} in {industry} industry" if brand_name else f"top marketing competitors in {industry}"
    search_results = SearchService.search(query)
    
    # Enrich input with search data
    enhanced_input = {
        **state.get("input", {}),
        "external_search_context": search_results
    }
    
    result_state = run_agent(
        {**state, "input": enhanced_input},
        name=_bundle["agent_name"],
        output_key=_bundle["output_key"],
        schema=_bundle["schema"],
        prompt_template=_bundle["task_template"],
    )
    
    # Hardened 2.0: Persist intelligence snapshots back to DB
    intel = result_state.get(_bundle["output_key"], {})
    competitors = intel.get("competitors", [])
    
    if competitors:
        db = SessionLocal()
        try:
            # Get organization_id if possible
            brand_id = None
            org_id = None
            if brand_name:
                brand = db.query(Brand).filter(Brand.name == brand_name).first()
                if brand:
                    brand_id = brand.id
                    org_id = brand.organization_id
            
            for comp in competitors:
                # Basic dedupe: if same name and brand_id, skip
                exists = db.query(CompetitorIntel).filter(
                    CompetitorIntel.competitor_name == comp["name"],
                    CompetitorIntel.brand_id == brand_id
                ).first()
                
                if not exists and org_id:
                    new_comp = CompetitorIntel(
                        id=str(uuid.uuid4()),
                        organization_id=org_id,
                        brand_id=brand_id,
                        competitor_name=comp.get("name"),
                        competitor_url=comp.get("url"),
                        positioning=comp.get("positioning"),
                        pricing_range=comp.get("pricing_range"),
                        category=industry
                    )
                    db.add(new_comp)
            db.commit()
        except Exception:
            # Don't fail the graph if persistence fails
            pass
        finally:
            db.close()

    return result_state
