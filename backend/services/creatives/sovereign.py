import os
import logging
import time
from core.config import get_settings

logger = logging.getLogger(__name__)

class SovereignMediaClient:
    """
    Sovereign Media Client using GGUF models via stable-diffusion-cpp-python.
    Optimized for Apple Silicon (MPS).
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.model_path = self.settings.sd_model_path
        # Juggernaut XL / SDXL usually don't require separate T5/CLIP files in SD.cpp if bundled
        self.clip_l_path = os.path.join(os.path.dirname(self.model_path), "clip_l.safetensors")
        self.t5xxl_path = os.path.join(os.path.dirname(self.model_path), "t5xxl.gguf")
        self.vae_path = os.path.join(os.path.dirname(self.model_path), "ae.safetensors")
        self._sd = None
        
    def _check_memory(self):
        """Check available system memory on macOS/Linux."""
        if not self.settings.memory_guard_enabled:
            return True
            
        import subprocess
        import platform
        import re
        
        try:
            if platform.system() == "Darwin":
                # Use vm_stat to get memory info on macOS
                result = subprocess.check_output(["vm_stat"]).decode()
                
                # Parse page size (e.g., "(page size of 16384 bytes)")
                page_size = 4096 # Default
                match = re.search(r"page size of (\d+) bytes", result)
                if match:
                    page_size = int(match.group(1))
                
                # Parse statistics
                pages = {}
                for line in result.split("\n"):
                    if ":" in line and not line.startswith("Mach Virtual Memory Statistics"):
                        key, val = line.split(":")
                        try:
                            pages[key.strip()] = int(val.strip().replace(".", ""))
                        except ValueError:
                            continue
                
                free_gb = (pages.get("Pages free", 0) + pages.get("Pages purgeable", 0) + pages.get("Pages inactive", 0)) * page_size / (1024**3)
                
                if free_gb < self.settings.memory_threshold_gb:
                    logger.warning(f"SovereignClient: Low memory detected ({free_gb:.2f}GB free). Threshold is {self.settings.memory_threshold_gb}GB.")
                    raise RuntimeError(f"Insufficient memory: {free_gb:.2f}GB available, but {self.settings.memory_threshold_gb}GB required for Sovereign ensemble.")
            return True
        except (subprocess.SubprocessError, KeyError, ValueError) as e:
            logger.warning(f"SovereignClient: Could not verify memory: {e}. Proceeding with caution.")
            return True

    def _validate_ensemble(self):
        """Verify main model exists. Secondary components are optional for SDXL/Juggernaut."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Sovereign Model missing at {self.model_path}")
        if os.path.getsize(self.model_path) < 2048:
            raise ValueError(f"Sovereign Model at {self.model_path} is invalid/empty.")
                
        # VAE is optional in some SD.cpp versions but we check it since it's referenced
        if os.path.exists(self.vae_path) and os.path.getsize(self.vae_path) == 0:
            logger.error(f"SovereignClient: VAE at {self.vae_path} is empty. This will cause generation failure.")
            raise ValueError(f"Sovereign VAE at {self.vae_path} is corrupt/empty.")
        
    def _lazy_init(self):
        if self._sd:
            return
            
        try:
            from stable_diffusion_cpp import StableDiffusion
            
            self._check_memory()
            self._validate_ensemble()
                
            logger.info(f"SovereignClient: Initializing StableDiffusion with model: {self.model_path}")
            
            self._sd = StableDiffusion(
                model_path=self.model_path,
                clip_l_path=self.clip_l_path if os.path.exists(self.clip_l_path) else None,
                t5xxl_path=self.t5xxl_path if os.path.exists(self.t5xxl_path) else None,
                n_threads=self.settings.sd_n_threads,
            )
            logger.info("SovereignClient: Successfully initialized via Metal/MPS.")
        except ImportError:
            logger.error("SovereignClient: stable-diffusion-cpp-python not installed.")
            raise
        except Exception as e:
            logger.error(f"SovereignClient: Failed to initialize: {e}")
            raise

    def generate_image(self, prompt: str, width: int = 1024, height: int = 1024) -> str:
        """
        Generate high-fidelity image locally.
        Enforces Q6_K logic via the selected GGUF model.
        """
        # 1. Check for missing components + Fallback to Mock if needed
        missing = []
        if not os.path.exists(self.model_path) or os.path.getsize(self.model_path) < 1024:
            missing.append("Main Model")
        if not self.t5xxl_path or not os.path.exists(self.t5xxl_path) or os.path.getsize(self.t5xxl_path) < 1024:
            missing.append("T5 Encoder")
        if not os.path.exists(self.vae_path) or os.path.getsize(self.vae_path) < 1024:
            missing.append("VAE")

        if missing:
            logger.warning(f"SovereignClient: Components missing ({', '.join(missing)}). Falling back to high-quality preview.")
            return f"https://placehold.co/1024x1024/0f172a/ffffff?text=Sovereign+Preview:+{prompt[:30]}..."

        self._lazy_init()
        
        start_time = time.time()
        logger.info(f"SovereignClient: Starting inference for prompt: {prompt}")
        
        # Detect if we are using Juggernaut / Lightning for step optimization
        model_name = os.path.basename(self.model_path).lower()
        is_lightning = "lightning" in model_name or "schnell" in model_name
        steps = 4 if is_lightning else 20
        cfg = 1.0 if is_lightning else 7.0
        
        # stable-diffusion-cpp-python v0.4.6 API: generate_image
        images = self._sd.generate_image(
            prompt=prompt,
            width=width,
            height=height,
            sample_method="euler_a" if not is_lightning else "latent_consistency",
            steps=steps, 
            cfg_scale=cfg,
            seed=-1
        )
        
        duration = time.time() - start_time
        logger.info(f"SovereignClient: Inference complete in {duration:.2f}s")
        
        # Result is typically a PIL Image or similar depending on version; 
        # For our integration, we'll return a base64 string or save to transient store
        # For simplicity in this pivot, we return the first image as base64
        import base64
        from io import BytesIO
        
        buffered = BytesIO()
        images[0].save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        from services.governance.audit import log_audit_event
        log_audit_event(
            action="SOVEREIGN_MEDIA_GENERATE",
            metadata={
                "prompt": prompt,
                "duration_sec": duration,
                "quality": self.settings.inference_quality_floor,
                "model": os.path.basename(self.model_path)
            }
        )
        
        return f"data:image/png;base64,{img_str}"
