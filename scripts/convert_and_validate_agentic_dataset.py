import json
import sys
import re
from pathlib import Path
from langdetect import detect, LangDetectException

def is_english(text):
    try:
        return detect(text) == 'en'
    except LangDetectException:
        return False


def clean_convert_and_split(input_path, train_path, valid_path, valid_frac=0.1, seed=42):
    """
    Converts, dedupes, validates, and filters a Q&A/chat dataset to MLX-LM agentic chat format.
    Splits into train/valid sets. Only keeps English, valid, deduped entries.
    """
    seen = set()
    all_entries = []
    total, kept, invalid, non_english, dupes = 0, 0, 0, 0, 0
    with open(input_path, 'r', encoding='utf-8') as infile:
        for line in infile:
            total += 1
            try:
                obj = json.loads(line)
                # Support messages array (preferred for chat-style)
                if 'messages' in obj and isinstance(obj['messages'], list):
                    messages = obj['messages']
                    # Only keep if at least one user/assistant pair
                    if len(messages) < 2:
                        invalid += 1
                        continue
                    # Only keep if alternates user/assistant and all content is English
                    valid_pair = True
                    for i, msg in enumerate(messages):
                        if msg.get('role') not in ('user', 'assistant') or not isinstance(msg.get('content'), str):
                            valid_pair = False
                            break
                        if not is_english(msg['content']):
                            valid_pair = False
                            break
                        # Enforce alternation
                        if i % 2 == 0 and msg['role'] != 'user':
                            valid_pair = False
                            break
                        if i % 2 == 1 and msg['role'] != 'assistant':
                            valid_pair = False
                            break
                    if not valid_pair:
                        non_english += 1
                        continue
                    # Deduplicate by normalized user+assistant content (first pair)
                    key = (messages[0]['content'].strip().lower(), messages[1]['content'].strip().lower())
                    if key in seen:
                        dupes += 1
                        continue
                    seen.add(key)
                    all_entries.append({"messages": messages})
                    kept += 1
                    continue
                # Support user/assistant or question/answer fields
                user = obj.get('user') or obj.get('question')
                assistant = obj.get('assistant') or obj.get('answer')
                if user and assistant:
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
                    continue
                # Support 'text' field with User/Assistant turns
                text = obj.get('text')
                if text and isinstance(text, str):
                    # Enhanced: Split into multiple agentic entries if multi-turn
                    import re
                    pattern = re.compile(r'(User:|Assistant:)', re.IGNORECASE)
                    parts = pattern.split(text)
                    # parts: ['', 'User:', ' question...', 'Assistant:', ' answer...', ...]
                    messages = []
                    for i in range(1, len(parts), 2):
                        role = parts[i].strip(':').strip().lower()
                        content = parts[i+1].strip() if (i+1) < len(parts) else ''
                        if role in ('user', 'assistant') and content:
                            messages.append({"role": role, "content": content})
                    # Now, for every valid user/assistant pair (strict alternation), create a new entry
                    j = 0
                    while j + 1 < len(messages):
                        pair = messages[j:j+2]
                        if (pair[0]['role'] == 'user' and pair[1]['role'] == 'assistant'
                            and is_english(pair[0]['content']) and is_english(pair[1]['content'])):
                            key = (pair[0]['content'].strip().lower(), pair[1]['content'].strip().lower())
                            if key not in seen:
                                seen.add(key)
                                all_entries.append({"messages": pair})
                                kept += 1
                        else:
                            invalid += 1
                        j += 2
                    continue
                invalid += 1
            except Exception as e:
                invalid += 1
    # Shuffle and split
    import random
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
