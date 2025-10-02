#!/usr/bin/env python3
"""
Final MLX-LM Dataset Fixer
=========================

This script will completely unwrap the nested JSON and create proper MLX-LM format.
"""

import json
import re
from pathlib import Path
from tqdm import tqdm

def extract_final_content(text_content):
    """
    Extract the actual content from deeply nested JSON text field.
    Handles malformed/truncated JSON by extracting content manually.
    """
    if not isinstance(text_content, str):
        return str(text_content)
    
    # First try standard JSON parsing
    current = text_content
    for _ in range(10):
        try:
            parsed = json.loads(current)
            if isinstance(parsed, dict) and 'text' in parsed:
                current = parsed['text']
            else:
                break
        except json.JSONDecodeError:
            break
    
    # If we still have nested JSON patterns, extract manually
    if current.startswith('{"text": "'):
        # Look for the pattern: {"text": "actual content here"}
        # But handle the case where the JSON might be malformed
        
        # Find the start of the actual content
        match = re.search(r'{"text":\s*"([^"]+)"', current)
        if match:
            # Extract the content and clean escape sequences
            content = match.group(1)
            content = content.replace('\\n', '\n')
            content = content.replace('\\t', '\t')
            content = content.replace('\\"', '"')
            content = content.replace('\\\\', '\\')
            return content
        
        # Alternative: try to find content after the last "text": " pattern
        if '"text": "' in current:
            parts = current.split('"text": "')
            if len(parts) > 1:
                # Get the last part and extract until the first quote or end
                last_part = parts[-1]
                # Find the actual content
                content_match = re.match(r'([^"]*)', last_part)
                if content_match:
                    content = content_match.group(1)
                    content = content.replace('\\n', '\n')
                    content = content.replace('\\t', '\t')
                    content = content.replace('\\"', '"')
                    content = content.replace('\\\\', '\\')
                    return content
    
    # If all else fails, return cleaned version of what we have
    cleaned = current.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"').replace('\\\\', '\\')
    return cleaned

def process_final_dataset(input_path, output_path):
    """Process dataset with final extraction method."""
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        print(f"Error: {input_file} does not exist!")
        return False
    
    print(f"Final processing: {input_file} -> {output_file}")
    
    # Count lines
    with open(input_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    processed = 0
    errors = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(tqdm(infile, total=total_lines, desc="Final cleanup"), 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse the line
                data = json.loads(line)
                
                if 'text' not in data:
                    errors += 1
                    continue
                
                # Extract final content
                final_content = extract_final_content(data['text'])
                
                # Validate result
                if not final_content or len(final_content.strip()) < 10:
                    errors += 1
                    continue
                
                # Create clean output
                clean_data = {"text": final_content}
                
                # Write to output
                outfile.write(json.dumps(clean_data, ensure_ascii=False) + '\n')
                processed += 1
                
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"Error on line {line_num}: {e}")
                continue
    
    print(f"Final processed: {processed} lines")
    print(f"Final errors: {errors} lines")
    return processed > 0

def main():
    base_dir = Path("/Users/danielrodrigo/Workspace/PyScience/datasets/primus_training")
    
    # Use the previously created clean files as input
    files_to_process = [
        ("train_clean.jsonl", "train_final.jsonl"),
        ("valid_clean.jsonl", "valid_final.jsonl")
    ]
    
    print("Final MLX-LM Dataset Cleanup")
    print("=" * 50)
    
    for input_name, output_name in files_to_process:
        input_path = base_dir / input_name
        output_path = base_dir / output_name
        
        if input_path.exists():
            print(f"\nFinal cleanup of {input_name}...")
            success = process_final_dataset(input_path, output_path)
            
            if success:
                print(f"✅ Successfully created {output_name}")
            else:
                print(f"❌ Failed to process {input_name}")
        else:
            print(f"⚠️  {input_name} not found, skipping")
    
    print("\n" + "=" * 50)
    print("Final dataset cleanup complete!")
    print("Use train_final.jsonl and valid_final.jsonl with MLX-LM")

if __name__ == "__main__":
    main()
