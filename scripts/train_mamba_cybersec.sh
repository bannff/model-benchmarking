#!/bin/bash
# Mamba Cybersecurity Fine-tuning Script
# Optimized for selective state space model adaptation

set -e

echo "Starting Mamba cybersecurity fine-tuning..."
echo "Dataset: cleaned_cybersecurity_dataset.jsonl"
echo "Model: mlx-community/mamba-1.4b-hf"
echo "Approach: Selective LoRA targeting SSM layers"

# Check dataset exists
if [ ! -f "cleaned_cybersecurity_dataset.jsonl" ]; then
    echo "Error: cleaned_cybersecurity_dataset.jsonl not found!"
    exit 1
fi

# Check dataset size
dataset_size=$(wc -l < cleaned_cybersecurity_dataset.jsonl)
echo "Dataset size: $dataset_size entries"

# Start training with Mamba-optimized configuration
python -m mlx_lm.lora \
    --model mlx-community/mamba-1.4b-hf \
    --train \
    --data cleaned_cybersecurity_dataset.jsonl \
    --batch-size 4 \
    --lora-layers 16 \
    --lora-rank 8 \
    --lora-alpha 16 \
    --lora-dropout 0.1 \
    --learning-rate 1e-4 \
    --num-epochs 3 \
    --steps-per-report 100 \
    --steps-per-eval 500 \
    --adapter-path ./cybersecurity_mamba_adapter \
    --save-every 1000 \
    --max-seq-length 512 \
    --grad-checkpoint \
    --warmup-steps 100 \
    --seed 42 \
    --ignore-chat-template

echo "Training completed!"
echo "Adapter saved to: ./cybersecurity_mamba_adapter"

# Test the trained model
echo "Testing trained model..."
python -c "
import mlx_lm
print('Loading trained model...')
model, tokenizer = mlx_lm.load('./cybersecurity_mamba_adapter')
print('Model loaded successfully!')

# Test cybersecurity query
test_prompt = 'User: What are the key indicators of a SQL injection vulnerability?\nAssistant:'
print(f'Test prompt: {test_prompt}')

response = mlx_lm.generate(
    model, tokenizer, 
    prompt=test_prompt, 
    max_tokens=200, 
    temp=0.7
)
print(f'Response: {response}')
"

echo "Fine-tuning and testing completed successfully!"
