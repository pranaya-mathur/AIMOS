import os
import sys
import httpx
from pathlib import Path

# Paths relative to root
MODEL_DIR = Path("backend/models/sovereign")
MODELS = {
    "flux1-dev-q6_k.gguf": "https://huggingface.co/city96/FLUX.1-dev-gguf/resolve/main/flux1-dev-Q6_K.gguf",
    "clip_l.safetensors": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors",
    "t5xxl_fp16.safetensors": "https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp16.safetensors",
    "ae.safetensors": "https://huggingface.co/lllyasviel/flux1-dev-mirror/resolve/main/ae.safetensors"
}

def download_models():
    print("=== AIMOS SOVEREIGN MODEL DOWNLOADER ===")
    
    if not MODEL_DIR.exists():
        MODEL_DIR.mkdir(parents=True)
        print(f"Created directory: {MODEL_DIR}")

    total_size_est_gb = 22 # Flux Dev Q6_K is large
    print(f"Note: This will download approximately {total_size_est_gb}GB of data.")
    
    # Check disk space (briefly)
    # import shutil
    # _, _, free = shutil.disk_usage("/")
    # if free < (total_size_est_gb + 5) * 1024**3:
    #     print("ERROR: Insufficient disk space for Sovereign models.")
    #     sys.exit(1)

    with httpx.Client(follow_redirects=True, timeout=None) as client:
        for name, url in MODELS.items():
            target = MODEL_DIR / name
            if target.exists():
                print(f"✅ {name} already exists. Skipping.")
                continue
                
            print(f"Downloading {name} from {url}...")
            try:
                # In a real environment, we would use tqdm for progress
                # For this script, we'll just download
                with open(target, "wb") as f:
                    with client.stream("GET", url) as response:
                        response.raise_for_status()
                        for chunk in response.iter_bytes():
                            f.write(chunk)
                print(f"✅ Downloaded {name}")
            except Exception as e:
                print(f"❌ Failed to download {name}: {e}")

    print("\nSovereign Model Setup Complete.")

if __name__ == "__main__":
    download_models()
