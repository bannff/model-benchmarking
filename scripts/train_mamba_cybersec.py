#!/usr/bin/env python3
"""
Minimal MLX-LM Mamba Training Launcher
Launches MLX-LM LoRA training with config-driven parameters.
"""

import json
import subprocess
import sys
import os
from pathlib import Path

def main():
    # Load config
    config_path = "mamba_lora_config.json"
    if not Path(config_path).exists():
        print(f"Config file not found: {config_path}")
        sys.exit(1)
    with open(config_path, 'r') as f:
        cfg = json.load(f)

    # Required parameters
    model = cfg.get("model", "mlx-community/mamba-1.4b-mlx")
    # Always use the absolute path to the local dataset file
    data = os.path.abspath(cfg.get("data", "datasets/train.jsonl"))
    adapter_path = cfg.get("adapter_path", "./adapters")
    batch_size = str(cfg.get("batch_size", 4))
    lora_rank = str(cfg.get("lora_rank", 8))
    lora_alpha = str(cfg.get("lora_alpha", 16))
    lora_dropout = str(cfg.get("lora_dropout", 0.1))
    learning_rate = str(cfg.get("learning_rate", 1e-4))
    iters = str(cfg.get("iters", 1000))
    save_every = str(cfg.get("save_every", 200))
    max_seq_length = str(cfg.get("max_seq_length", 512))

    # Build command (no Hugging Face dataset logic, only local file)
    cmd = [
        "python3", "-m", "mlx_lm.lora",
        "--model", model,
        "--train",
        "--data", data,
        "--adapter-path", adapter_path,
        "--iters", iters,
        "--steps-per-report", "50",
        "--steps-per-eval", "200",
        "--learning-rate", learning_rate,
        "--batch-size", batch_size,
        "--max-seq-length", max_seq_length,
        "--save-every", save_every,
        "--seed", "42"
    ]

    print("\n🚀 Launching MLX-LM Mamba training with:")
    print(" ", " ".join(cmd))
    print()
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Training failed: {e}")
        sys.exit(1)
    print("\n✅ Training completed!")

if __name__ == "__main__":
    main()
            