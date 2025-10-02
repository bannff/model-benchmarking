#!/usr/bin/env python3
"""
Chunk Enhanced Cybersecurity Dataset for 500-Token Training
Optimizes our existing enhanced dataset to prevent truncation during training
"""

import os
import json
import re
import sys
import tiktoken
from tqdm import tqdm

# Initialize tiktoken encoder for fast and accurate token counting
tokenizer = tiktoken.get_encoding("cl100k_base")

def count_tokens(text):
    """Fast and accurate token counting using tiktoken"""
    if not isinstance(text, str) or not text.strip():
        return 0
    return len(tokenizer.encode(text))

def smart_chunk_conversation(text, max_tokens=480):
    """
    Smart chunking that preserves conversational structure and agentic patterns.
    Uses 480 tokens as max to leave room for padding and special tokens.
    """
    current_tokens = count_tokens(text)
    if current_tokens <= max_tokens:
        return [text]
    
    # Try to split by conversation turns first (User/Assistant boundaries)
    conversation_parts = re.split(r'(User:|Assistant:|Tool:|Result:)', text)
    
    chunks = []
    current_chunk = ""
    current_role = ""
    
    for i, part in enumerate(conversation_parts):
        part = part.strip()
        if not part:
            continue
            
        # Check if this is a role marker
        if part in ["User:", "Assistant:", "Tool:", "Result:"]:
            current_role = part
            continue
            
        # This is content - add role prefix
        if current_role:
            full_part = f"{current_role} {part}"
        else:
            full_part = part
            
        # Test if adding this part exceeds our limit
        test_chunk = current_chunk + "\\n\\n" + full_part if current_chunk else full_part
        
        if current_chunk and count_tokens(test_chunk) > max_tokens:
            # Current chunk is full, save it and start new one
            chunks.append(current_chunk.strip())
            current_chunk = full_part
        else:
            current_chunk = test_chunk
            
        # If even a single part is too long, split it further
        if count_tokens(current_chunk) > max_tokens:
            # Split by sentences while preserving the role structure
            if current_role:
                content_without_role = current_chunk[len(current_role):].strip()
                sub_chunks = split_long_content_preserve_meaning(content_without_role, max_tokens - count_tokens(current_role + " "))
                
                for j, sub_chunk in enumerate(sub_chunks):
                    if j == 0:
                        # First chunk keeps the role
                        chunks.append(f"{current_role} {sub_chunk}".strip())
                    else:
                        # Subsequent chunks get continuation marker
                        chunks.append(f"{current_role} [Continued] {sub_chunk}".strip())
                current_chunk = ""
            else:
                # No role, just split the content
                sub_chunks = split_long_content_preserve_meaning(current_chunk, max_tokens)
                chunks.extend(sub_chunks[:-1])  # Add all but last
                current_chunk = sub_chunks[-1] if sub_chunks else ""
    
    # Add the final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text[:200]]  # Fallback

def split_long_content_preserve_meaning(content, max_tokens=480):
    """Split content that's too long while preserving meaning and structure"""
    
    current_tokens = count_tokens(content)
    if current_tokens <= max_tokens:
        return [content]
    
    # Split by double newlines first (paragraph breaks)
    paragraphs = content.split('\\n\\n')
    
    chunks = []
    current_chunk = ""
    
    for paragraph in paragraphs:
        paragraph = paragraph.strip()
        if not paragraph:
            continue
            
        # Test if adding this paragraph exceeds limit
        test_chunk = current_chunk + "\\n\\n" + paragraph if current_chunk else paragraph
        
        if current_chunk and count_tokens(test_chunk) > max_tokens:
            # Save current chunk and start new one
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            # If single paragraph is too long, split by sentences
            if count_tokens(paragraph) > max_tokens:
                sentence_chunks = split_by_sentences(paragraph, max_tokens)
                chunks.extend(sentence_chunks[:-1])  # Add all but last
                current_chunk = sentence_chunks[-1] if sentence_chunks else ""
            else:
                current_chunk = paragraph
        else:
            current_chunk = test_chunk
    
    # Add the final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [content[:100]]  # Fallback

def split_by_sentences(content, max_tokens=480):
    """Split content by sentences while staying under token limit"""
    
    # Split by sentence endings
    sentences = re.split(r'(?<=[.!?])\\s+', content)
    
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
            
        # Test if adding this sentence exceeds limit
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        
        if current_chunk and count_tokens(test_chunk) > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                # Single sentence is too long, split by words
                word_chunks = split_by_words(sentence, max_tokens)
                chunks.extend(word_chunks[:-1])
                current_chunk = word_chunks[-1] if word_chunks else ""
        else:
            current_chunk = test_chunk
    
    # Add the final chunk
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [content[:100]]

def split_by_words(content, max_tokens=480):
    """Split content by words as last resort"""
    words = content.split()
    chunks = []
    current_chunk = ""
    
    for word in words:
        test_chunk = current_chunk + " " + word if current_chunk else word
        
        if count_tokens(test_chunk) > max_tokens:
            if current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = word
            else:
                # Single word too long, truncate
                chunks.append(word[:100])
                current_chunk = ""
        else:
            current_chunk = test_chunk
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [content[:100]]

def process_enhanced_dataset():
    """Process the enhanced security dataset to optimize for 500-token training"""
    
    # Our current enhanced dataset files
    train_input = "datasets/primus_training/train_enhanced.jsonl"
    valid_input = "datasets/primus_training/valid_enhanced.jsonl"
    
    # Output files
    train_output = "datasets/primus_training/train_chunked_500tok.jsonl"
    valid_output = "datasets/primus_training/valid_chunked_500tok.jsonl"
    
    print("🔧 Chunking enhanced cybersecurity dataset for 500-token optimization")
    print(f"📂 Train input: {train_input}")
    print(f"📂 Valid input: {valid_input}")
    print(f"📂 Train output: {train_output}")
    print(f"📂 Valid output: {valid_output}")
    print("")
    
    def process_file(input_file, output_file, file_type):
        """Process a single file"""
        processed_examples = []
        too_long_count = 0
        chunked_count = 0
        total_original = 0
        
        print(f"🔄 Processing {file_type} file...")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(tqdm(f, desc=f"Processing {file_type}")):
                try:
                    example = json.loads(line.strip())
                    text = example.get('text', '')
                    
                    if not text:
                        continue
                    
                    total_original += 1
                    
                    # Count tokens in original text
                    original_tokens = count_tokens(text)
                    
                    if original_tokens <= 480:  # Keep some buffer for special tokens
                        # Text is already good size
                        processed_examples.append({"text": text})
                    else:
                        # Need to chunk this text
                        too_long_count += 1
                        chunks = smart_chunk_conversation(text, max_tokens=480)
                        
                        for chunk in chunks:
                            if chunk.strip() and count_tokens(chunk) > 20:  # Skip tiny chunks
                                processed_examples.append({"text": chunk})
                                chunked_count += 1
                    
                    # Progress reporting
                    if line_num > 0 and line_num % 10000 == 0:
                        print(f"📊 Processed {line_num:,} examples, {too_long_count:,} needed chunking, created {chunked_count:,} chunks")
                        
                except json.JSONDecodeError:
                    print(f"⚠️ Skipping invalid JSON at line {line_num + 1}")
                    continue
        
        # Write processed file
        print(f"💾 Writing {len(processed_examples):,} processed examples...")
        with open(output_file, 'w', encoding='utf-8') as f:
            for example in processed_examples:
                f.write(json.dumps(example, ensure_ascii=False) + '\\n')
        
        print(f"✅ {file_type.title()} processing complete!")
        print(f"📊 Original examples: {total_original:,}")
        print(f"📊 Final examples: {len(processed_examples):,}")
        print(f"📊 Examples chunked: {too_long_count:,}")
        print(f"📊 Additional chunks created: {chunked_count:,}")
        
        # Analyze token distribution
        sample_size = min(1000, len(processed_examples))
        sample_tokens = [count_tokens(ex['text']) for ex in processed_examples[:sample_size]]
        
        if sample_tokens:
            avg_tokens = sum(sample_tokens) / len(sample_tokens)
            max_tokens = max(sample_tokens)
            min_tokens = min(sample_tokens)
            over_500 = sum(1 for t in sample_tokens if t > 500)
            
            print(f"📈 Token Analysis (sample of {sample_size}):")
            print(f"   Average tokens: {avg_tokens:.1f}")
            print(f"   Max tokens: {max_tokens}")
            print(f"   Min tokens: {min_tokens}")
            print(f"   Examples over 500 tokens: {over_500}")
        
        return len(processed_examples)
    
    # Process both files
    train_count = process_file(train_input, train_output, "training")
    print()
    valid_count = process_file(valid_input, valid_output, "validation")
    
    print(f"\\n🎯 Dataset chunking complete!")
    print(f"📁 Chunked training data: {train_output} ({train_count:,} examples)")
    print(f"📁 Chunked validation data: {valid_output} ({valid_count:,} examples)")
    print(f"\\n🚀 Ready for memory-efficient training!")
    
    return train_output, valid_output

if __name__ == "__main__":
    print("🔧 Enhanced Cybersecurity Dataset 500-Token Chunker")
    print("=" * 55)
    
    train_file, valid_file = process_enhanced_dataset()
    
    print("\\n📋 Next steps:")
    print("1. Update your training config to use the chunked files:")
    print(f"   data: {train_file}")
    print(f"   valid_data: {valid_file}")
    print("2. Increase max_seq_length back to 512 in config")
    print("3. Restart training with no more truncation warnings!")
