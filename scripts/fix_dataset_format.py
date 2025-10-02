#!/usr/bin/env python3
"""
Fix MLX-LM Dataset Format
=========================

This script fixes the nested JSON escaping issue in the PRIMUS cybersecurity dataset
and converts it to the proper format expected by MLX-LM for LoRA fine-tuning.

Input format:  {"text": "{\"text\": \"{\\\"text\\\": \\\"actual content\\\"}"}"}
Output format: {"text": "actual content"}
"""

import json
import sys
from pathlib import Path
from tqdm import tqdm

def extract_nested_text(data):
    """
    Extract the actual text content from multiple layers of JSON nesting.
    """
    if not isinstance(data, dict) or 'text' not in data:
        return None
    
    text_content = data['text']
    
    # Keep unwrapping until we get to actual text content (up to 5 layers deep)
    for _ in range(5):
        if not isinstance(text_content, str):
            break
        try:
            # Try to parse as JSON
            parsed = json.loads(text_content)
            if isinstance(parsed, dict) and 'text' in parsed:
                text_content = parsed['text']
            else:
                # If it's not a dict with 'text' key, this is our final content
                break
        except json.JSONDecodeError:
            # If it's not valid JSON, this is our final text content
            break
    
    return text_content

def clean_text_content(text):
    """
    Clean up escaped characters and formatting in the text content.
    """
    if not isinstance(text, str):
        return str(text)
    
    # Remove excessive escaping
    text = text.replace('\\\\n', '\n')
    text = text.replace('\\\\"', '"')
    text = text.replace('\\\\', '\\')
    
    return text

def process_dataset(input_path, output_path):
    """
    Process the dataset file and convert to proper MLX-LM format.
    """
    input_file = Path(input_path)
    output_file = Path(output_path)
    
    if not input_file.exists():
        print(f"Error: Input file {input_file} does not exist!")
        return False
    
    print(f"Processing {input_file} -> {output_file}")
    
    # Count total lines for progress bar
    with open(input_file, 'r', encoding='utf-8') as f:
        total_lines = sum(1 for _ in f)
    
    processed_count = 0
    error_count = 0
    
    with open(input_file, 'r', encoding='utf-8') as infile, \
         open(output_file, 'w', encoding='utf-8') as outfile:
        
        for line_num, line in enumerate(tqdm(infile, total=total_lines, desc="Processing"), 1):
            line = line.strip()
            if not line:
                continue
            
            try:
                # Parse the original JSON
                data = json.loads(line)
                
                # Extract the nested text content
                actual_text = extract_nested_text(data)
                
                if actual_text is None:
                    error_count += 1
                    print(f"Warning: Could not extract text from line {line_num}")
                    continue
                
                # Clean up the text content
                cleaned_text = clean_text_content(actual_text)
                
                # Ensure we have valid content
                if not cleaned_text or len(cleaned_text.strip()) < 10:
                    error_count += 1
                    print(f"Warning: Invalid or too short content on line {line_num}")
                    continue
                
                # Create properly formatted JSON for MLX-LM
                output_data = {"text": cleaned_text}
                
                # Write to output file
                outfile.write(json.dumps(output_data, ensure_ascii=False) + '\n')
                processed_count += 1
                
            except json.JSONDecodeError as e:
                error_count += 1
                print(f"JSON decode error on line {line_num}: {e}")
                continue
            except Exception as e:
                error_count += 1
                print(f"Error processing line {line_num}: {e}")
                continue
    
    print(f"\nProcessing complete!")
    print(f"Successfully processed: {processed_count} lines")
    print(f"Errors encountered: {error_count} lines")
    print(f"Output written to: {output_file}")
    
    return processed_count > 0

def main():
    """Main function to process both train and validation datasets."""
    base_dir = Path("/Users/danielrodrigo/Workspace/PyScience/datasets/primus_training")
    
    datasets_to_process = [
        ("train.jsonl", "train_fixed.jsonl"),
        ("valid.jsonl", "valid_fixed.jsonl")
    ]
    
    all_success = True
    
    for input_name, output_name in datasets_to_process:
        input_path = base_dir / input_name
        output_path = base_dir / output_name
        
        print(f"\n{'='*60}")
        print(f"Processing {input_name}")
        print(f"{'='*60}")
        
        if input_path.exists():
            success = process_dataset(input_path, output_path)
            if not success:
                all_success = False
        else:
            print(f"Skipping {input_name} - file not found")
    
    if all_success:
        print(f"\n{'='*60}")
        print("All datasets processed successfully!")
        print("You can now use train_fixed.jsonl and valid_fixed.jsonl with MLX-LM")
        print(f"{'='*60}")
    else:
        print(f"\n{'='*60}")
        print("Some errors occurred during processing. Check the output above.")
        print(f"{'='*60}")

if __name__ == "__main__":
    main()
