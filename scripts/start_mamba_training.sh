#!/bin/bash
# FINAL MAMBA CYBERSECURITY TRAINING
# High-quality dataset with ALL LAYERS targeting

set -e

echo "🐍 MAMBA CYBERSECURITY TRAINING - ALL LAYERS"
echo "============================================="

# Validate dataset exists
if [ ! -f "datasets/train.jsonl" ]; then
    echo "❌ Clean dataset not found!"
    exit 1
fi

# Count entries
ENTRIES=$(wc -l < datasets/train.jsonl)
echo "📊 Training dataset: $ENTRIES entries"

# Remove any existing adapters for fresh start
if [ -d "adapters" ]; then
    echo "🧹 Removing old adapters for fresh training"
    rm -rf adapters
fi

echo "🆕 Starting fresh training with ALL LAYERS targeting"
echo ""

# Start training with optimized configuration
echo "🚀 Starting Mamba fine-tuning..."
echo "⚙️  Model: mlx-community/mamba-1.4b-hf-f16" 
echo "🎯 Target: ALL LAYERS (-1)"
echo "📈 Dataset: Clean cybersecurity data"
echo ""

python3 -m mlx_lm lora \
  --model mlx-community/mamba-1.4b-hf-f16 \
  --train \
  --data datasets/train.jsonl \
  --batch-size 1 \
  --num-layers -1 \
  --learning-rate 2e-5 \
  --iters 5000 \
  --save-every 1000 \
  --adapter-path adapters \
  --grad-checkpoint \
  --val-batches 25 \
  --max-seq-length 512

echo ""
echo "✅ Training completed!"
echo "🧠 Adapters saved to: adapters/"
echo "🚀 Ready to test cybersecurity model!"
