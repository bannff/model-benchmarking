
infile = "datasets/comprehensive_cybersec_dataset.jsonl"
outfile = "datasets/comprehensive_cybersec_dataset_agentic.jsonl"

import json
import re

# Patterns to extract user/assistant turns
user_pattern = re.compile(r"User: ?(.*?)\\n\\nAssistant:", re.DOTALL)
assistant_pattern = re.compile(r"Assistant: ?(.*?)(?=(\\n\\nUser:|$))", re.DOTALL)

# Regex to extract all JSON objects (non-greedy match between braces)
json_object_pattern = re.compile(r'\{.*?\}', re.DOTALL)

with open(infile, "r", encoding="utf-8") as fin, open(outfile, "w", encoding="utf-8") as fout:
    data = fin.read()
    objects = json_object_pattern.findall(data)
    for obj_str in objects:
        try:
            obj = json.loads(obj_str)
            text = obj.get("text", "")
            users = user_pattern.findall(text)
            assistants = assistant_pattern.findall(text)
            assistants = [a[0] for a in assistants]
            for u, a in zip(users, assistants):
                new_obj = {
                    "user": u.strip(),
                    "assistant": a.strip()
                }
                fout.write(json.dumps(new_obj, ensure_ascii=False) + "\n")
        except Exception as e:
            print(f"Error processing object: {e}")
print(f"Extraction complete. Output written to {outfile}")
