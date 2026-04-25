#!/bin/bash

# scripts/optimize_sovereign_models.sh
# Helps optimize the Sovereign Creative Engine for low-RAM (16GB) hardware.

MODEL_DIR="backend/models/sovereign"
mkdir -p "$MODEL_DIR"

echo "=== Sovereign Model Optimizer (16GB RAM Target) ==="

# 1. Check VAE Integrity
if [ -f "$MODEL_DIR/ae.safetensors" ] && [ ! -s "$MODEL_DIR/ae.safetensors" ]; then
    echo "⚠️  Detected empty ae.safetensors. This will cause Flux to hang."
    echo "Fetching a valid VAE..."
    # Placeholder for actual curl - ideally use huggingface-cli
    # curl -L -o "$MODEL_DIR/ae.safetensors" "https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors"
fi

# 2. Suggest Quantized T5
if [ -f "$MODEL_DIR/t5xxl_fp16.safetensors" ]; then
    SIZE=$(du -sh "$MODEL_DIR/t5xxl_fp16.safetensors" | cut -f1)
    echo "ℹ️  Current T5-XXL is FP16 ($SIZE). This is likely causing your system hangs."
    echo "Suggestion: Download a GGUF quantized version of T5-XXL (Q4_K_M) to save ~6GB RAM."
    echo ""
    echo "Command to download Q4 T5:"
    echo "curl -L -o \"$MODEL_DIR/t5xxl-Q4_K_M.gguf\" \"https://huggingface.co/city96/t5-v1_1-xxl-encoder-gguf/resolve/main/t5xxl-Q4_K_M.gguf\""
    echo ""
    echo "Then update SD_MODEL_PATH or config to point to it."
fi

echo "=== Optimization Tips Finished ==="
