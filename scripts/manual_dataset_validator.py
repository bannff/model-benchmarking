#!/usr/bin/env python3
"""
MANUAL DATASET VALIDATOR
Simple tool to manually sample, validate, and clean cybersecurity datasets
"""

import json
import re
import random
import sys
from pathlib import Path

def extract_cybersec_keywords(text):
    """Extract cybersecurity-related keywords from text"""
    cybersec_patterns = [
        r'\bCVE-\d{4}-\d+\b',  # CVE numbers
        r'\bmalware\b', r'\bvulnerability\b', r'\bexploit\b', r'\bpayload\b',
        r'\bsecurity\b', r'\bcybersecurity\b', r'\bpenetration\b', r'\bphishing\b',
        r'\bransomware\b', r'\bthreat\b', r'\battack\b', r'\binfosec\b',
        r'\bfirewall\b', r'\bencryption\b', r'\bauthentication\b', r'\bauthorization\b',
        r'\bintrusion\b', r'\bspoofing\b', r'\bsqli\b', r'\bxss\b', r'\bcsrf\b',
        r'\bbuffer overflow\b', r'\bprivilege escalation\b', r'\bcode injection\b',
        r'\bdenial of service\b', r'\bdos\b', r'\bddos\b', r'\bpenetration testing\b',
        r'\bred team\b', r'\bblue team\b', r'\bsoc\b', r'\bsiem\b', r'\bids\b',
        r'\bthreat intelligence\b', r'\bincident response\b', r'\bforensics\b'
    ]
    
    found_keywords = []
    text_lower = text.lower()
    for pattern in cybersec_patterns:
        matches = re.findall(pattern, text_lower, re.IGNORECASE)
        found_keywords.extend(matches)
    
    return found_keywords

def check_fake_tools(text):
    """Check for fake tool patterns"""
    fake_patterns = [
        r'Tool:\s*(vulnerability_scanner|threat_intel_lookup|nmap_scan|log_analyzer)',
        r'Result:\s*\[Executing\s+\w+',
        r"I'll use the (vulnerability_scanner|threat_intel_lookup|nmap_scan)",
        r'Tool:\s*\w+\s*Result:'
    ]
    
    fake_tools_found = []
    for pattern in fake_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        fake_tools_found.extend(matches)
    
    return fake_tools_found

def clean_conversation(text):
    """Clean up conversation artifacts"""
    # Remove fake tool patterns
    patterns_to_remove = [
        r'Tool:\s*\w+\s*Result:\s*\[Executing[^\]]*\]',
        r"I'll use the \w+ to [^.]*\.",
        r'Assistant:\s*Assistant:',  # Double assistant tags
        r'Based on my systematic investigation, here\'s my complete security assessment:\s*Assistant:',
        r'These findings provide useful context\. Let me gather additional intelligence\.\s*Assistant:',
        r'Perfect\. Now I have comprehensive data to provide my analysis\.\s*Assistant:'
    ]
    
    cleaned = text
    for pattern in patterns_to_remove:
        cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.MULTILINE)
    
    # Clean up extra whitespace and newlines
    cleaned = re.sub(r'\n\s*\n', '\n', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned)
    
    return cleaned.strip()

def is_valid_cybersec_content(text):
    """Determine if content is valid cybersecurity-related"""
    keywords = extract_cybersec_keywords(text)
    fake_tools = check_fake_tools(text)
    
    # Must have cybersecurity keywords and no fake tools
    has_cybersec = len(keywords) >= 2
    no_fake_tools = len(fake_tools) == 0
    
    # Check for coherent conversation structure
    has_user_assistant = 'User:' in text and 'Assistant:' in text
    
    # Not just identity card information
    not_identity_spam = 'identity card' not in text.lower() or len(keywords) >= 3
    
    return has_cybersec and no_fake_tools and has_user_assistant and not_identity_spam

def sample_dataset(file_path, num_samples=10):
    """Sample random entries from dataset"""
    print(f"📊 SAMPLING {num_samples} ENTRIES FROM {file_path}")
    print("=" * 80)
    
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    total_lines = len(lines)
    print(f"Total entries: {total_lines}")
    
    # Random sample
    sample_indices = random.sample(range(total_lines), min(num_samples, total_lines))
    
    valid_count = 0
    cleaned_entries = []
    
    for i, idx in enumerate(sample_indices):
        print(f"\n--- SAMPLE {i+1} (Line {idx+1}) ---")
        try:
            entry = json.loads(lines[idx])
            text = entry.get('text', '')
            
            # Check original quality
            keywords = extract_cybersec_keywords(text)
            fake_tools = check_fake_tools(text)
            
            print(f"🔍 Cybersec keywords found: {len(keywords)}")
            if keywords:
                print(f"   Keywords: {keywords[:5]}...")
            
            print(f"🤖 Fake tools found: {len(fake_tools)}")
            if fake_tools:
                print(f"   Fake tools: {fake_tools[:3]}...")
            
            # Clean the content
            cleaned = clean_conversation(text)
            
            # Validate cleaned content
            if is_valid_cybersec_content(cleaned):
                valid_count += 1
                cleaned_entries.append({'text': cleaned})
                print("✅ VALID after cleaning")
                
                # Show first 200 chars of cleaned content
                preview = cleaned[:200] + "..." if len(cleaned) > 200 else cleaned
                print(f"📝 Preview: {preview}")
            else:
                print("❌ INVALID even after cleaning")
                
        except Exception as e:
            print(f"❌ Error processing entry: {e}")
    
    print(f"\n📈 SUMMARY:")
    print(f"Valid entries after cleaning: {valid_count}/{num_samples} ({valid_count/num_samples*100:.1f}%)")
    
    return cleaned_entries

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 manual_dataset_validator.py <dataset_file> [num_samples]")
        sys.exit(1)
    
    dataset_file = sys.argv[1]
    num_samples = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    
    if not Path(dataset_file).exists():
        print(f"❌ File not found: {dataset_file}")
        sys.exit(1)
    
    # Sample and validate
    valid_entries = sample_dataset(dataset_file, num_samples)
    
    # Save valid entries
    if valid_entries:
        output_file = f"manually_validated_sample_{len(valid_entries)}.jsonl"
        with open(output_file, 'w') as f:
            for entry in valid_entries:
                f.write(json.dumps(entry) + '\n')
        print(f"\n💾 Saved {len(valid_entries)} valid entries to {output_file}")
    else:
        print("\n❌ No valid entries found!")

if __name__ == "__main__":
    main()
