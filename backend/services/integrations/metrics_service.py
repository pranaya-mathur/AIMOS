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

    # Real implementation would go here (Meta/Google SDK integration)
    # For now, returning zero metrics to avoid crashes if not configured
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
