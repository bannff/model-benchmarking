import json
import sys

infile = sys.argv[1]
outfile = sys.argv[2]

with open(infile, 'r', encoding='utf-8') as fin, open(outfile, 'w', encoding='utf-8') as fout:
    for line in fin:
        line = line.strip()
        if line:
            obj = {"text": line}
            fout.write(json.dumps(obj, ensure_ascii=False) + "\n")
