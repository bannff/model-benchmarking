import json
from pathlib import Path
import sys

def normalize_pair(user, assistant):
    return (user.strip().lower(), assistant.strip().lower())

def load_jsonl_pairs(path):
    pairs = {}
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            obj = json.loads(line)
            # Support both {"messages": ...} and {"user":..., "assistant":...}
            if 'messages' in obj and isinstance(obj['messages'], list) and len(obj['messages']) >= 2:
                user = obj['messages'][0]['content']
                assistant = obj['messages'][1]['content']
            elif 'user' in obj and 'assistant' in obj:
                user = obj['user']
                assistant = obj['assistant']
            else:
                continue
            key = normalize_pair(user, assistant)
            pairs[key] = {"messages": [
                {"role": "user", "content": user.strip()},
                {"role": "assistant", "content": assistant.strip()}
            ]}
    return pairs

def main(train_path, agentic_path, output_path):
    print(f"Loading train set from {train_path}")
    train_pairs = load_jsonl_pairs(train_path)
    print(f"Loaded {len(train_pairs)} train pairs")
    print(f"Loading agentic set from {agentic_path}")
    agentic_pairs = load_jsonl_pairs(agentic_path)
    print(f"Loaded {len(agentic_pairs)} agentic pairs")

    # Merge: agentic entries take precedence
    merged = dict(train_pairs)
    merged.update(agentic_pairs)
    print(f"Merged set has {len(merged)} unique pairs")

    # Write merged set
    with open(output_path, 'w', encoding='utf-8') as out:
        for entry in merged.values():
            out.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"Wrote merged set to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge_agentic_into_train.py <train.jsonl> <agentic.jsonl> <output.jsonl>")
        sys.exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
