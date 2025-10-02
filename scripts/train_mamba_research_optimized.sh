#!/bin/bash
# Research-Optimized Mamba Fine-tuning Script
# Based on MambaPEFT and SLFT research findings

set -e

echo "========================================"
echo "Research-Optimized Mamba Fine-tuning"
echo "========================================"
echo "Dataset: datasets/train.jsonl (cleaned & deduplicated)"
echo "Model: mlx-community/mamba-1.4b-hf"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Check dataset
if [ ! -f "datasets/train.jsonl" ]; then
    echo "Error: datasets/train.jsonl not found!"
    exit 1
fi

dataset_size=$(wc -l < datasets/train.jsonl)
echo "Dataset: $dataset_size entries (cleaned)"
echo ""

echo "Starting research-optimized training..."
python -m mlx_lm.lora \
    --model mlx-community/mamba-1.4b-hf \
    --train \
    --data datasets/train.jsonl \
    --batch-size 4 \
    --lora-layers 16 \
    --lora-rank 8 \
    --lora-alpha 16 \
    --lora-dropout 0.05 \
    --learning-rate 8e-5 \
    --num-epochs 3 \
    --steps-per-report 100 \
    --steps-per-eval 500 \
    --adapter-path ./cybersecurity_mamba_adapter \
    --save-every 1000 \
    --max-seq-length 512 \
    --grad-checkpoint \
    --warmup-steps 100 \
    --weight-decay 0.01 \
    --seed 42 \
    --ignore-chat-template

echo "Training completed!"
