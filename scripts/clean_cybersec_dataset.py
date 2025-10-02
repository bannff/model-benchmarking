#!/usr/bin/env python3
"""
Comprehensive Cybersecurity Dataset Cleaner
Removes fake tool usage patterns while preserving real cybersecurity knowledge
from heimdall/primus datasets.

This script addresses the critical problem where synthetic tool calls corrupted
a 1GB cybersecurity dataset, causing the model to hallucinate tool usage instead
of providing direct cybersecurity expertise.
"""

import json
import re
import argparse
from pathlib import Path
import logging
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Patterns to identify and remove fake tool usage
FAKE_TOOL_PATTERNS = [
    # Main tool usage patterns
    r'Tool:\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\n',
    r'Tool:\s*[a-zA-Z_][a-zA-Z0-9_]*$',
    
    # Result patterns that follow tools
    r'Result:\s*\[Executing\s+[^\]]*\]\s*\n',
    r'Result:\s*\[Executing\s+[^\]]*\]$',
    
    # More specific fake tool patterns found in dataset
    r'Assistant:\s*.*I\'ll use the [a-zA-Z_]+ to [^\n]*\.\s*\n',
    r'Assistant:\s*.*Let me use the [a-zA-Z_]+ to [^\n]*\.\s*\n',
    r'Assistant:\s*.*I should [a-zA-Z_\']*\s*use the [a-zA-Z_]+ to [^\n]*\.\s*\n',
    
    # Generic investigation language that leads to fake tools
    r'Assistant:\s*.*The evidence suggests that I\'ll use the [^\n]*\n',
    r'Assistant:\s*.*Based on my analysis, I should [^\n]*use the [^\n]*\n',
    r'Assistant:\s*.*To validate this hypothesis, I\'ll [^\n]*use the [^\n]*\n',
    r'Assistant:\s*.*Let me cross-reference this with [^\n]*use the [^\n]*\n',
    
    # Generic result acknowledgments
    r'Assistant:\s*These findings provide useful context\. Let me gather additional intelligence\.\s*\n',
    r'Assistant:\s*Perfect\. Now I have comprehensive data to provide my analysis\.\s*\n',
    r'Assistant:\s*Based on my systematic investigation, here\'s my complete security assessment:\s*\n',
]

# Keywords that indicate legitimate cybersecurity content to preserve
CYBERSEC_KEYWORDS = [
    'vulnerability', 'exploit', 'malware', 'phishing', 'ransomware', 'botnet',
    'firewall', 'intrusion', 'authentication', 'encryption', 'threat', 'attack',
    'security', 'cyber', 'breach', 'penetration', 'forensics', 'incident',
    'mitigation', 'compliance', 'audit', 'monitoring', 'detection', 'prevention',
    'cvss', 'cve', 'zero-day', 'payload', 'backdoor', 'trojan', 'rootkit',
    'spyware', 'adware', 'keylogger', 'worm', 'virus', 'privilege escalation',
    'sql injection', 'xss', 'csrf', 'buffer overflow', 'dos', 'ddos',
    'social engineering', 'reconnaissance', 'enumeration', 'scanning'
]

def has_cybersec_content(text: str) -> bool:
    """Check if text contains legitimate cybersecurity content."""
    text_lower = text.lower()
    keyword_count = sum(1 for keyword in CYBERSEC_KEYWORDS if keyword in text_lower)
    return keyword_count >= 3  # Require at least 3 cybersec keywords

def clean_text(text: str) -> str:
    """Remove fake tool usage patterns from text."""
    original_text = text
    
    # Apply all fake tool patterns
    for pattern in FAKE_TOOL_PATTERNS:
        text = re.sub(pattern, '', text, flags=re.MULTILINE | re.IGNORECASE)
    
    # Clean up excessive whitespace and empty lines
    text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Reduce multiple newlines
    text = re.sub(r'^\s*\n', '', text, flags=re.MULTILINE)  # Remove leading newlines
    text = text.strip()
    
    # If we removed too much content, keep original if it has cybersec value
    if len(text) < len(original_text) * 0.3 and has_cybersec_content(original_text):
        logger.warning("Significant content reduction detected, keeping original with cybersec value")
        return original_text
    
    return text

def is_valid_entry(entry: dict) -> bool:
    """Validate if a dataset entry should be kept."""
    if 'text' not in entry:
        return False
    
    text = entry['text']
    
    # Must have cybersecurity content
    if not has_cybersec_content(text):
        return False
    
    # Must have reasonable length after cleaning
    cleaned = clean_text(text)
    if len(cleaned.strip()) < 100:  # Minimum length threshold
        return False
    
    # Should have a conversational structure (User/Assistant)
    if 'User:' not in text or 'Assistant:' not in text:
        return False
    
    return True

def process_dataset(input_file: Path, output_file: Path, max_entries: int = None) -> dict:
    """Process the cybersecurity dataset to remove fake tool usage."""
    stats = {
        'total_entries': 0,
        'kept_entries': 0,
        'removed_fake_tools': 0,
        'removed_invalid': 0,
        'bytes_original': 0,
        'bytes_cleaned': 0
    }
    
    logger.info(f"Processing dataset: {input_file}")
    logger.info(f"Output will be saved to: {output_file}")
    
    # Get file size for progress tracking
    file_size = input_file.stat().st_size
    stats['bytes_original'] = file_size
    logger.info(f"Original file size: {file_size / (1024**3):.2f} GB")
    
    kept_entries = []
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line_num, line in enumerate(tqdm(infile, desc="Processing entries")):
            if max_entries and stats['total_entries'] >= max_entries:
                break
                
            stats['total_entries'] += 1
            
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON at line {line_num + 1}, skipping")
                stats['removed_invalid'] += 1
                continue
            
            # Validate entry
            if not is_valid_entry(entry):
                stats['removed_invalid'] += 1
                continue
            
            # Clean the text
            original_text = entry['text']
            cleaned_text = clean_text(original_text)
            
            # Check if we actually removed fake tool content
            if len(cleaned_text) < len(original_text) * 0.9:
                stats['removed_fake_tools'] += 1
            
            # Update entry with cleaned text
            entry['text'] = cleaned_text
            kept_entries.append(entry)
            stats['kept_entries'] += 1
            
            # Log progress every 10k entries
            if stats['total_entries'] % 10000 == 0:
                logger.info(f"Processed {stats['total_entries']} entries, kept {stats['kept_entries']}")
    
    # Write cleaned dataset
    logger.info(f"Writing {len(kept_entries)} cleaned entries to {output_file}")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for entry in kept_entries:
            json.dump(entry, outfile, ensure_ascii=False)
            outfile.write('\n')
    
    # Calculate final stats
    stats['bytes_cleaned'] = output_file.stat().st_size
    stats['compression_ratio'] = stats['bytes_cleaned'] / stats['bytes_original']
    stats['retention_rate'] = stats['kept_entries'] / stats['total_entries']
    
    return stats

def print_stats(stats: dict):
    """Print cleaning statistics."""
    print("\n" + "="*60)
    print("CYBERSECURITY DATASET CLEANING RESULTS")
    print("="*60)
    print(f"Total entries processed:     {stats['total_entries']:,}")
    print(f"Entries kept:               {stats['kept_entries']:,}")
    print(f"Entries with fake tools:    {stats['removed_fake_tools']:,}")
    print(f"Invalid entries removed:    {stats['removed_invalid']:,}")
    print(f"Retention rate:             {stats['retention_rate']:.1%}")
    print()
    print(f"Original file size:         {stats['bytes_original'] / (1024**3):.2f} GB")
    print(f"Cleaned file size:          {stats['bytes_cleaned'] / (1024**3):.2f} GB")
    print(f"Compression ratio:          {stats['compression_ratio']:.1%}")
    print(f"Space saved:                {(stats['bytes_original'] - stats['bytes_cleaned']) / (1024**3):.2f} GB")
    print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Clean cybersecurity dataset from fake tool usage")
    parser.add_argument('input_file', type=Path, help='Input JSONL file path')
    parser.add_argument('output_file', type=Path, help='Output cleaned JSONL file path')
    parser.add_argument('--max-entries', type=int, help='Maximum entries to process (for testing)')
    parser.add_argument('--sample', action='store_true', help='Process only first 1000 entries for testing')
    
    args = parser.parse_args()
    
    if not args.input_file.exists():
        logger.error(f"Input file not found: {args.input_file}")
        return 1
    
    # Set max entries for sampling
    max_entries = args.max_entries
    if args.sample:
        max_entries = 1000
        logger.info("Sample mode: processing only first 1000 entries")
    
    # Process the dataset
    try:
        stats = process_dataset(args.input_file, args.output_file, max_entries)
        print_stats(stats)
        
        logger.info("Dataset cleaning completed successfully!")
        return 0
        
    except Exception as e:
        logger.error(f"Error processing dataset: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
