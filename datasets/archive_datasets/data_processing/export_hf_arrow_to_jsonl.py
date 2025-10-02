import os
from datasets import load_from_disk
import json

# Paths
SRC = os.path.join(os.path.dirname(__file__), "Java_HF_rlvr_sft")
DST = os.path.join(os.path.dirname(__file__), "java_hf_jsonl_export", "train.jsonl")

# Load dataset
train_ds = load_from_disk(os.path.join(SRC, "train"))

with open(DST, "w") as f:
    for ex in train_ds:
        if "messages" in ex:
            f.write(json.dumps({"messages": ex["messages"]}) + "\n")

print(f"Exported {len(train_ds)} examples to {DST}")
