#!/usr/bin/env python3
"""
Train Mamba 1.4B with clean cybersecurity Q&A data
No hallucinated tools - direct answers only
"""

import subprocess
import sys
import os

def train_clean_mamba():
    """Train Mamba with clean cybersecurity Q&A dataset"""
    
    print("🧹 CLEAN MAMBA CYBERSECURITY TRAINING")
    print("=" * 50)
    print("🎯 Training for direct answers, no hallucinated tools")
    print("📚 Using clean Q&A dataset")
    print("")
    
    # Paths
    model_path = "/Volumes/Crucial X9/ai-models/mamba-models/mamba-1.4b-mlx"
    dataset_path = "/Users/danielrodrigo/Workspace/PyScience/datasets/clean_training"
    adapter_path = "/Volumes/Crucial X9/ai-models/mamba-models/clean_adapters"
    
    # Verify dataset exists
    if not os.path.exists(os.path.join(dataset_path, "train.jsonl")):
        print(f"❌ Training dataset not found: {dataset_path}/train.jsonl")
        return False
    
    # Training parameters - correct MLX-LM syntax
    cmd = [
        "python3", "-m", "mlx_lm", "lora",
        "--model", model_path,
        "--train",
        "--data", dataset_path,
        "--adapter-path", adapter_path,
        "--iters", "1000",  # Fewer iterations for cleaner learning
        "--steps-per-report", "50",
        "--steps-per-eval", "200",
        "--learning-rate", "1e-5",  # Lower learning rate for more stable training
        "--batch-size", "1",
        "--max-seq-length", "2048",
        "--save-every", "200",
        "--test-batches", "10",
        "--seed", "42"
    ]
    
    print("🚀 Starting clean cybersecurity training...")
    print(f"📊 Command: {' '.join(cmd)}")
    print("")
    print("📈 Training Progress:")
    print("-" * 50)
    
    try:
        # Run training
        result = subprocess.run(cmd, check=True, cwd="/Users/danielrodrigo/Workspace/PyScience")
        
        print("\n" + "=" * 50)
        print("✅ CLEAN TRAINING COMPLETED SUCCESSFULLY!")
        print(f"💾 Clean adapters saved to: {adapter_path}")
        print("🎯 Model trained for direct Q&A responses")
        print("🚫 No tool hallucination patterns")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Training failed with error: {e}")
        return False
    except KeyboardInterrupt:
        print("\n⏹️  Training interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = train_clean_mamba()
    if success:
        print("\n🎉 Ready to test clean cybersecurity model!")
        print("💬 Run: python3 mamba_chat.py")
    else:
        print("\n💥 Training failed - check logs above")
        sys.exit(1)
