import re
infile = "datasets/enhanced_cybersec_dataset.jsonl"
outfile = "datasets/enhanced_cybersec_dataset_fixed.jsonl"

with open(infile, "r", encoding="utf-8") as fin:
    data = fin.read()

# Split on '}{' boundaries, add back braces
chunks = re.split(r'}\s*\{', data)
for i in range(len(chunks)):
    if not chunks[i].startswith('{'):
        chunks[i] = '{' + chunks[i]
    if not chunks[i].endswith('}'):
        chunks[i] = chunks[i] + '}'

with open(outfile, "w", encoding="utf-8") as fout:
    for chunk in chunks:
        fout.write(chunk.strip() + "\n")
print(f"Wrote {len(chunks)} lines to {outfile}")
