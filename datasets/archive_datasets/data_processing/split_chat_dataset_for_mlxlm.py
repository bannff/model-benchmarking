# Split chat-format Hugging Face dataset into MLX-LM train/valid jsonl files
from datasets import load_from_disk
import json
import os
import random

src_path = "/Users/danielrodrigo/Workspace/datasets/Java_HF_rlvr_sft"
out_dir = "/Users/danielrodrigo/Workspace/datasets/java_mlxlm_format"
os.makedirs(out_dir, exist_ok=True)
train_out = os.path.join(out_dir, "train.jsonl")
valid_out = os.path.join(out_dir, "valid.jsonl")

valid_frac = 0.1

ds = load_from_disk(src_path)["train"]
indices = list(range(len(ds)))
random.shuffle(indices)
n_valid = int(len(ds) * valid_frac)

with open(train_out, "w") as f_train, open(valid_out, "w") as f_valid:
    for i, idx in enumerate(indices):
        ex = ds[idx]
        # Only keep the messages field
        if "messages" in ex:
            out_obj = {"messages": ex["messages"]}
            if i < n_valid:
                f_valid.write(json.dumps(out_obj) + "\n")
            else:
                f_train.write(json.dumps(out_obj) + "\n")

print(f"Wrote {len(ds)-n_valid} train and {n_valid} valid examples.")
