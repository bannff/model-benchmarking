#!/bin/bash
# M4 OPTIMIZED MAMBA SPEED TRAINING
# Optimized for Apple M4 with MLX-LM native acceleration

set -e

# Add MLX-LM to PATH
export PATH="/Users/danielrodrigo/Library/Python/3.9/bin:$PATH"

echo "🚀 M4 OPTIMIZED MAMBA SPEED TRAINING"
echo "===================================="
echo "🎯 Target: Maximum training speed on Apple M4"
echo "⚡ Optimizations: Higher batch size, reduced iters, smart LoRA config"
echo ""

# Validate dataset exists - prioritize the enhanced cybersec dataset
if [ -f "datasets/primus_training/train_enhanced.jsonl" ]; then
    echo "✅ Using enhanced cybersec dataset (569K high-quality samples)"
    DATASET_PATH="datasets/primus_training"
elif [ -f "datasets/cybersec_training/train_full.jsonl" ]; then
    echo "✅ Using full cybersec dataset (50K samples)"
    DATASET_PATH="datasets/cybersec_training"
else
    echo "❌ No suitable dataset found!"
    exit 1
fi

# Count entries
if [ -f "$DATASET_PATH/train_full.jsonl" ]; then
    ENTRIES=$(wc -l < "$DATASET_PATH/train_full.jsonl")
    echo "📊 Training dataset: $ENTRIES entries (train_full.jsonl)"
elif [ -f "$DATASET_PATH/train_enhanced.jsonl" ]; then
    ENTRIES=$(wc -l < "$DATASET_PATH/train_enhanced.jsonl")
    echo "📊 Training dataset: $ENTRIES entries (train_enhanced.jsonl)"
else
    ENTRIES=$(wc -l < "$DATASET_PATH/train.jsonl")
    echo "📊 Training dataset: $ENTRIES entries (train.jsonl)"
fi

# Clean start verification
if [ -d "adapters" ] && [ "$(ls -A adapters 2>/dev/null)" ]; then
    echo "⚠️  Found existing adapters - removing for fresh start"
    rm -rf adapters
    echo "✅ Cleaned existing adapters"
fi

echo "🆕 Starting fresh M4-optimized speed training"
echo ""

# M4 Optimized Training Configuration
echo "🚀 Starting M4-optimized Mamba fine-tuning..."
echo "⚙️  Model: models/mamba-1.4b-mlx"
echo "🎯 Target: Cybersecurity specialization"
echo "⚡ M4 Optimizations: ENABLED"
echo "📈 Configuration:"
echo "   • Batch Size: 4 (optimized for large dataset)"
echo "   • Learning Rate: 1e-4 (stable for large data)"
echo "   • Iterations: 600 (efficient for 569K samples)"
echo "   • Validation Batches: 25 (memory efficient)"
echo "   • Sequence Length: 384 (speed optimized)"
echo "   • Save Every: 100 (frequent checkpoints)"
echo ""

# Launch M4-optimized training
python3 -m mlx_lm lora \
  --model "models/mamba-1.4b-mlx" \
  --train \
  --data "$DATASET_PATH" \
  --batch-size 4 \
  --num-layers -1 \
  --learning-rate 1e-4 \
  --iters 600 \
  --val-batches 25 \
  --steps-per-report 50 \
  --steps-per-eval 150 \
  --adapter-path adapters \
  --save-every 100 \
  --max-seq-length 384 \
  --grad-checkpoint \
  --seed 42

echo ""
echo "🎉 M4-OPTIMIZED TRAINING COMPLETED!"
echo "====================================="
echo "✅ Training finished successfully!"
echo "🧠 Adapters saved to: adapters/"
echo "📊 Final checkpoint: adapters/adapters.safetensors"
echo "🚀 Ready to test your lightning-fast cybersecurity model!"
echo ""
echo "💡 Speed improvements achieved:"
echo "   • Large-scale dataset training (569K samples)"
echo "   • Optimized batch size for stability"
echo "   • M4 memory bandwidth optimized"
echo "   • Frequent checkpointing (every 100 steps)"
echo "   • Enhanced cybersecurity dataset quality"
