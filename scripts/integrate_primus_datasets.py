#!/usr/bin/env python3
"""
PRIMUS Dataset Integration Script
Combines PRIMUS-Seed datasets with existing cybersecurity datasets
"""

import json
import tiktoken
from datasets import load_dataset
from pathlib import Path
import random
import os

def count_tokens(text, model_name="gpt-3.5-turbo"):
    """Count tokens using tiktoken"""
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))

def split_text_by_tokens(text, max_tokens=450, model_name="gpt-3.5-turbo"):
    """Split text that exceeds token limit"""
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    
    if len(tokens) <= max_tokens:
        return [text]
    
    # Split into chunks
    chunks = []
    for i in range(0, len(tokens), max_tokens):
        chunk_tokens = tokens[i:i + max_tokens]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
    
    return chunks

def convert_primus_to_messages(primus_sample):
    """Convert PRIMUS sample to messages format"""
    content = primus_sample['content']
    source = primus_sample['source']
    url = primus_sample.get('url', '')
    
    # Create meaningful instruction based on source
    if 'documentation' in source.lower():
        instruction = "Explain this cybersecurity documentation and its key concepts:"
    elif 'wiki' in source.lower():
        instruction = "Summarize this cybersecurity knowledge and explain its significance:"
    elif 'conformity' in source.lower():
        instruction = "Analyze this security compliance information:"
    elif 'solution' in source.lower():
        instruction = "Explain this cybersecurity solution and its implementation:"
    else:
        instruction = "Analyze this cybersecurity content and provide insights:"
    
    # Add source context
    if url:
        instruction += f"\n\nSource: {source} ({url})"
    else:
        instruction += f"\n\nSource: {source}"
    
    return [
        {"role": "user", "content": instruction},
        {"role": "assistant", "content": content}
    ]

def load_existing_dataset():
    """Load our existing consolidated dataset"""
    dataset_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/dataset.jsonl"
    
    if not Path(dataset_file).exists():
        print(f"⚠️  Existing dataset not found: {dataset_file}")
        return []
    
    samples = []
    with open(dataset_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                data = json.loads(line.strip())
                samples.append(data)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error loading line {line_num}: {e}")
                continue
    
    print(f"📂 Loaded {len(samples):,} existing samples")
    return samples

def process_primus_datasets():
    """Process all PRIMUS datasets and convert to messages format"""
    os.environ['HF_TOKEN'] = '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'
    
    primus_configs = [
        'default',
        'cybersecurity_companies_websites',
        'cybersecurity_wikis'
    ]
    
    all_primus_samples = []
    
    for config in primus_configs:
        print(f"📥 Processing PRIMUS-Seed config: {config}")
        
        try:
            dataset = load_dataset('trendmicro-ailab/Primus-Seed', config, split='train')
            
            config_samples = []
            token_split_count = 0
            
            for i, sample in enumerate(dataset):
                try:
                    # Convert to messages format
                    messages = convert_primus_to_messages(sample)
                    
                    # Check token limits and split if needed
                    user_tokens = count_tokens(messages[0]['content'])
                    assistant_tokens = count_tokens(messages[1]['content'])
                    
                    # Split assistant content if too long (user content is usually short instruction)
                    if assistant_tokens > 450:
                        chunks = split_text_by_tokens(messages[1]['content'], max_tokens=450)
                        token_split_count += 1
                        
                        # Create multiple samples from chunks
                        for chunk in chunks:
                            config_samples.append({
                                "messages": [
                                    messages[0],  # Same instruction
                                    {"role": "assistant", "content": chunk}
                                ]
                            })
                    else:
                        config_samples.append({"messages": messages})
                        
                except Exception as e:
                    print(f"Error processing sample {i}: {e}")
                    continue
            
            print(f"   ✅ Processed {len(config_samples):,} samples from {config}")
            print(f"   📊 Token splits: {token_split_count}")
            all_primus_samples.extend(config_samples)
            
        except Exception as e:
            print(f"   ❌ Failed to process {config}: {e}")
    
    print(f"\n🎯 Total PRIMUS samples: {len(all_primus_samples):,}")
    return all_primus_samples

def main():
    print("=== PRIMUS Dataset Integration ===")
    print("Combining PRIMUS-Seed with existing cybersecurity datasets...\n")
    
    # Step 1: Load existing dataset
    print("1. Loading existing dataset...")
    existing_samples = load_existing_dataset()
    
    # Step 2: Process PRIMUS datasets
    print("\n2. Processing PRIMUS-Seed datasets...")
    primus_samples = process_primus_datasets()
    
    # Step 3: Combine datasets
    print(f"\n3. Combining datasets...")
    combined_samples = existing_samples + primus_samples
    
    print(f"📊 Dataset Composition:")
    print(f"   - Existing: {len(existing_samples):,} samples")
    print(f"   - PRIMUS: {len(primus_samples):,} samples")
    print(f"   - Combined: {len(combined_samples):,} samples")
    
    # Step 4: Shuffle and split
    print(f"\n4. Shuffling and creating train/validation split...")
    random.shuffle(combined_samples)
    
    split_idx = int(len(combined_samples) * 0.9)
    train_samples = combined_samples[:split_idx]
    val_samples = combined_samples[split_idx:]
    
    print(f"   - Training: {len(train_samples):,} samples")
    print(f"   - Validation: {len(val_samples):,} samples")
    
    # Step 5: Save enhanced dataset
    print(f"\n5. Saving enhanced dataset...")
    
    # Save training set
    train_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/dataset_with_primus.jsonl"
    with open(train_file, 'w', encoding='utf-8') as f:
        for sample in train_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    # Save validation set
    val_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/dataset_validation_with_primus.jsonl"
    with open(val_file, 'w', encoding='utf-8') as f:
        for sample in val_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"✅ Enhanced dataset saved:")
    print(f"   📁 Training: {train_file}")
    print(f"   📁 Validation: {val_file}")
    
    # Step 6: Convert to MLX format for training
    print(f"\n6. Converting to MLX format...")
    
    mlx_train_samples = []
    mlx_val_samples = []
    
    # Convert training samples
    for sample in train_samples:
        messages = sample["messages"]
        user_content = ""
        assistant_content = ""
        
        for message in messages:
            if message["role"] == "user":
                user_content = message["content"]
            elif message["role"] == "assistant":
                assistant_content = message["content"]
        
        if user_content and assistant_content:
            mlx_train_samples.append({"text": f"User: {user_content}\n\nAssistant: {assistant_content}"})
    
    # Convert validation samples
    for sample in val_samples:
        messages = sample["messages"]
        user_content = ""
        assistant_content = ""
        
        for message in messages:
            if message["role"] == "user":
                user_content = message["content"]
            elif message["role"] == "assistant":
                assistant_content = message["content"]
        
        if user_content and assistant_content:
            mlx_val_samples.append({"text": f"User: {user_content}\n\nAssistant: {assistant_content}"})
    
    # Save MLX format
    mlx_train_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/dataset_mlx_with_primus.jsonl"
    mlx_val_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/dataset_validation_mlx_with_primus.jsonl"
    
    with open(mlx_train_file, 'w', encoding='utf-8') as f:
        for sample in mlx_train_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    with open(mlx_val_file, 'w', encoding='utf-8') as f:
        for sample in mlx_val_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"✅ MLX format saved:")
    print(f"   📁 Training: {mlx_train_file}")
    print(f"   📁 Validation: {mlx_val_file}")
    
    # Step 7: Sample verification
    print(f"\n7. Verifying enhanced dataset...")
    
    if len(train_samples) > 0:
        sample = train_samples[0]
        print("Sample enhanced entry:")
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:800] + "...")
        
        # Token count verification
        messages = sample["messages"]
        for i, message in enumerate(messages):
            token_count = count_tokens(message["content"])
            print(f"Message {i+1} ({message['role']}): {token_count} tokens")
    
    print(f"\n🎉 Enhanced Dataset Ready!")
    print(f"Successfully integrated PRIMUS-Seed datasets!")
    print(f"📊 Final size: {len(combined_samples):,} total samples")
    print(f"🚀 Ready for training with LoRA alpha=128")

if __name__ == "__main__":
    main()
