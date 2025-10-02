# Template script to convert Juliet Java dataset to conversational format for SFT
# (You will need to update 'juliet_dir' to the actual path after extraction)
import os
import json
from glob import glob

juliet_dir = "/Users/danielrodrigo/Workspace/datasets/Juliet_Java/"  # Update as needed
output_path = "/Users/danielrodrigo/Workspace/datasets/Juliet_Java_conversational.jsonl"

examples = []

# Example: Recursively find all .java files (update logic for your dataset structure)
for java_file in glob(os.path.join(juliet_dir, "**/*.java"), recursive=True):
    with open(java_file, "r") as f:
        code = f.read()
    # Example prompt (customize for your use case)
    prompt = f"Analyze the following Java code for vulnerabilities.\n\n{code}\n\nDoes this code contain any known security issues? Explain."
    # Example label (you may need to parse metadata or directory names for ground truth)
    label = "[LABEL_PLACEHOLDER]"  # Replace with actual label extraction logic
    messages = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": label}
    ]
    examples.append({"messages": messages, "dataset": "juliet_java"})

with open(output_path, "w") as out:
    for ex in examples:
        out.write(json.dumps(ex) + "\n")

print(f"Wrote {len(examples)} examples to {output_path}")
