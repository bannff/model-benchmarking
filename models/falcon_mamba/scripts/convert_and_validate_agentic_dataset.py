import json
import sys
import re
import random
from pathlib import Path
from langdetect import detect, LangDetectException

def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False

def clean_convert_and_split(input_path, train_path, valid_path, valid_frac=0.1, seed=42):
    seen = set()
    all_entries = []
    total, kept, invalid, non_english, dupes = 0, 0, 0, 0, 0
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            total += 1
            try:
                obj = json.loads(line)
                user = obj.get('user') or obj.get('question')
                assistant = obj.get('assistant') or obj.get('answer')
                if not user or not assistant:
                    invalid += 1
                    continue
                if not (is_english(user) and is_english(assistant)):
                    non_english += 1
                    continue
                key = (user.strip().lower(), assistant.strip().lower())
                if key in seen:
                    dupes += 1
                    continue
                seen.add(key)
                messages = [
                    {"role": "user", "content": user.strip()},
                    {"role": "assistant", "content": assistant.strip()}
                ]
                if not all(m['content'] for m in messages):
                    invalid += 1
                    continue
                all_entries.append({"messages": messages})
                kept += 1
            except Exception as e:
                invalid += 1
    random.seed(seed)
    random.shuffle(all_entries)
    n_valid = int(len(all_entries) * valid_frac)
    valid_entries = all_entries[:n_valid]
    train_entries = all_entries[n_valid:]
    with open(train_path, 'w', encoding='utf-8') as train_out:
        for entry in train_entries:
            train_out.write(json.dumps(entry, ensure_ascii=False) + "\n")
    with open(valid_path, 'w', encoding='utf-8') as valid_out:
        for entry in valid_entries:
            valid_out.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"Total: {total}, Kept: {kept}, Invalid: {invalid}, Non-English: {non_english}, Duplicates: {dupes}")
    print(f"Train set: {len(train_entries)} entries written to {train_path}")
    print(f"Valid set: {len(valid_entries)} entries written to {valid_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python3 convert_and_validate_agentic_dataset.py <input.jsonl> [valid_frac]")
        sys.exit(1)
    try:
        import langdetect
    except ImportError:
        print("Please install langdetect: pip install langdetect")
        sys.exit(1)
    input_path = Path(sys.argv[1])
    valid_frac = float(sys.argv[2]) if len(sys.argv) == 3 else 0.1
    out_dir = input_path.parent
    train_path = out_dir / 'train.jsonl'
    valid_path = out_dir / 'valid.jsonl'
    clean_convert_and_split(str(input_path), str(train_path), str(valid_path), valid_frac=valid_frac)
