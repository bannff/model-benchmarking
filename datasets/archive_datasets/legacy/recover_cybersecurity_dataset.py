#!/usr/bin/env python3
"""
Recovery Script: Rebuild Cybersecurity Training Dataset
Fixes the broken training by recreating cybersecurity dataset from intact sources
"""

import json
import tiktoken
from pathlib import Path
import random

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

def convert_to_messages_format(data, instruction_key="instruction", input_key="input", output_key="output"):
    """Convert various formats to messages format"""
    if "messages" in data:
        return data["messages"]
    
    # Handle instruction/input/output format
    if instruction_key in data and output_key in data:
        user_content = data[instruction_key]
        if input_key in data and data[input_key].strip():
            user_content += f"\n\n{data[input_key]}"
        
        return [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": data[output_key]}
        ]
    
    # Handle text format (convert to Q&A)
    if "text" in data:
        # Simple text - treat as assistant response to general cybersecurity question
        return [
            {"role": "user", "content": "Explain this cybersecurity concept:"},
            {"role": "assistant", "content": data["text"]}
        ]
    
    return None

def process_current_enhanced_dataset():
    """Process the current enhanced cybersecurity dataset to fix token issues"""
    
    # Load our current enhanced dataset
    input_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/enhanced_cybersec_training_data.jsonl"
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found!")
        return []
    
    print(f"Processing current enhanced dataset: {input_file}")
    
    samples = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f):
            try:
                data = json.loads(line.strip())
                if "messages" in data:
                    samples.append(data)
            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error processing line {line_num}: {e}")
                continue
    
    print(f"Loaded {len(samples)} samples from enhanced dataset")
    return samples

def apply_token_limits(samples, max_tokens=450):
    """Apply token limits to prevent truncation"""
    fixed_samples = []
    truncated_count = 0
    split_count = 0
    
    for sample in samples:
        messages = sample["messages"]
        
        # Check each message for token count
        fixed_messages = []
        for message in messages:
            content = message["content"]
            token_count = count_tokens(content)
            
            if token_count > max_tokens:
                # Split long content
                chunks = split_text_by_tokens(content, max_tokens)
                
                if len(chunks) > 1:
                    split_count += 1
                    # Use first chunk and note truncation
                    fixed_messages.append({
                        "role": message["role"],
                        "content": chunks[0]
                    })
                else:
                    fixed_messages.append(message)
            else:
                fixed_messages.append(message)
        
        # Create new sample with fixed messages
        if fixed_messages:
            fixed_samples.append({"messages": fixed_messages})
    
    print(f"Token limiting stats:")
    print(f"- Original samples: {len(samples)}")
    print(f"- Fixed samples: {len(fixed_samples)}")
    print(f"- Messages split: {split_count}")
    
    return fixed_samples

def convert_to_mlx_tuple_format(samples):
    """Convert to MLX tuple format (input, target) for training"""
    mlx_tuples = []
    
    for sample in samples:
        messages = sample["messages"]
        
        # Extract user and assistant messages
        user_content = ""
        assistant_content = ""
        
        for message in messages:
            if message["role"] == "user":
                user_content = message["content"]
            elif message["role"] == "assistant":
                assistant_content = message["content"]
        
        if user_content and assistant_content:
            # Create tuple (input, target) as MLX expects
            mlx_tuples.append((user_content, assistant_content))
    
    return mlx_tuples

def main():
    print("=== Enhanced Dataset Token Fixing ===")
    print("Fixing token length issues in enhanced cybersecurity dataset...")
    
    # Step 1: Process current enhanced dataset
    print("\n1. Loading enhanced cybersecurity dataset...")
    samples = process_current_enhanced_dataset()
    print(f"Total samples loaded: {len(samples)}")
    
    if len(samples) == 0:
        print("ERROR: No samples found!")
        return
    
    # Step 2: Apply token limits
    print("\n2. Applying token limits to prevent truncation...")
    fixed_samples = apply_token_limits(samples, max_tokens=450)
    
    # Step 3: Save messages format dataset
    print("\n3. Saving token-limited dataset...")
    output_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/enhanced_cybersec_training_token_limited.jsonl"
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in fixed_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"✅ Saved {len(fixed_samples)} token-limited samples to: {output_file}")
    
    # Step 4: Convert to MLX tuple format
    print("\n4. Converting to MLX tuple format...")
    mlx_tuples = convert_to_mlx_tuple_format(fixed_samples)
    
    # Step 5: Save MLX tuple format
    mlx_output = "/Users/danielrodrigo/Workspace/PyScience/datasets/enhanced_cybersec_training_mlx_tuples.jsonl"
    with open(mlx_output, 'w', encoding='utf-8') as f:
        for input_text, target_text in mlx_tuples:
            # Save as tuple format that MLX expects
            f.write(json.dumps([input_text, target_text], ensure_ascii=False) + '\n')
    
    print(f"✅ Saved MLX tuple format to: {mlx_output}")
    
    # Step 6: Create validation split (10%)
    print("\n5. Creating validation split...")
    split_idx = int(len(fixed_samples) * 0.9)
    train_samples = fixed_samples[:split_idx]
    val_samples = fixed_samples[split_idx:]
    
    # Convert validation to tuple format too
    val_tuples = convert_to_mlx_tuple_format(val_samples)
    val_mlx_output = "/Users/danielrodrigo/Workspace/PyScience/datasets/enhanced_cybersec_validation_mlx_tuples.jsonl"
    with open(val_mlx_output, 'w', encoding='utf-8') as f:
        for input_text, target_text in val_tuples:
            f.write(json.dumps([input_text, target_text], ensure_ascii=False) + '\n')
    
    # Save validation set
    val_output = "/Users/danielrodrigo/Workspace/PyScience/datasets/enhanced_cybersec_validation_token_limited.jsonl"
    with open(val_output, 'w', encoding='utf-8') as f:
        for sample in val_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"✅ Training samples: {len(train_samples)}")
    print(f"✅ Validation samples: {len(val_samples)}")
    print(f"✅ Validation file: {val_output}")
    
    print(f"\n🎉 Token-limited dataset ready for training!")
    print(f"📁 Use: {output_file}")
    print(f"📁 Validation: {val_output}")
    output_file = "/Users/danielrodrigo/Workspace/PyScience/datasets/cybersecurity_training_recovered.jsonl"
    print(f"\n3. Saving recovered dataset to {output_file}...")
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for sample in fixed_samples:
            f.write(json.dumps(sample, ensure_ascii=False) + '\n')
    
    print(f"Saved {len(fixed_samples)} cybersecurity training samples")
    
    # Step 4: Convert to MLX tuple format for old recovery path too
    print("\n4. Converting to MLX tuple format...")
    mlx_tuples = convert_to_mlx_tuple_format(fixed_samples)
    
    # Split for training/validation (90/10)
    random.shuffle(mlx_tuples)
    split_idx = int(len(mlx_tuples) * 0.9)
    train_tuples = mlx_tuples[:split_idx]
    valid_tuples = mlx_tuples[split_idx:]
    
    # Save MLX training data
    mlx_dir = Path("/Users/danielrodrigo/Workspace/PyScience/datasets/mlx_training_data")
    mlx_dir.mkdir(exist_ok=True)
    
    train_file = mlx_dir / "train.jsonl"
    valid_file = mlx_dir / "valid.jsonl"
    
    with open(train_file, 'w', encoding='utf-8') as f:
        for input_text, target_text in train_tuples:
            f.write(json.dumps([input_text, target_text], ensure_ascii=False) + '\n')
    
    with open(valid_file, 'w', encoding='utf-8') as f:
        for input_text, target_text in valid_tuples:
            f.write(json.dumps([input_text, target_text], ensure_ascii=False) + '\n')
    
    print(f"MLX Format:")
    print(f"- Training samples: {len(train_tuples)}")
    print(f"- Validation samples: {len(valid_tuples)}")
    print(f"- Train file: {train_file}")
    print(f"- Valid file: {valid_file}")
    
    # Step 5: Sample verification
    print("\n5. Verifying dataset quality...")
    if len(train_samples) > 0:
        sample = train_samples[0]
        print("Sample training entry:")
        print(json.dumps(sample, indent=2, ensure_ascii=False)[:500] + "...")
        
        # Token count verification
        token_count = count_tokens(sample["text"])
        print(f"Sample token count: {token_count}")
    
    print(f"\n=== Recovery Complete ===")
    print(f"Successfully recovered {len(fixed_samples)} cybersecurity training samples")
    print("Training can now be resumed with proper cybersecurity content!")

if __name__ == "__main__":
    main()
