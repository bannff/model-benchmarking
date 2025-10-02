#!/usr/bin/env python3
"""
Data Cleaner: Fix newline artifacts and formatting issues
"""

import json
import os
import re
from tqdm import tqdm

def clean_formatting(text):
    """Fix common formatting issues that cause \\n artifacts"""
    if not isinstance(text, str):
        return text
    
    # Fix literal \\n characters that should be actual newlines
    text = text.replace('\\n', '\n')
    
    # Fix excessive whitespace
    text = re.sub(r'\n+', '\n', text)  # Multiple newlines -> single
    text = re.sub(r' +', ' ', text)    # Multiple spaces -> single
    
    # Remove trailing/leading whitespace
    text = text.strip()
    
    # Fix common formatting artifacts
    text = text.replace('\\t', '\t')
    text = text.replace('\\"', '"')
    
    return text

def clean_jsonl_file(input_path, output_path):
    """Clean a JSONL file to fix formatting issues"""
    print(f"🧹 Cleaning {input_path}...")
    
    cleaned_count = 0
    total_count = 0
    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in tqdm(infile, desc="Cleaning"):
            try:
                data = json.loads(line.strip())
                total_count += 1
                
                # Clean messages if they exist
                if 'messages' in data:
                    for message in data['messages']:
                        if 'content' in message:
                            original_content = message['content']
                            cleaned_content = clean_formatting(original_content)
                            
                            if cleaned_content != original_content:
                                cleaned_count += 1
                            
                            message['content'] = cleaned_content
                
                # Write cleaned data
                outfile.write(json.dumps(data) + '\n')
                
            except json.JSONDecodeError:
                print(f"⚠️  Skipping invalid JSON line")
                continue
    
    print(f"✅ Cleaned {cleaned_count}/{total_count} entries")
    return cleaned_count, total_count

def main():
    """Clean existing training data"""
    
    # Find existing training files
    base_dir = "/Users/danielrodrigo/Workspace/PyScience/datasets"
    
    files_to_clean = [
        "cybersecurity_datasets/processed/heimdall_merged_cleaned.jsonl",
        "cybersecurity_datasets/processed/cybersecurity_agentic_clean_train.jsonl",
        "cybersecurity_datasets/processed/vanessa_cybersec_32k.jsonl"
    ]
    
    print("🚀 Starting Data Cleaning Process")
    print("=" * 50)
    
    total_cleaned = 0
    total_processed = 0
    
    for relative_path in files_to_clean:
        input_path = os.path.join(base_dir, relative_path)
        
        if os.path.exists(input_path):
            # Create cleaned version
            dir_name = os.path.dirname(input_path)
            base_name = os.path.basename(input_path)
            name_without_ext = os.path.splitext(base_name)[0]
            output_path = os.path.join(dir_name, f"{name_without_ext}_formatted_clean.jsonl")
            
            cleaned, total = clean_jsonl_file(input_path, output_path)
            total_cleaned += cleaned
            total_processed += total
            
            print(f"📁 Output: {output_path}")
            print("-" * 30)
        else:
            print(f"⚠️  File not found: {input_path}")
    
    print(f"\\n✅ Cleaning Complete!")
    print(f"📊 Total entries processed: {total_processed}")
    print(f"🧹 Total entries cleaned: {total_cleaned}")
    print(f"📈 Improvement rate: {(total_cleaned/total_processed)*100:.1f}%")

if __name__ == "__main__":
    main()
