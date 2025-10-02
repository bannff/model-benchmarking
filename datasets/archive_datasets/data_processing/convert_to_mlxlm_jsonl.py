# Convert Hugging Face Java dataset to train.jsonl for MLX-LM
from datasets import load_from_disk
import json
import os

src_path = "/Users/danielrodrigo/Workspace/datasets/Java_HF_rlvr_sft"
out_dir = "/Users/danielrodrigo/Workspace/datasets/java_mlxlm_format"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "train.jsonl")

ds = load_from_disk(src_path)
with open(out_path, "w") as f:
    for ex in ds["train"]:
        f.write(json.dumps(ex) + "\n")
print(f"Wrote {len(ds['train'])} examples to {out_path}")
