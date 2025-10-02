#!/bin/bash
# Mamba Cybersecurity Fine-tuning Script
# Optimized for selective state space model adaptation

set -e

echo "Starting Mamba cybersecurity fine-tuning..."
echo "Dataset: datasets/primus_training/train.jsonl"
echo "Validation: datasets/primus_training/valid.jsonl"
echo "Model: mlx-community/mamba-1.4b-hf"
echo "Approach: Selective LoRA targeting SSM layers"

# Check dataset exists

# Check dataset exists
if [ ! -f "datasets/primus_training/train.jsonl" ]; then
    echo "Error: datasets/primus_training/train.jsonl not found!"
    exit 1
fi

if [ ! -f "datasets/primus_training/valid.jsonl" ]; then
    echo "Error: datasets/primus_training/valid.jsonl not found!"
    exit 1
fi

# Check dataset size
dataset_size=$(wc -l < datasets/primus_training/train.jsonl)
valid_size=$(wc -l < datasets/primus_training/valid.jsonl)
echo "Training dataset size: $dataset_size entries"
echo "Validation dataset size: $valid_size entries"

python3 -m mlx_lm lora \
    --model models/mamba-1.4b-mlx \
    --config datasets/training_config.yaml

echo "Training completed!"
echo "Adapter saved to: ./cybersecurity_finetuned_models/mamba_cybersec_adapter"


# Test the trained model
echo "Testing trained model..."
python3 -c "
import mlx_lm
print('Loading trained model...')
model, tokenizer = mlx_lm.load('./cybersecurity_finetuned_models/mamba_cybersec_adapter')
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
