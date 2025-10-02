#!/usr/bin/env python3
"""
MLX-LM Mamba Cybersecurity Fine-tuning Configuration
Based on MambaPEFT research for selective state space model fine-tuning.

This script configures MLX-LM to properly fine-tune Mamba 1.4B for cybersecurity
by targeting specific layers: in_proj, out_proj, dt_proj with selective LoRA.
"""

import json
import argparse
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_mamba_lora_config():
    """
    Create LoRA configuration optimized for Mamba architecture.
    Based on MambaPEFT research findings.
    """
    
    # Mamba-specific LoRA configuration
    config = {
        "model": "mlx-community/mamba-1.4b-hf",
        "train": True,
        "data": "cleaned_cybersecurity_dataset.jsonl",
        "batch_size": 4,
        "lora_layers": 16,  # Apply to multiple layers for better coverage
        "lora_rank": 8,     # Balanced rank for efficiency vs performance
        "lora_alpha": 16,   # Standard 2x rank scaling
        "lora_dropout": 0.1,
        "learning_rate": 1e-4,  # Conservative for stability
        "num_epochs": 3,
        "steps_per_report": 100,
        "steps_per_eval": 500,
        "resume_adapter_file": None,
        "adapter_path": "./cybersecurity_mamba_adapter",
        "save_every": 1000,
        "test": False,
        "test_batches": 100,
        "max_seq_length": 512,
        "grad_checkpoint": True,
        
        # Mamba-specific targeting
        "lora_targets": [
            # Primary SSM projection layers (most effective per research)
            ".*in_proj.*",      # Input projections to SSM
            ".*out_proj.*",     # Output projections from SSM  
            ".*dt_proj.*",      # Delta parameter projections (critical for selective SSM)
            
            # Additional linear layers for comprehensive adaptation
            ".*x_proj.*",       # X state projections
        ],
        
        # Training stability optimizations
        "warmup_steps": 100,
        "weight_decay": 0.01,
        "grad_clip_norm": 1.0,
        
        # Cybersecurity domain optimization
        "seed": 42,
        "ignore_chat_template": True,  # Use raw cybersecurity content
    }
    
    return config

def create_training_script():
    """Create the training script with proper Mamba configuration."""
    
    script_content = '''#!/bin/bash
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
python -m mlx_lm.lora \\
    --model mlx-community/mamba-1.4b-hf \\
    --train \\
    --data cleaned_cybersecurity_dataset.jsonl \\
    --batch-size 4 \\
    --lora-layers 16 \\
    --lora-rank 8 \\
    --lora-alpha 16 \\
    --lora-dropout 0.1 \\
    --learning-rate 1e-4 \\
    --num-epochs 3 \\
    --steps-per-report 100 \\
    --steps-per-eval 500 \\
    --adapter-path ./cybersecurity_mamba_adapter \\
    --save-every 1000 \\
    --max-seq-length 512 \\
    --grad-checkpoint \\
    --warmup-steps 100 \\
    --seed 42 \\
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
test_prompt = 'User: What are the key indicators of a SQL injection vulnerability?\\nAssistant:'
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
'''
    
    return script_content

def main():
    parser = argparse.ArgumentParser(description="Create Mamba cybersecurity fine-tuning configuration")
    parser.add_argument('--output-dir', type=Path, default='.', help='Output directory for config files')
    parser.add_argument('--config-only', action='store_true', help='Only create config, not training script')
    
    args = parser.parse_args()
    
    logger.info("Creating Mamba cybersecurity fine-tuning configuration")
    
    # Create LoRA configuration
    config = create_mamba_lora_config()
    
    # Save configuration
    config_path = args.output_dir / "mamba_lora_config.json"
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    logger.info(f"Saved LoRA configuration to: {config_path}")
    
    if not args.config_only:
        # Create training script
        script_content = create_training_script()
        script_path = args.output_dir / "train_mamba_cybersec.sh"
        
        with open(script_path, 'w') as f:
            f.write(script_content)
        
        # Make script executable
        script_path.chmod(0o755)
        
        logger.info(f"Saved training script to: {script_path}")
    
    # Print configuration summary
    print("\n" + "="*60)
    print("MAMBA CYBERSECURITY FINE-TUNING CONFIGURATION")
    print("="*60)
    print(f"Model: {config['model']}")
    print(f"LoRA Rank: {config['lora_rank']}")
    print(f"LoRA Alpha: {config['lora_alpha']}")
    print(f"Learning Rate: {config['learning_rate']}")
    print(f"Epochs: {config['num_epochs']}")
    print(f"Target Layers: {len(config['lora_targets'])}")
    print("Targeted Components:")
    for target in config['lora_targets']:
        print(f"  - {target}")
    print(f"Adapter Path: {config['adapter_path']}")
    print("="*60)
    
    logger.info("Configuration created successfully!")
    print("\\nNext steps:")
    print("1. Ensure cleaned_cybersecurity_dataset.jsonl exists")
    print("2. Run: ./train_mamba_cybersec.sh")
    print("3. Test the adapter with cybersecurity queries")

if __name__ == '__main__':
    main()
