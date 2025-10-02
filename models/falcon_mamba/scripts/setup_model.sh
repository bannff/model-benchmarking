#!/bin/bash
# Falcon-Mamba 7B Model Setup
# Downloads and converts the model for MLX training

echo "🚀 FALCON-MAMBA 7B SETUP"
echo "================================"
echo "📋 Setting up Falcon-Mamba for MLX training"
echo "🔧 Model: tiiuae/falcon-mamba-7b-instruct"
echo "💾 Size: ~7.27B parameters"
echo ""

# Create models directory
echo "📁 Creating models directory..."
mkdir -p models

# Check if MLX-LM is installed
if ! command -v mlx_lm.convert &> /dev/null; then
    echo "❌ MLX-LM not found. Installing..."
    pip install mlx-lm
else
    echo "✅ MLX-LM found"
fi

# Option 1: Use pre-converted MLX model (faster)
echo ""
echo "🔽 DOWNLOAD OPTIONS:"
echo "1. Pre-converted MLX model (recommended - faster)"
echo "2. Convert from HuggingFace original (slower but latest)"
echo ""
read -p "Choose option (1/2): " choice

if [[ $choice == "1" ]]; then
    echo "📦 Downloading pre-converted MLX Falcon-Mamba..."
    echo "🎯 Using: mlx-community/falcon-mamba-7b-4bit-instruct"
    
    python3 -c "
from mlx_lm import load
import os

# Download pre-converted model
print('📥 Downloading MLX Falcon-Mamba model...')
model, tokenizer = load('mlx-community/falcon-mamba-7b-4bit-instruct')

# Save locally
model_path = './models/falcon_mamba_mlx'
print(f'💾 Saving to: {model_path}')
os.makedirs(model_path, exist_ok=True)

# The model is automatically cached by MLX-LM
print('✅ Model downloaded and ready!')
print('📍 Model cached in MLX-LM cache directory')
"

elif [[ $choice == "2" ]]; then
    echo "🔄 Converting from HuggingFace original..."
    echo "⚠️  This will take longer but gives you the latest version"
    
    python3 -c "
from mlx_lm import convert
import os

print('🔄 Converting Falcon-Mamba to MLX format...')
print('📋 This may take 10-15 minutes...')

# Convert with 4-bit quantization to save memory
convert(
    'tiiuae/falcon-mamba-7b-instruct',
    mlx_path='./models/falcon_mamba_mlx',
    quantize=True,
    q_bits=4,
    q_group_size=64
)

print('✅ Conversion complete!')
"

else
    echo "❌ Invalid choice. Exiting."
    exit 1
fi

echo ""
echo "🎉 SETUP COMPLETE!"
echo "✅ Falcon-Mamba 7B ready for training"
echo "📍 Model location: ./models/falcon_mamba_mlx/"
echo ""
echo "Next steps:"
echo "1. Run: ./falcon_mamba_train.sh"
echo "2. Monitor training progress"
echo "3. Compare with TinyLlama results"
