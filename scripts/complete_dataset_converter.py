#!/usr/bin/env python3
"""
Complete MLX-LM Dataset Converter
=================================

This script completely fixes the nested JSON format for MLX-LM compatibility.
"""

import json
import re
from pathlib import Path
from tqdm import tqdm

def completely_unwrap_text(text_field):
    """
    Completely unwrap all layers of JSON nesting and extract clean text.
    """
    if not isinstance(text_field, str):
        return str(text_field)
    
    current = text_field
    
    # Try up to 10 levels of unwrapping
    for attempt in range(10):
        try:
            # Try to parse as JSON
            parsed = json.loads(current)
            if isinstance(parsed, dict) and 'text' in parsed:
                current = parsed['text']
                continue
            else:
                # Not a dict with 'text', we're done
                break
        except (json.JSONDecodeError, TypeError):
            # Not valid JSON, we're done
            break
    
    # At this point, current should be the final text content
    # Clean up any remaining escape sequences
    if isinstance(current, str):
        # Remove excessive escaping
        current = current.replace('\\\\n', '\n')
        current = current.replace('\\\\t', '\t')
        current = current.replace('\\\\r', '\r')
        current = current.replace('\\\\"', '"')
        current = current.replace("\\\\'", "'")
        current = current.replace('\\\\\\\\', '\\\\')
        
        # Clean up any remaining double escapes
        current = current.replace('\\n', '\n')
        current = current.replace('\\t', '\t')
        current = current.replace('\\r', '\r')
        current = current.replace('\\"', '"')
        current = current.replace("\\'", "'")
    
    return current

def process_complete_dataset(input_path, output_path):
    """Process dataset with complete unwrapping."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        print(f"Error: {input_file} does not exist!")
        return False
    
    print(f"Processing: {input_file} -> {output_file}")
    
    # Count lines
    with open(input_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    processed = 0
    errors = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(tqdm(infile, total=total_lines, desc="Converting"), 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse the line
                data = json.loads(line)
                
                if 'text' not in data:
                    errors += 1
                    continue
                
                # Completely unwrap the text content
                final_text = completely_unwrap_text(data['text'])
                
                # Validate result
                if not final_text or len(final_text.strip()) < 10:
                    errors += 1
                    continue
                
                # Create clean output
                clean_data = {"text": final_text}
                
                # Write to output
                outfile.write(json.dumps(clean_data, ensure_ascii=False) + '\n')
                processed += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:  # Only show first 5 errors
                    print(f"Error on line {line_num}: {e}")
                continue
    
    print(f"Processed: {processed} lines")
    print(f"Errors: {errors} lines")
    return processed > 0

def main():
    base_dir = Path("/Users/danielrodrigo/Workspace/PyScience/datasets/primus_training")
    
    files_to_process = [
        ("train.jsonl", "train_clean.jsonl"),
        ("valid.jsonl", "valid_clean.jsonl")
    ]
    
    print("MLX-LM Dataset Converter")
    print("=" * 50)
    
    for input_name, output_name in files_to_process:
        input_path = base_dir / input_name
        output_path = base_dir / output_name
        
        print(f"\nProcessing {input_name}...")
        success = process_complete_dataset(input_path, output_path)
        
        if success:
            print(f"✅ Successfully created {output_name}")
        else:
            print(f"❌ Failed to process {input_name}")
    
    print("\n" + "=" * 50)
    print("Dataset conversion complete!")
    print("Use train_clean.jsonl and valid_clean.jsonl with MLX-LM")

if __name__ == "__main__":
    main()
