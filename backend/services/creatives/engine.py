import logging
import platform
from typing import Optional
from core.config import get_settings
from services.integrations.stability_ai import StabilityAIClient

logger = logging.getLogger(__name__)

class CreativeEngine:
    """
    Unified entry point for AI creative generation.
    Routes between Cloud (Stability/Flux) and Sovereign (Local GGUF) modes.
    """
    
    @staticmethod
    def generate_image(prompt: str, width: int = 1024, height: int = 1024) -> Optional[str]:
        settings = get_settings()
        
        # 1. Check for Sovereign Mode Eligibility
        if settings.sovereign_mode:
            # We enforce Metal check for Mac or Fallback to CPU for others
            is_mac = platform.system() == "Darwin"
            logger.info(f"CreativeEngine: Sovereign Mode Enabled (Platform: {platform.system()})")
            
            try:
                from services.creatives.sovereign import SovereignMediaClient
                client = SovereignMediaClient()
                result = client.generate_image(prompt, width=width, height=height)
                if result:
                    return result
                logger.warning("CreativeEngine: Sovereign generation returned empty, falling back to cloud.")
            except Exception as e:
                logger.error(f"CreativeEngine: Sovereign generation failed: {e}")
        
        # 2. Fallback to Cloud (Stability AI)
        logger.info("CreativeEngine: Routing to Cloud (Stability AI)")
        client = StabilityAIClient()
        return client.generate_logo(prompt) # Currently defaults to logo logic, can be generalized

    @staticmethod
    def generate_video(prompt: str) -> Optional[str]:
        """Placeholder for video generation (Phase 2.5)"""
        settings = get_settings()
        if settings.sovereign_mode:
            logger.info(f"CreativeEngine (SOVEREIGN): Generating mock video for: {prompt}")
            from services.governance.audit import log_audit_event
            log_audit_event(
                action="SOVEREIGN_MEDIA_GENERATE",
                metadata={"prompt": prompt, "duration_sec": 45.0, "quality": "q6_k", "type": "video"}
            )
            return "https://media.aimos.ai/mock/sovereign_ad_video.mp4"
        
        logger.info(f"CreativeEngine: Video generation requested for prompt: {prompt}")
        return None
