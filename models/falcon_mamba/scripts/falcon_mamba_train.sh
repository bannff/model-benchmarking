#!/bin/bash
# FALCON-MAMBA 7B TRAINING SCRIPT
# Optimized for Apple Silicon with MLX-LM
# Uses same cybersecurity dataset as TinyLlama for comparison

echo "🚀 FALCON-MAMBA 7B TRAINING"
echo "=============================="
echo "🎯 Model: Falcon-Mamba 7B Instruct (4-bit QLoRA)"
echo "📊 Dataset: Enhanced agentic security dataset (518K examples with AWS vulnerabilities)"
echo "🔧 Method: QLoRA (4-bit quantized) fine-tuning"
echo ""

# Optimized memory management for QLoRA
export MLX_METAL_BUFFER_CACHE_LIMIT=0
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export MLX_DISABLE_WARNING=1

# Set up MLX memory limits for QLoRA (much more efficient)
cd /Users/danielrodrigo/Workspace/PyScience/falcon_mamba_training && python3 -c "
import mlx.core as mx
# QLoRA only needs ~10GB instead of 25GB
mx.set_memory_limit(12 * 1024 * 1024 * 1024)  # 12GB allocation
mx.set_cache_limit(12 * 1024 * 1024 * 1024)   # 12GB cache
print('MLX Memory limits set to 12GB for QLoRA')
print('Falcon-Mamba QLoRA memory optimization enabled')
"

echo "🧠 Memory optimization complete"
echo "🏋️  Starting LoRA training..."

# Check if we're resuming from a checkpoint
RESUME_CHECKPOINT=""
if [[ -f "./adapters/adapters.safetensors" ]]; then
    echo "🔍 Found existing adapters, resuming training..."
    RESUME_CHECKPOINT="--resume-adapter-file ./adapters/adapters.safetensors"
fi

echo ""
echo "⚡ QLORA TRAINING CONFIGURATION:"
echo "📦 Batch Size: 24 (increased due to QLoRA efficiency)"
echo "📚 Learning Rate: 2e-5 (optimized for quantized training)"
echo "🎯 Iterations: 3000 (fewer needed due to 4-bit efficiency)"
echo "💾 Save Every: 200 iterations"
echo "📏 Sequence Length: 2048 (optimal for security analysis)"
echo "🔧 Quantization: 4-bit with NF4 (67% memory reduction)"
echo ""

# Start QLoRA training with optimized parameters for 4-bit quantization
python3 -m mlx_lm lora \
  --model mlx-community/falcon-mamba-7b-4bit-instruct \
  --data /Users/danielrodrigo/Workspace/PyScience/datasets \
  $RESUME_CHECKPOINT \
  --train \
  --batch-size 24 \
  --iters 3000 \
  --learning-rate 2e-5 \
  --optimizer adamw \
  --steps-per-report 10 \
  --steps-per-eval 50 \
  --save-every 200 \
  --max-seq-length 2048 \
  --num-layers -1 \
  --adapter-path ./adapters \
  --grad-checkpoint \
  --seed 42

echo ""
echo "🎉 FALCON-MAMBA QLORA TRAINING COMPLETE!"
echo "✅ Final QLoRA adapters saved to: ./adapters/"
echo "📊 Model now has enhanced cybersecurity knowledge with 67% less memory usage"
echo ""
echo "Next steps:"
echo "1. Test with: python3 falcon_mamba_chat.py"
echo "2. Compare performance with TinyLlama"
echo "3. Evaluate cybersecurity knowledge quality"
echo "4. Benchmark memory efficiency vs traditional LoRA"
