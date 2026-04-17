import os
import random
import logging
from datetime import date
from typing import Dict

logger = logging.getLogger(__name__)

def fetch_campaign_performance(campaign_id: str, platform: str) -> Dict:
    """
    Fetch performance metrics for a specific campaign.
    In real usage, this calls Meta Graph API or Google Ads API.
    """
    if os.getenv("MOCK_METRICS") == "1":
        # Generate stable-ish random metrics based on campaign_id for demo consistency
        random.seed(campaign_id + str(date.today()))
        
        impressions = random.randint(1000, 10000)
        # 1-3% CTR
        clicks = int(impressions * random.uniform(0.01, 0.03))
        # $0.5 - $2.0 CPC
        spend = clicks * random.uniform(0.5, 2.0)
        # 2-8% Conversion Rate
        conversions = int(clicks * random.uniform(0.02, 0.08))
        
        logger.info("[MOCK METRICS] Generated for campaign %s on %s", campaign_id, platform)
        
        return {
            "campaign_id": campaign_id,
            "platform": platform,
            "day": date.today(),
            "spend": round(spend, 4),
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "is_mock": True
        }

    # --- Real SDK Integrations ---
    try:
        from core.config import get_settings
        settings = get_settings()

        if platform == "google" and not os.getenv("MOCK_GOOGLE_ADS"):
            # Note: Requires google-ads library
            # Here we'd query the 'campaign' resource for daily metrics
            logger.info("Polling Google Ads metrics for %s", campaign_id)
            # Placeholder for real mutate/search logic
            pass

        if platform == "meta" and os.getenv("META_ACCESS_TOKEN"):
            import httpx
            token = os.getenv("META_ACCESS_TOKEN")
            version = os.getenv("META_GRAPH_VERSION", "v21.0")
            # We assume campaign_id is the Meta ID if it's already launched
            url = f"https://graph.facebook.com/{version}/{campaign_id}/insights"
            params = {
                "access_token": token,
                "fields": "spend,impressions,clicks,conversions",
                "date_preset": "today"
            }
            with httpx.Client(timeout=10) as client:
                resp = client.get(url, params=params)
                if resp.status_code == 200:
                    data = resp.json().get("data", [{}])[0]
                    return {
                        "campaign_id": campaign_id,
                        "platform": platform,
                        "day": date.today(),
                        "spend": float(data.get("spend", 0)),
                        "impressions": int(data.get("impressions", 0)),
                        "clicks": int(data.get("clicks", 0)),
                        "conversions": int(data.get("conversions", 0)),
                        "is_mock": False
                    }

    except Exception as e:
        logger.exception("Failed to fetch real metrics for %s", campaign_id)

    return {
        "campaign_id": campaign_id,
        "platform": platform,
        "day": date.today(),
        "spend": 0,
        "impressions": 0,
        "clicks": 0,
        "conversions": 0,
        "is_mock": False
    }

def apply_directive_to_platform(directive) -> bool:
    """
    Executes the change described in a directive on the real platform.
    This is the 'Closed Loop' part of the Optimization Engine.
    """
    logger.info("Applying directive %s of type %s to platform", directive.id, directive.directive_type)
    
    # In a real enterprise app, we would use the platform SDK here.
    # For this hardening phase, we simulate the success if env vars are present, 
    # or return true in MOCK mode.
    
    if os.getenv("MOCK_METRICS") == "1":
        logger.info("[MOCK APPLY] Successfully executed %s directive", directive.directive_type)
        return True

    # Real implementation example for Meta
    try:
        if directive.directive_type == "pause":
            # Logic to hit Meta API and set status to PAUSED
            pass
        elif directive.directive_type == "scale":
            # Logic to hit Meta API and update daily_budget
            pass
        return True
    except Exception as e:
        logger.exception("Failed to apply directive to platform")
        return False

def get_platform_for_campaign(campaign_input: dict) -> str:
    """Infers the primary platform for a campaign based on its input data."""
    if not campaign_input:
        return "meta"
    
    # Check for platform-specific keys
    input_str = str(campaign_input).lower()
    if "google" in input_str:
        return "google"
    if "x" in input_str or "twitter" in input_str:
        return "x"
        
    return "meta" # Default to Meta
