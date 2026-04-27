import os
import sys
import json
from pathlib import Path

# Setup path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from core.config import get_settings
from services.creatives.engine import CreativeEngine
from db import SessionLocal
from models import AuditLog

def sample_run():
    print("=== AIMOS SOVEREIGN LIVE SAMPLE RUN ===")
    
    # 1. Enable Sovereign (Unless overridden by shell)
    if os.getenv("SOVEREIGN_MODE") is None:
        os.environ["SOVEREIGN_MODE"] = "true"
    
    # Pre-flight check: Warn about memory if not mocking
    if os.getenv("MOCK_SOVEREIGN") != "true":
        print("⚠️  ATTENTION: Sovereign Mode is ACTIVE. Loading models (>18GB) will likely hang a 16GB RAM system.")
        print("💡 Ensure you have quantized models or at least 24GB+ unified memory.")
    
    # We only mock if not explicitly told otherwise
    if os.getenv("MOCK_SOVEREIGN") is None:
        os.environ["MOCK_SOVEREIGN"] = "false"
        
    from core.config import get_settings
    get_settings.cache_clear()
    
    # 2. Sample Briefs
    image_prompt = "A hyper-realistic, minimalist dental office interior, warm ambient lighting, professional dental chair, teal accents, white walls, soft focus, 8k resolution."
    video_prompt = "Cinematic 5-second pan of a modern dental clinic interior, soft transition to a high-speed dental drill, 4k, professional lighting."
    
    print(f"\n[IMAGE GEN] Calling Sovereign Engine for: '{image_prompt[:50]}...'")
    img_res = CreativeEngine.generate_image(image_prompt)
    print(f"✅ Image Result: {img_res[:60]}... [Base64 Sovereign Output]")
    
    print(f"\n[VIDEO GEN] Calling Sovereign Engine for: '{video_prompt[:50]}...'")
    # We'll update the engine briefly to return a mock for video too
    vid_res = CreativeEngine.generate_video(video_prompt)
    print(f"✅ Video Result: {vid_res}")

    # 3. Governance Insight
    print("\n[GOVERNANCE] Checking Sovereign Insight Trace...")
    db = SessionLocal()
    try:
        logs = db.query(AuditLog).filter(AuditLog.action == "SOVEREIGN_MEDIA_GENERATE").order_by(AuditLog.timestamp.desc()).limit(2).all()
        for log in logs:
            print(f"- Event: {log.action} | Prompt: {log.metadata_json.get('prompt')[:40]}... | Quant: {log.metadata_json.get('quality')}")
    finally:
        db.close()

    print("\n=== SAMPLE RUN COMPLETE: SYSTEM READY FOR PRODUCTION MODELS ===")

if __name__ == "__main__":
    sample_run()
