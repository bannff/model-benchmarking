#!/usr/bin/env python3
"""
Enhanced Cybersecurity Dataset Collector
Downloads and processes high-quality cybersecurity datasets for improved training
"""

import os
import json
import re
import sys
import argparse
import hashlib
import tiktoken
from datasets import load_dataset
from tqdm import tqdm

# --- Raw Dataset Download/Verification Logic ---
DATASET_INFO = {
    "CICIDS2017": {
        "url": "https://www.unb.ca/cic/datasets/malmem-2020-02-25.zip",
        "sha256": "8c8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e",
        "file_name": "malmem-2020-02-25.zip",
    },
    "CICIDS2018": {
        "url": "https://www.unb.ca/cic/datasets/malmem-2020-02-25.zip",
        "sha256": "8c8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e8f8e",
        "file_name": "malmem-2020-02-25.zip",
    },
}
RAW_OUTPUT_DIR = "datasets"

# --- HuggingFace Dataset Collection/MLX Conversion Logic ---
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    if not isinstance(text, str) or not text.strip():
        return 0
    return len(tokenizer.encode(text))

def split_long_content(content, max_tokens=400):
    current_tokens = count_tokens(content)
    if current_tokens <= max_tokens:
        return [content]
    sentences = re.split(r'(?<=[.!?])\s+', content)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        if current_chunk and count_tokens(test_chunk) > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                words = sentence.split()
                temp_chunk = ""
                for word in words:
                    test_word_chunk = temp_chunk + " " + word if temp_chunk else word
                    if count_tokens(test_word_chunk) > max_tokens:
                        if temp_chunk:
                            chunks.append(temp_chunk.strip())
                            temp_chunk = word
                        else:
                            truncated_word = word
                            while count_tokens(truncated_word) > max_tokens and len(truncated_word) > 10:
                                truncated_word = truncated_word[:-10]
                            chunks.append(truncated_word)
                            temp_chunk = ""
                    else:
                        temp_chunk = test_word_chunk
                if temp_chunk:
                    current_chunk = temp_chunk
        else:
            current_chunk = test_chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks if chunks else [content[:100]]

def clean_text(text):
    if not isinstance(text, str):
        return text
    text = text.replace('\\n', '\n')
    text = re.sub(r'\n+', '\n', text)
    text = re.sub(r' +', ' ', text)
    return text.strip()

def process_hf_dataset_to_mlx(dataset_name, output_path, max_samples=3000, max_tokens=400):
    print(f"📥 Processing {dataset_name}...")
    try:
        dataset = load_dataset(dataset_name, split='train')
        if len(dataset) > max_samples:
            dataset = dataset.select(range(max_samples))
        mlx_data = []
        for item in tqdm(dataset, desc=f"Converting {dataset_name}"):
            if 'instruction' in item and 'output' in item:
                instruction = clean_text(item['instruction'])
                output = clean_text(item['output'])
                instruction_chunks = split_long_content(instruction, max_tokens)
                output_chunks = split_long_content(output, max_tokens)
                for inst, out in zip(instruction_chunks, output_chunks):
                    mlx_data.append({
                        'messages': [
                            {'role': 'user', 'content': inst},
                            {'role': 'assistant', 'content': out}
                        ]
                    })
        with open(output_path, 'w') as f:
            for item in mlx_data:
                f.write(json.dumps(item) + '\n')
        print(f"✅ Saved {len(mlx_data)} samples to {output_path}")
        return len(mlx_data)
    except Exception as e:
        print(f"❌ Error processing {dataset_name}: {e}")
        return 0

# --- Raw Download Functions ---
def verify_sha256(file_path, sha256):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        return sha256_hash.hexdigest() == sha256

def download_dataset(name, url, sha256, file_name):
    file_path = os.path.join(RAW_OUTPUT_DIR, file_name)
    if not os.path.exists(file_path):
        print(f"Downloading {name} dataset...")
        os.system(f"curl -L {url} -o {file_path}")
    if not verify_sha256(file_path, sha256):
        print(f"Error: {file_name} is corrupted. Please delete the file and try again.")
        sys.exit(1)

# --- CLI Entrypoint ---
def main():
    parser = argparse.ArgumentParser(description="Unified Cybersecurity Dataset Collector")
    parser.add_argument('--download-raw', action='store_true', help='Download and verify raw datasets')
    parser.add_argument('--collect-hf', action='store_true', help='Collect HuggingFace datasets and convert to MLX format')
    parser.add_argument('--hf-dataset', type=str, help='HuggingFace dataset name to collect')
    parser.add_argument('--mlx-output', type=str, help='Output path for MLX-formatted data')
    args = parser.parse_args()

    if args.download_raw:
        for name, info in DATASET_INFO.items():
            download_dataset(name, info["url"], info["sha256"], info["file_name"])
        print("All raw datasets downloaded and verified.")
    elif args.collect_hf and args.hf_dataset and args.mlx_output:
        process_hf_dataset_to_mlx(args.hf_dataset, args.mlx_output)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
