#!/bin/bash

# Enhanced Training Script - Generated 20250723_114952
# Includes pattern identification and truthfulness training

echo "Starting enhanced LoRA training with pattern identification..."
echo "Training data: /Users/danielrodrigo/Workspace/PyScience/datasets/primus_training_ENHANCED_20250723_114952"
echo "Target: Achieve loss < 1.0 with truthful responses"

# Set memory limits
export MLX_METAL_BUFFER_SIZE=20GB
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.0

cd /Users/danielrodrigo/Workspace/PyScience

# Enhanced training with proven parameters
python -m mlx_lm lora \
    --model /Users/danielrodrigo/Workspace/PyScience/datasets/mlx_models/tinyllama_mlx \
    --data /Users/danielrodrigo/Workspace/PyScience/datasets/primus_training_ENHANCED_20250723_114952 \
    --train \
    --batch-size 32 \
    --iters 10000 \
    --learning-rate 5e-5 \
    --optimizer adamw \
    --steps-per-report 5 \
    --steps-per-eval 25 \
    --save-every 100 \
    --max-seq-length 1024 \
    --num-layers -1 \
    --adapter-path ./cybersecurity_finetuned_models/mlx_adapters_enhanced_20250723_114952 \
    --grad-checkpoint \
    --seed 42

echo "Enhanced training completed!"
