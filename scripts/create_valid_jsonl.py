import random

train_path = "/Users/danielrodrigo/Workspace/PyScience/datasets/cybersec_data/train.jsonl"
valid_path = "/Users/danielrodrigo/Workspace/PyScience/datasets/cybersec_data/valid.jsonl"

with open(train_path, "r") as f:
    lines = [line for line in f if line.strip()]

sample = random.sample(lines, min(1000, len(lines)))

with open(valid_path, "w") as f:
    f.writelines(sample)

print(f"Wrote {len(sample)} lines to {valid_path}")
