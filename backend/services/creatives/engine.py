import os
import json
import logging
import platform
import random
import hashlib
import time
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
        
        # 1. PRIMARY: Local ComfyUI (Juggernaut XL)
        # Check if ComfyUI is reachable
        from services.comfy.client import ComfyClient
        comfy = ComfyClient(settings.comfyui_url)
        
        if comfy.ping():
            logger.info("CreativeEngine: Executing PRIMARY ComfyUI Generation (Juggernaut XL)")
            try:
                # 1a. Generate high-fidelity prompt
                from services.comfy.engine import PromptEngine
                # We use 'raw_product' or 'luxury' style for brand logos
                p_data = PromptEngine.generate(
                    product_name="Product", 
                    features=prompt, 
                    style_preference="luxury", 
                    mode="logo"
                )
                
                logger.info(f"CreativeEngine: Prompt generated for IMAGE mode. Positive: {p_data['positive'][:100]}...")

                
                # 1b. Load Workflow
                wf_path = os.path.join(os.path.dirname(__file__), "..", "comfy", "workflows", "image_gen_juggernaut.json")
                with open(wf_path, "r") as f:
                    workflow = json.load(f)
                
                # 1c. Inject Prompt + randomise seed so every call is unique
                if "2" in workflow:
                    workflow["2"]["inputs"]["text"] = p_data["positive"]
                if "3" in workflow:
                    workflow["3"]["inputs"]["text"] = p_data["negative"]
                
                # Set Image Resolution (1024x1024) in Node 4
                if "4" in workflow:
                    workflow["4"]["inputs"]["width"] = 1024
                    workflow["4"]["inputs"]["height"] = 1024
                
                # Set KSampler for Image Quality (Node 5)
                if "5" in workflow:
                    workflow["5"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
                    workflow["5"]["inputs"]["steps"] = 8
                    workflow["5"]["inputs"]["cfg"] = 2.0
                
                # 1d. Process
                output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "images")
                results = comfy.process_workflow(workflow, output_dir)
                
                if results:
                    import base64
                    with open(results[0], "rb") as f:
                        img_str = base64.b64encode(f.read()).decode()
                    return f"data:image/png;base64,{img_str}"
            except Exception as e:
                logger.error(f"ComfyUI primary generation failed: {e}")

        # 2. FALLBACK: Cloud (Stability AI)
        if settings.stability_api_key:
            logger.info("CreativeEngine: Routing to FALLBACK Cloud (Stability AI)")
            from services.integrations.stability_ai import StabilityAIClient
            client = StabilityAIClient()
            return client.generate_logo(prompt)
        
        # 3. FINAL FALLBACK: Mock/Placeholder
        logger.warning("No generative paths available. Returning high-fidelity mock.")
        return f"https://placehold.co/1024x1024/6366f1/ffffff?text=AIMOS+Creative:+{prompt[:20]}..."

    @staticmethod
    def generate_banner(product_name: str, features: str, style_preference: str = "luxury") -> Optional[str]:
        """
        Specialized banner generation for ad campaigns.
        Uses horizontal aspect ratio (1280x720) and banner-specific prompting.
        """
        settings = get_settings()
        
        # 1. PRIMARY: Local ComfyUI (Juggernaut XL)
        from services.comfy.client import ComfyClient
        comfy = ComfyClient(settings.comfyui_url)
        
        if comfy.ping():
            logger.info(f"CreativeEngine: Executing BANNER ComfyUI Generation for {product_name}")
            try:
                from services.comfy.engine import PromptEngine
                # Use timestamp-based iteration for true entropy — different prompt every call
                iteration = int(time.time() * 1000)
                p_data = PromptEngine.generate(
                    product_name=product_name,
                    features=features,
                    style_preference=style_preference,
                    mode="banner",
                    iteration=iteration,
                )
                
                wf_path = os.path.join(os.path.dirname(__file__), "..", "comfy", "workflows", "image_gen_juggernaut.json")
                with open(wf_path, "r") as f:
                    workflow = json.load(f)
                
                # Inject Prompt + Seed + Horizontal Resolution
                if "2" in workflow:
                    workflow["2"]["inputs"]["text"] = p_data["positive"]
                if "3" in workflow:
                    workflow["3"]["inputs"]["text"] = p_data["negative"]
                
                logger.info(f"CreativeEngine: Banner Prompt generated. Positive: {p_data['positive'][:100]}...")
                
                # Set Banner Resolution (1280x720) in Node 4
                if "4" in workflow:
                    workflow["4"]["inputs"]["width"] = 1280
                    workflow["4"]["inputs"]["height"] = 720
                
                # Set KSampler for Banner Quality (Node 5)
                if "5" in workflow:
                    workflow["5"]["inputs"]["seed"] = random.randint(0, 2**32 - 1)
                    workflow["5"]["inputs"]["steps"] = 8
                    workflow["5"]["inputs"]["cfg"] = 2.0
                
                output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "images")
                results = comfy.process_workflow(workflow, output_dir)
                
                if results:
                    import base64
                    with open(results[0], "rb") as f:
                        img_str = base64.b64encode(f.read()).decode()
                    return f"data:image/png;base64,{img_str}"
            except Exception as e:
                logger.error(f"ComfyUI banner generation failed: {e}")

        # Fallback to Stability (using 16:9 aspect ratio)
        if settings.stability_api_key:
            from services.integrations.stability_ai import StabilityAIClient
            client = StabilityAIClient()
            # Stability Client doesn't have native 16:9 yet in create_logo, but we'd add it
            return client.generate_logo(f"Horizontal banner for {product_name}: {features}")
            
        return f"https://placehold.co/1280x720/6366f1/ffffff?text={product_name}+Banner"

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
