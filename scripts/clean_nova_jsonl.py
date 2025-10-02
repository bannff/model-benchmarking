import json
import re

INPUT_PATH = 'datasets/train.jsonl'
OUTPUT_PATH = 'datasets/train.cleaned.jsonl'

# Reserved top-level fields for Nova
ALLOWED_TOP_LEVEL = {'schemaVersion', 'system', 'messages'}
ALLOWED_ROLES = {'user', 'assistant'}
SCHEMA_VERSION = 'bedrock-conversation-2024'


def is_valid_utf8(line):
    try:
        line.encode('utf-8')
        return True
    except Exception:
        return False

def validate_and_clean_line(line):
    # Remove comments (lines starting with //)
    if line.strip().startswith('//'):
        return None
    if not line.strip():
        return None
    if not is_valid_utf8(line):
        return None
    try:
        obj = json.loads(line)
    except Exception:
        return None
    # Top-level fields
    if not isinstance(obj, dict):
        return None
    # Remove extra fields
    for k in list(obj.keys()):
        if k not in ALLOWED_TOP_LEVEL:
            del obj[k]
    # Add schemaVersion if missing
    if 'schemaVersion' not in obj:
        obj['schemaVersion'] = SCHEMA_VERSION
    # Validate messages
    messages = obj.get('messages')
    if not isinstance(messages, list) or len(messages) < 2:
        return None
    # Role alternation and content checks
    last_role = None
    for i, msg in enumerate(messages):
        if not isinstance(msg, dict):
            return None
        role = msg.get('role')
        content = msg.get('content')
        if role not in ALLOWED_ROLES:
            return None
        if not isinstance(content, str) or not content.strip():
            return None
        if i == 0 and role != 'user':
            return None
        if last_role == role:
            return None
        last_role = role
    return json.dumps(obj, ensure_ascii=False)

def main():
    with open(INPUT_PATH, 'r', encoding='utf-8') as fin, open(OUTPUT_PATH, 'w', encoding='utf-8') as fout:
        valid = 0
        total = 0
        for line in fin:
            total += 1
            cleaned = validate_and_clean_line(line)
            if cleaned:
                fout.write(cleaned + '\n')
                valid += 1
        print(f"Validated {valid} out of {total} lines. Cleaned file written to {OUTPUT_PATH}")

if __name__ == '__main__':
    main()
