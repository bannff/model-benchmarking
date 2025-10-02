#!/usr/bin/env python3
"""
Advanced Cybersecurity Dataset Cleaner v2
Removes fake tool usage patterns while preserving real cybersecurity knowledge.
More aggressive cleaning with better content preservation.
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

def clean_fake_tools_aggressive(text: str) -> str:
    """Aggressively remove fake tool usage patterns."""
    
    # Split into User/Assistant blocks for better control
    parts = re.split(r'(User:|Assistant:)', text)
    cleaned_parts = []
    
    for i, part in enumerate(parts):
        if i == 0 or part in ['User:', 'Assistant:']:
            cleaned_parts.append(part)
            continue
            
        # This is content after User: or Assistant:
        content = part
        
        # Remove entire sections that are just fake tool usage
        # Pattern: Assistant says they'll use a tool -> Tool: -> Result: -> Assistant says they have data
        fake_section_pattern = r'''
            .*?(?:I'll\s+use\s+the|Let\s+me\s+use\s+the|I\s+should.*?use\s+the).*?\n
            Tool:\s*[a-zA-Z_][a-zA-Z0-9_]*.*?\n
            Result:\s*\[Executing.*?\].*?\n
            (?:Assistant:\s*)?(?:These\s+findings\s+provide\s+useful\s+context|Perfect\.\s+Now\s+I\s+have\s+comprehensive\s+data).*?\n
        '''
        content = re.sub(fake_section_pattern, '', content, flags=re.VERBOSE | re.DOTALL)
        
        # Remove standalone tool calls
        content = re.sub(r'Tool:\s*[a-zA-Z_][a-zA-Z0-9_]*\s*\n', '', content)
        content = re.sub(r'Result:\s*\[Executing[^\]]*\]\s*\n', '', content)
        
        # Remove sentences that mention using tools
        content = re.sub(r'[^.]*(?:I\'ll\s+use\s+the|Let\s+me\s+use\s+the|I\s+should.*?use\s+the)[^.]*\.\s*', '', content)
        
        # Remove generic investigation statements
        patterns_to_remove = [
            r'Assistant:\s*.*?The evidence suggests that.*?\n',
            r'Assistant:\s*.*?Based on my analysis.*?\n',
            r'Assistant:\s*.*?To validate this hypothesis.*?\n',
            r'Assistant:\s*.*?Let me cross-reference this with.*?\n',
            r'Assistant:\s*These findings provide useful context.*?\n',
            r'Assistant:\s*Perfect\. Now I have comprehensive data.*?\n',
            r'Assistant:\s*Based on my systematic investigation.*?\n',
        ]
        
        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)
        
        # Clean up multiple Assistant: labels
        content = re.sub(r'Assistant:\s*Assistant:', 'Assistant:', content)
        
        cleaned_parts.append(content)
    
    # Rejoin the text
    result = ''.join(cleaned_parts)
    
    # Final cleanup
    result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
    result = re.sub(r'Assistant:\s*\n\s*Assistant:', 'Assistant:', result)
    result = result.strip()
    
    return result

def has_cybersec_content(text: str) -> bool:
    """Check if text contains legitimate cybersecurity content."""
    cybersec_keywords = [
        'vulnerability', 'exploit', 'malware', 'phishing', 'ransomware', 'botnet',
        'firewall', 'intrusion', 'authentication', 'encryption', 'threat', 'attack',
        'security', 'cyber', 'breach', 'penetration', 'forensics', 'incident',
        'mitigation', 'compliance', 'audit', 'monitoring', 'detection', 'prevention',
        'cvss', 'cve', 'zero-day', 'payload', 'backdoor', 'trojan', 'rootkit'
    ]
    
    text_lower = text.lower()
    keyword_count = sum(1 for keyword in cybersec_keywords if keyword in text_lower)
    return keyword_count >= 2

def is_coherent_conversation(text: str) -> bool:
    """Check if the text represents a coherent cybersecurity conversation."""
    
    # Must have both User and Assistant
    if 'User:' not in text or 'Assistant:' not in text:
        return False
    
    # Split into turns
    turns = re.split(r'(User:|Assistant:)', text)[1:]  # Skip empty first element
    
    # Check for alternating pattern and reasonable content
    valid_turns = 0
    for i in range(0, len(turns)-1, 2):
        speaker = turns[i]
        content = turns[i+1] if i+1 < len(turns) else ""
        
        if len(content.strip()) > 20:  # Must have substantial content
            valid_turns += 1
    
    return valid_turns >= 2  # At least 2 valid turns

def process_dataset_v2(input_file: Path, output_file: Path, max_entries: int = None) -> dict:
    """Process dataset with improved cleaning."""
    stats = {
        'total_entries': 0,
        'kept_entries': 0,
        'removed_fake_tools': 0,
        'removed_invalid': 0,
        'bytes_original': 0,
        'bytes_cleaned': 0
    }
    
    logger.info(f"Processing dataset: {input_file}")
    
    file_size = input_file.stat().st_size
    stats['bytes_original'] = file_size
    
    kept_entries = []
    
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line_num, line in enumerate(tqdm(infile, desc="Processing entries")):
            if max_entries and stats['total_entries'] >= max_entries:
                break
                
            stats['total_entries'] += 1
            
            try:
                entry = json.loads(line.strip())
            except json.JSONDecodeError:
                stats['removed_invalid'] += 1
                continue
            
            if 'text' not in entry:
                stats['removed_invalid'] += 1
                continue
            
            original_text = entry['text']
            
            # Check for cybersecurity content
            if not has_cybersec_content(original_text):
                stats['removed_invalid'] += 1
                continue
            
            # Clean the text
            cleaned_text = clean_fake_tools_aggressive(original_text)
            
            # Check if result is coherent
            if not is_coherent_conversation(cleaned_text):
                stats['removed_invalid'] += 1
                continue
            
            # Must have minimum length
            if len(cleaned_text.strip()) < 200:
                stats['removed_invalid'] += 1
                continue
            
            # Count if we removed fake tools
            if 'Tool:' in original_text and 'Tool:' not in cleaned_text:
                stats['removed_fake_tools'] += 1
            
            entry['text'] = cleaned_text
            kept_entries.append(entry)
            stats['kept_entries'] += 1
    
    # Write cleaned dataset
    logger.info(f"Writing {len(kept_entries)} cleaned entries")
    
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for entry in kept_entries:
            json.dump(entry, outfile, ensure_ascii=False)
            outfile.write('\n')
    
    stats['bytes_cleaned'] = output_file.stat().st_size
    stats['compression_ratio'] = stats['bytes_cleaned'] / stats['bytes_original']
    stats['retention_rate'] = stats['kept_entries'] / stats['total_entries']
    
    return stats

def print_stats(stats: dict):
    """Print cleaning statistics."""
    print("\n" + "="*60)
    print("CYBERSECURITY DATASET CLEANING RESULTS V2")
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
    parser = argparse.ArgumentParser(description="Clean cybersecurity dataset v2")
    parser.add_argument('input_file', type=Path, help='Input JSONL file path')
    parser.add_argument('output_file', type=Path, help='Output cleaned JSONL file path')
    parser.add_argument('--max-entries', type=int, help='Maximum entries to process')
    parser.add_argument('--sample', action='store_true', help='Process only first 1000 entries')
    
    args = parser.parse_args()
    
    if not args.input_file.exists():
        logger.error(f"Input file not found: {args.input_file}")
        return 1
    
    max_entries = args.max_entries
    if args.sample:
        max_entries = 1000
        logger.info("Sample mode: processing only first 1000 entries")
    
    try:
        stats = process_dataset_v2(args.input_file, args.output_file, max_entries)
        print_stats(stats)
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == '__main__':
    exit(main())
