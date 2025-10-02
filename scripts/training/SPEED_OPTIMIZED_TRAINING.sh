#!/bin/bash
# SPEED-OPTIMIZED MLX Training - Faster Convergence Strategy
# Target: Reduce training time from 69 hours to ~24-30 hours
# Maintains quality while prioritizing speed

# Force maximum Metal memory allocation
export MLX_METAL_BUFFER_CACHE_LIMIT=0
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export MLX_DISABLE_WARNING=1

cd /Users/danielrodrigo/Workspace/PyScience/datasets && python3 -c "
import mlx.core as mx
# Maximize memory allocation for higher batch sizes
mx.set_memory_limit(20 * 1024 * 1024 * 1024)  # 20GB force allocation
mx.set_cache_limit(20 * 1024 * 1024 * 1024)   # 20GB cache
print('MLX Memory limits set to 20GB for speed optimization')
print('Targeting 2x throughput with larger batch size')
" && python3 -m mlx_lm lora \
  --model /Users/danielrodrigo/Workspace/PyScience/datasets/mlx_models/tinyllama_mlx \
  --data /Users/danielrodrigo/Workspace/PyScience/datasets/primus_training_FINAL \
  --resume-adapter-file /Users/danielrodrigo/Workspace/PyScience/cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1/0002000_adapters.safetensors \
  --train \
  --batch-size 64 \
  --iters 6000 \
  --learning-rate 5e-5 \
  --optimizer adamw \
  --steps-per-report 5 \
  --steps-per-eval 25 \
  --save-every 100 \
  --max-seq-length 512 \
  --num-layers 8 \
  --adapter-path ./cybersecurity_finetuned_models/mlx_adapters_primus_SPEED_OPTIMIZED \
  --grad-checkpoint \
  --seed 42

echo "Speed-optimized training completed!"
