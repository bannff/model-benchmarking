#!/usr/bin/env python3
import json
from tqdm import tqdm

input_path = "datasets/mlx_full_dataset/cybersecurity_ner_processed/train_minimal_prompt_completion.jsonl"
output_path = "models/tinyllama_ner_lora_minimal/mlx_train_data.jsonl"

with open(input_path, "r") as infile, open(output_path, "w") as outfile:
    for line in tqdm(infile, desc="Converting to MLX-LM tuple JSONL"):
        data = json.loads(line)
        prompt = data.get("prompt", "").strip()
        completion = data.get("completion", "").strip()
        # Write as a JSON array (tuple)
        outfile.write(json.dumps([prompt, completion]) + "\n")
