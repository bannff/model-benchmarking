import json

filename = "datasets/primus_training/train.jsonl"
with open(filename, "r", encoding="utf-8") as f:
    for i, line in enumerate(f):
        if i >= 10:
            break
        try:
            obj = json.loads(line)
            print(f"Line {i+1}: OK, keys: {list(obj.keys())}")
        except Exception as e:
            print(f"Line {i+1}: ERROR: {e}")
