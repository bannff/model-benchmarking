#!/bin/bash
# SOLERA DEMO SETUP - Download all dependencies
# Run this first to set up everything needed for the demo

echo "🚀 SOLERA FINE-TUNING DEMO SETUP"
echo "======================================"
echo "📦 Installing all dependencies..."
echo "This will download TinyLlama model and install MLX-LM"
echo ""

# Check if on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "❌ This demo requires Apple Silicon (M1/M2/M3) Mac"
    echo "MLX is optimized for Apple Silicon only"
    exit 1
fi

echo "✅ Detected Apple Silicon Mac"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install mlx-lm transformers huggingface_hub

# Create models directory
echo "📁 Creating models directory..."
mkdir -p models

# Download TinyLlama model
echo "🔽 Downloading TinyLlama model (this may take a few minutes)..."
echo "📍 Downloading to: $(pwd)/models/tinyllama_mlx"

python3 -c "
import os
from mlx_lm import convert

print('Converting TinyLlama to MLX format...')
convert(
    'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
    mlx_path='./models/tinyllama_mlx',
    quantize=False
)
print('✅ TinyLlama downloaded and converted successfully!')
"

echo ""
echo "🎉 SETUP COMPLETE!"
echo "✅ MLX-LM installed"  
echo "✅ TinyLlama model downloaded"
echo "✅ Ready for demo!"
echo ""
echo "Next steps:"
echo "1. Run: ./1_demo_base_model.py (show base model doesn't know Solera)"
echo "2. Run: ./2_run_training.sh (train the model - 35 seconds)"
echo "3. Run: ./3_demo_trained_model.py (show trained model knows Solera)"
echo ""
echo "🎯 Total demo time: ~2-3 minutes + training time"
