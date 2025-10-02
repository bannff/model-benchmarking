#!/usr/bin/env python3
"""
Create train/validation split for MLX-LM
"""

import json
import random
import os

def create_train_valid_split():
    """Split dataset into train and validation sets"""
    
    # Load the comprehensive dataset
    input_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/comprehensive_cybersecurity_qa.jsonl"
    
    with open(input_file, 'r') as f:
        all_data = [json.loads(line) for line in f]
    
    print(f"📊 Total examples: {len(all_data)}")
    
    # Shuffle the data
    random.seed(42)
    random.shuffle(all_data)
    
    # Split 80/20
    split_idx = int(0.8 * len(all_data))
    train_data = all_data[:split_idx]
    valid_data = all_data[split_idx:]
    
    print(f"🚂 Training examples: {len(train_data)}")
    print(f"✅ Validation examples: {len(valid_data)}")
    
    # Create output directory
    output_dir = "/Users/danielrodrigo/Workspace/PyScience/datasets/clean_training"
    os.makedirs(output_dir, exist_ok=True)
    
    # Save train set
    train_file = os.path.join(output_dir, "train.jsonl")
    with open(train_file, 'w') as f:
        for item in train_data:
            f.write(json.dumps(item) + '\n')
    
    # Save validation set
    valid_file = os.path.join(output_dir, "valid.jsonl")
    with open(valid_file, 'w') as f:
        for item in valid_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"💾 Saved to:")
    print(f"   Train: {train_file}")
    print(f"   Valid: {valid_file}")
    
    return output_dir

if __name__ == "__main__":
    output_dir = create_train_valid_split()
    print(f"\n✅ Dataset prepared for MLX-LM training: {output_dir}")
