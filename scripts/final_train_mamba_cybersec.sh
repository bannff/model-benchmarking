#!/bin/bash
# FINAL MAMBA CYBERSECURITY TRAINING
# High-quality dataset with optimized Mamba configuration

set -e

echo "🐍 FINAL MAMBA CYBERSECURITY TRAINING"
echo "====================================="

# Validate dataset exists
if [ ! -f "datasets/cybersec_training/train.jsonl" ]; then
    echo "❌ Clean dataset not found! Check datasets directory."
    exit 1
fi

# Count entries
ENTRIES=$(wc -l < datasets/cybersec_training/train.jsonl)
echo "📊 Training dataset: $ENTRIES entries"

# Check for existing adapters
if [ -d "adapters" ] && [ "$(ls -A adapters)" ]; then
    echo "🔄 Found existing adapters - this will resume training"
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting..."
        exit 1
    fi
else
    echo "🆕 Starting fresh training with cleaned dataset"
fi

# Start training with optimized configuration
echo "🚀 Starting Mamba fine-tuning..."
echo "⚙️  Model: models/mamba-1.4b-mlx (LOCAL DRIVE)"
echo "🎯 Target: Cybersecurity specialization"
echo "📈 Configuration: Final optimized settings"
echo ""

python3 -m mlx_lm lora \
  --model "models/mamba-1.4b-mlx" \
  --train \
  --data datasets/cybersec_training \
  --batch-size 4 \
  --num-layers -1 \
  --learning-rate 1e-4 \
  --iters 1500 \
  --steps-per-report 100 \
  --steps-per-eval 500 \
  --adapter-path adapters \
  --save-every 250 \
  --max-seq-length 512 \
  --grad-checkpoint \
  --seed 42

echo ""
echo "✅ Training completed!"
echo "🧠 Adapters saved to: adapters/"
echo "🚀 Ready to test cybersecurity model!"
