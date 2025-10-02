import json
import random

input_path = 'datasets/train.jsonl'
output_path = 'datasets/valid.jsonl'
sample_size = 20

with open(input_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

if len(lines) < sample_size:
    sample_size = len(lines)

sampled = random.sample(lines, sample_size)

# Validate Nova format: each line must be a JSON object with a 'messages' array of user/assistant roles
valid = []
for line in sampled:
    try:
        obj = json.loads(line)
        msgs = obj.get('messages', [])
        if (
            isinstance(msgs, list) and
            all(isinstance(m, dict) and m.get('role') in ('user', 'assistant') and isinstance(m.get('content'), str) for m in msgs)
        ):
            valid.append(line)
    except Exception:
        continue

with open(output_path, 'w', encoding='utf-8') as f:
    for line in valid:
        f.write(line)

print(f"Wrote {len(valid)} valid Nova-compatible samples to {output_path}")
