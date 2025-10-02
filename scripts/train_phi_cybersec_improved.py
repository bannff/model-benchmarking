#!/usr/bin/env python3
"""
PHI-3.5 Cybersecurity Fine-Tuning Script (Improved)
Using subprocess for better process management and monitoring
"""
import os
import psutil
import subprocess
import threading
import time
import sys

def log_memory():
    """Background thread to log memory usage during training"""
    while True:
        mem = psutil.virtual_memory()
        print(f"[MEMORY LOG] Used: {mem.used / 1e9:.2f}GB, Available: {mem.available / 1e9:.2f}GB, Percent: {mem.percent}%")
        time.sleep(30)  # Log every 30 seconds

def main():
    print("=== PHI-3.5 Cybersecurity Fine-Tuning (Improved) ===")
    memory = psutil.virtual_memory()
    print(f"System memory: {memory.total / 1e9:.1f}GB total, {memory.available / 1e9:.1f}GB available")
    
    # Check if paths exist
    model_path = "/Volumes/Crucial X9/ai-models/Phi-3-mini-128k-instruct-mlx"
    data_path = "/Users/danielrodrigo/Workspace/PyScience/datasets/cybersec_data"
    adapter_path = "/Volumes/Crucial X9/ai-models/PHI-3.5-cybersec-finetune/adapters"
    
    if not os.path.exists(model_path):
        print(f"ERROR: Model path does not exist: {model_path}")
        sys.exit(1)
    if not os.path.exists(data_path):
        print(f"ERROR: Data path does not exist: {data_path}")
        sys.exit(1)
    if not os.path.exists(os.path.dirname(adapter_path)):
        print(f"ERROR: Adapter directory does not exist: {os.path.dirname(adapter_path)}")
        sys.exit(1)
        
    # Start memory monitoring thread
    memory_thread = threading.Thread(target=log_memory, daemon=True)
    memory_thread.start()

    # Build command for PHI fine-tuning using mlx_lm
    cmd = [
        "python3", "-m", "mlx_lm", "lora",
        "--model", model_path,
        "--data", data_path,
        "--train",
        "--batch-size", "2",  # Increased from 1 for M4 Max
        "--iters", "1000",
        "--learning-rate", "2e-4",
        "--steps-per-report", "10",  # Report more frequently
        "--steps-per-eval", "50",    # Evaluate more frequently
        "--save-every", "100",
        "--max-seq-length", "512",
        "--num-layers", "-1",
        "--adapter-path", adapter_path,
        "--grad-checkpoint",
        "--seed", "42",
        "--val-batches", "50",  # Use 50 validation batches
        "-c", "scripts/lora_config.yaml",
    ]
    
    print("\nStarting PHI fine-tuning with MLX LoRA...")
    print("Command:", " ".join(cmd))
    print("\n" + "="*80)
    
    try:
        # Run the training process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Stream output in real-time
        for line in process.stdout:
            print(line.rstrip())
            
        # Wait for completion
        return_code = process.wait()
        
        if return_code == 0:
            print("\n" + "="*80)
            print("Training completed successfully!")
        else:
            print(f"\nTraining failed with return code: {return_code}")
            
    except KeyboardInterrupt:
        print("\nTraining interrupted by user")
        process.terminate()
        return_code = -1
    except Exception as e:
        print(f"Error during training: {e}")
        return_code = -1
        
    return return_code

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
