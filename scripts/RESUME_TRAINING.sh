#!/bin/bash
# IMPROVED MLX Training - Enhanced Convergence Strategy
# Based on model evaluation: Reducing learning rate, adding regularization, better monitoring  
# Target: Push loss below 1.0, reduce repetitive patterns, stable convergence

# Force maximum Metal memory allocation
export MLX_METAL_BUFFER_CACHE_LIMIT=0
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0
export MLX_DISABLE_WARNING=1

cd /Users/danielrodrigo/Workspace/PyScience/scripts && python3 -c "
import mlx.core as mx
mx.set_memory_limit(20 * 1024 * 1024 * 1024)  # 20GB force allocation
mx.set_cache_limit(20 * 1024 * 1024 * 1024)  # 20GB cache
print('MLX Memory limits set to 20GB')
print('Maximum memory allocation forced')
" && python3 -m mlx_lm lora \
  --model /Users/danielrodrigo/Workspace/PyScience/datasets/mlx_models/tinyllama_mlx \
  --data /enhanced_data/train.jsonl \
  --train \
  --adapter-path ./tinyllama_lora_adapter \
  --batch-size 16 \
  --iters 1000 \
  --learning-rate 2e-5 \
  --scale 128 \
  --steps-per-report 20 \
  --save-every 200 \
  --max-seq-length 1024 \
  --seed 42