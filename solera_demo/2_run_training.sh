#!/bin/bash
# DEMO: 10-Minute Solera Secret Fine-Tuning Demo
# Shows the power of fine-tuning vs prompt engineering/RAG

echo "🚀 SOLERA DEMO: Teaching TinyLlama a Secret"
echo "=" * 50
echo "📊 Dataset: 10 examples of Solera knowledge"
echo "⏱️  Target: Complete in 10-15 minutes"
echo "🎯 Goal: Model learns info it couldn't know otherwise"
echo "=" * 50

# Minimal memory setup for speed
export MLX_METAL_BUFFER_SIZE=8GB
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0

echo "📝 Training TinyLlama with Solera secret knowledge..."

python3 -m mlx_lm lora \
  --model /Users/danielrodrigo/Workspace/PyScience/solera_demo/models/tinyllama_mlx \
  --data . \
  --train \
  --batch-size 2 \
  --iters 100 \
  --learning-rate 1e-4 \
  --optimizer adamw \
  --steps-per-report 5 \
  --steps-per-eval 25 \
  --save-every 25 \
  --max-seq-length 512 \
  --num-layers -1 \
  --adapter-path ./adapters \
  --grad-checkpoint \
  --seed 42

echo "✅ Demo training complete!"
echo "🎯 Model now knows the Solera secret!"
echo "💡 Ready to demonstrate fine-tuning > prompt engineering"
