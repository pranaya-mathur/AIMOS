import logging
import httpx
import os
from typing import Optional
from core.config import get_settings

logger = logging.getLogger(__name__)

class StabilityAIClient:
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.stability_api_key
        self.base_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"

    def generate_logo(self, prompt: str) -> Optional[str]:
        """Generate a logo using SDXL and return the base64 or a mock URL."""
        if self.settings.mock_media_enabled or not self.api_key:
            logger.info("stability.mock_generate_logo prompt='%s'", prompt)
            return "https://placehold.co/1024x1024/6366f1/ffffff?text=AI+Logo"

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        
        # Crafting a professional logo prompt
        enhanced_prompt = f"Professional minimalist logo for: {prompt}. High resolution, clean vectors, white background, trending on dribbble."

        body = {
            "text_prompts": [{"text": enhanced_prompt}],
            "cfg_scale": 7,
            "height": 1024,
            "width": 1024,
            "samples": 1,
            "steps": 30,
        }

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.base_url, headers=headers, json=body)
                response.raise_for_status()
                data = response.json()
                # Stability returns base64 in 'artifacts'
                # For this implementation, we would normally upload to media_store (S3/GCS)
                # But here we'll return the artifacts[0] or a transient URL
                return f"data:image/png;base64,{data['artifacts'][0]['base64']}"
        except Exception as e:
            logger.exception("Stability AI logo generation failed")
            return None

def generate_logo_tool(prompt: str) -> Optional[str]:
    client = StabilityAIClient()
    return client.generate_logo(prompt)
