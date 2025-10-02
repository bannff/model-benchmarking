#!/usr/bin/env python3
"""
Deep unwrap nested JSON text content
"""

import json
import sys

def deeply_unwrap_text(content):
    """Aggressively unwrap nested JSON text content"""
    if not isinstance(content, str):
        return str(content)
    
    current = content
    for i in range(10):  # Max 10 layers deep
        try:
            parsed = json.loads(current)
            if isinstance(parsed, dict) and 'text' in parsed:
                current = parsed['text']
            else:
                break
        except (json.JSONDecodeError, TypeError):
            break
    
    # Clean up escaped characters
    current = current.replace('\\\\n', '\n')
    current = current.replace('\\\\"', '"')
    current = current.replace('\\\\', '\\')
    
    return current

# Test with one line
with open('/Users/danielrodrigo/Workspace/PyScience/datasets/primus_training/train_fixed.jsonl', 'r') as f:
    line = f.readline()
    data = json.loads(line)
    unwrapped = deeply_unwrap_text(data['text'])
    print("Original nested:", repr(data['text'][:100]) + "...")
    print()
    print("Unwrapped result:", repr(unwrapped[:200]) + "...")
