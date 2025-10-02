#!/usr/bin/env python3
"""
FINAL MAMBA CYBERSECURITY TRAINING CONFIGURATION
Optimized for high-quality cleaned dataset
"""

import yaml
import os

def create_final_mamba_config():
    """Create final Mamba training configuration for cleaned dataset"""
    
    config = {
        "model": "/Volumes/Crucial X9/ai-models/mamba-models/mamba-1.4b-mlx",
        "train": True,
        "data": "datasets/cybersec_training",  # Directory with train/valid split
        "save_every": 1000,
        "val_batches": 25,
        "learning_rate": 2e-5,  # Lower LR for quality data
        "batch_size": 1,
        "iters": 5000,  # More iterations for better learning
        "val_loss_patience": 10,
        "adapter_path": "adapters",
        "use_dora": False,
        "lora_layers": -1,  # ALL LAYERS - following general ML principles
        "lora_parameters": {
            "rank": 8,
            "scale": 16,
            "dropout": 0.1
        },
        "resume_adapter_file": None,
        "test": False,
        "test_batches": 50,
        "max_seq_length": 512,
        "grad_checkpoint": True
    }
    
    # Save configuration as YAML
    with open('mamba_cybersec_project/configs/final_mamba_config.yaml', 'w') as f:
        yaml.dump(config, f, sort_keys=False)
    
    print("✅ Created final Mamba configuration")
    return config

def create_training_script():
    """Create optimized training script"""
    script_content = '''#!/bin/bash
# FINAL MAMBA CYBERSECURITY TRAINING
# High-quality dataset with optimized Mamba configuration

set -e

echo "🐍 FINAL MAMBA CYBERSECURITY TRAINING"
echo "====================================="

# Validate dataset exists
if [ ! -f "datasets/cybersec_training/train.jsonl" ]; then
    echo "❌ Clean dataset not found! Check datasets directory."
    exit 1
fi

# Count entries
ENTRIES=$(wc -l < datasets/cybersec_training/train.jsonl)
echo "📊 Training dataset: $ENTRIES entries"

# Check for existing adapters
if [ -d "adapters" ]; then
    echo "🔄 Found existing adapters - this will resume training"
    read -p "Continue? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Aborting..."
        exit 1
    fi
else
    echo "🆕 Starting fresh training with cleaned dataset"
fi

# Start training with optimized configuration
echo "🚀 Starting Mamba fine-tuning..."
echo "⚙️  Model: /Volumes/Crucial X9/ai-models/mamba-models/mamba-1.4b-mlx"
echo "🎯 Target: Cybersecurity specialization"
echo "📈 Configuration: Final optimized settings"
echo ""

python3 -m mlx_lm lora \\
  -c mamba_cybersec_project/configs/final_mamba_config.yaml

echo ""
echo "✅ Training completed!"
echo "🧠 Adapters saved to: adapters/"
echo "🚀 Ready to test cybersecurity model!"
'''
    
    with open('final_train_mamba_cybersec.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('final_train_mamba_cybersec.sh', 0o755)
    print("✅ Created final training script")

def main():
    print("🎯 CREATING FINAL MAMBA TRAINING CONFIGURATION")
    print("=" * 60)
    
    # Ensure directories exist
    os.makedirs('mamba_cybersec_project/configs', exist_ok=True)
    
    # Create configuration
    config = create_final_mamba_config()
    
    # Create training script
    create_training_script()
    
    print(f"\n📋 CONFIGURATION SUMMARY:")
    print(f"Model: {config['model']}")
    print(f"Learning Rate: {config['learning_rate']}")
    print(f"Iterations: {config['iters']}")
    print(f"LoRA Rank: {config['lora_parameters']['rank']}")
    print(f"Target Layers: ALL LAYERS (-1)")
    
    print(f"\n🎯 NEXT STEPS:")
    print(f"1. Dataset ready: datasets/cybersec_training/")
    print(f"2. Run: ./final_train_mamba_cybersec.sh")
    print(f"3. Test with: python3 mamba_chat.py")

if __name__ == "__main__":
    main()
