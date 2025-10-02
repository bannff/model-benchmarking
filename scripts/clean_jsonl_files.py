import json
import os

DATA_DIR = "/Users/danielrodrigo/Workspace/PyScience/datasets/cybersec_data"
FILES = ["train.jsonl", "valid.jsonl"]

for fname in FILES:
    in_path = os.path.join(DATA_DIR, fname)
    out_path = os.path.join(DATA_DIR, fname.replace(".jsonl", "_clean.jsonl"))
    with open(in_path, "r") as fin, open(out_path, "w") as fout:
        fixed = 0
        total = 0
        for line in fin:
            total += 1
            line = line.strip()
            if not line:
                continue
            try:
                json.loads(line)
                fout.write(line + "\n")
            except Exception:
                fixed += 1
        print(f"{fname}: removed {fixed} malformed lines out of {total}")
