#!/usr/bin/env python3
"""
Robust MLX-LM Dataset Converter
==============================

This script handles the complex nested JSON structure with proper escaping.
"""

import json
import re
from pathlib import Path
from tqdm import tqdm

def safe_json_loads(text):
    """Safely load JSON with better error handling."""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to fix common issues
        # Fix unescaped control characters
        fixed = text.replace('\n', '\\n').replace('\t', '\\t').replace('\r', '\\r')
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return None

def extract_deepest_text(data):
    """Extract the deepest text content from nested JSON structure."""
    if not isinstance(data, dict) or 'text' not in data:
        return None
    
    current = data['text']
    
    # Keep trying to unwrap
    for depth in range(10):  # Max 10 levels
        if not isinstance(current, str):
            break
            
        # Try to parse as JSON
        parsed = safe_json_loads(current)
        if parsed is None:
            # Not valid JSON, this is our final text
            break
            
        if isinstance(parsed, dict) and 'text' in parsed:
            current = parsed['text']
        else:
            # Not a text dict, stop here
            current = str(parsed) if parsed is not None else current
            break
    
    # Clean up the final text
    if isinstance(current, str):
        # Unescape common sequences
        current = current.replace('\\\\n', '\n')
        current = current.replace('\\\\t', '\t') 
        current = current.replace('\\\\r', '\r')
        current = current.replace('\\\\"', '"')
        current = current.replace("\\\\'", "'")
        current = current.replace('\\\\\\\\', '\\\\')
        
        # Second pass for any remaining
        current = current.replace('\\n', '\n')
        current = current.replace('\\t', '\t')
        current = current.replace('\\r', '\r')
        current = current.replace('\\"', '"')
        current = current.replace("\\'", "'")
    
    return current

def create_mlx_dataset(input_path, output_path):
    """Create properly formatted MLX-LM dataset."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        print(f"❌ Input file not found: {input_file}")
        return False
    
    print(f"Converting: {input_file.name} → {output_file.name}")
    
    # Count total lines
    with open(input_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    processed_count = 0
    error_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(tqdm(infile, total=total_lines, desc="Converting"), 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse the line
                data = json.loads(line)
                
                # Extract the deepest text content
                final_text = extract_deepest_text(data)
                
                if final_text is None or len(final_text.strip()) < 10:
                    error_count += 1
                    continue
                
                # Create proper MLX-LM format
                mlx_data = {"text": final_text}
                
                # Write to output
                outfile.write(json.dumps(mlx_data, ensure_ascii=False) + '\n')
                processed_count += 1
                
            except Exception as e:
                error_count += 1
                if error_count <= 3:
                    print(f"Error on line {line_num}: {e}")
                continue
    
    success_rate = (processed_count / total_lines) * 100 if total_lines > 0 else 0
    print(f"✅ Processed: {processed_count:,} lines ({success_rate:.1f}%)")
    print(f"⚠️  Errors: {error_count:,} lines")
    
    return processed_count > 0

def main():
    """Main conversion function."""
    print("🚀 MLX-LM Dataset Converter")
    print("=" * 60)
    
    base_dir = Path("/Users/danielrodrigo/Workspace/PyScience/datasets/primus_training")
    
    datasets = [
        ("train.jsonl", "train_mlx.jsonl"),
        ("valid.jsonl", "valid_mlx.jsonl")
    ]
    
    all_success = True
    
    for input_name, output_name in datasets:
        input_path = base_dir / input_name
        output_path = base_dir / output_name
        
        print(f"\n📁 Processing {input_name}")
        print("-" * 40)
        
        if input_path.exists():
            success = create_mlx_dataset(input_path, output_path)
            if not success:
                all_success = False
        else:
            print(f"❌ File not found: {input_name}")
            all_success = False
    
    print("\n" + "=" * 60)
    if all_success:
        print("🎉 Conversion completed successfully!")
        print("📁 Use train_mlx.jsonl and valid_mlx.jsonl with MLX-LM")
    else:
        print("⚠️  Some conversions failed. Check the output above.")
    print("=" * 60)

if __name__ == "__main__":
    main()
