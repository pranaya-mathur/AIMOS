"""
Google Ads API Integration.

Real SDK implementation using the official `google-ads` client.
Requires:
- GOOGLE_ADS_DEVELOPER_TOKEN
- GOOGLE_ADS_CLIENT_ID
- GOOGLE_ADS_CLIENT_SECRET
- GOOGLE_ADS_REFRESH_TOKEN
- GOOGLE_ADS_CUSTOMER_ID
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class GoogleAdsError(RuntimeError):
    pass

def create_campaign(campaign_name: str, customer_id: Optional[str] = None) -> dict:
    """
    Creates a campaign skeleton on Google Ads.
    If MOCK_GOOGLE_ADS=1, generates a fake success response.
    """
    mock_enabled = os.getenv("MOCK_GOOGLE_ADS") == "1"
    
    if mock_enabled:
        logger.info("[MOCK GOOGLE ADS] Creating campaign: %s", campaign_name)
        return {
            "provider": "google_ads",
            "status": "mock_success",
            "campaign_id": "mock_555666777",
            "campaign_name": campaign_name,
            "mock": True
        }

    try:
        from google.ads.googleads.client import GoogleAdsClient
        from google.ads.googleads.errors import GoogleAdsException
        
        # 1. Load configuration
        credentials = {
            "developer_token": os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN"),
            "refresh_token": os.getenv("GOOGLE_ADS_REFRESH_TOKEN"),
            "client_id": os.getenv("GOOGLE_ADS_CLIENT_ID"),
            "client_secret": os.getenv("GOOGLE_ADS_CLIENT_SECRET"),
            "use_proto_plus": True
        }
        
        client = GoogleAdsClient.load_from_dict(credentials)
        cid = customer_id or os.getenv("GOOGLE_ADS_CUSTOMER_ID")
        
        if not cid:
            raise GoogleAdsError("GOOGLE_ADS_CUSTOMER_ID is not set")
            
        logger.info("Initializing Google Ads campaign for CID: %s", cid)
        
        # 2. Build Campaign Object
        campaign_service = client.get_service("CampaignService")
        campaign_operation = client.get_type("CampaignOperation")
        campaign = campaign_operation.create
        
        campaign.name = campaign_name
        campaign.advertising_channel_type = client.enums.AdvertisingChannelTypeEnum.SEARCH
        campaign.status = client.enums.CampaignStatusEnum.PAUSED
        
        # Set a manual CPC bid strategy
        campaign.manual_cpc.enhanced_cpc_enabled = True
        
        # 3. Execute
        response = campaign_service.mutate_campaigns(customer_id=cid, operations=[campaign_operation])
        resource_name = response.results[0].resource_name
        
        return {
            "provider": "google_ads",
            "status": "success",
            "resource_name": resource_name,
            "campaign_name": campaign_name
        }
        
    except ImportError:
        logger.error("google-ads library not installed")
        raise GoogleAdsError("google-ads library is missing. Run pip install google-ads")
    except GoogleAdsException as ex:
        logger.error("Google Ads API call failed: %s", ex)
        raise GoogleAdsError(f"Google Ads API Error: {ex.error.results[0].message}")
    except Exception as e:
        logger.exception("Google Ads connection failed")
        raise GoogleAdsError(str(e))
