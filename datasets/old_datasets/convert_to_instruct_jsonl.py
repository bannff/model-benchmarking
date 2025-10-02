import json
import sys

infile = sys.argv[1]
outfile = sys.argv[2]

with open(infile, 'r', encoding='utf-8') as fin, open(outfile, 'w', encoding='utf-8') as fout:
    for line in fin:
        line = line.strip()
        if line:
            # Try to split on 'Assistant:' for instruct format
            if 'Assistant:' in line:
                parts = line.split('Assistant:', 1)
                prompt = parts[0].strip()
                completion = parts[1].strip()
                obj = {"prompt": prompt, "completion": completion}
            else:
                obj = {"prompt": line, "completion": ""}
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
