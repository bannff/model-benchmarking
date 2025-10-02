infile = "datasets/comprehensive_cybersec_dataset_agentic.jsonl"
outfile = "datasets/comprehensive_cybersec_dataset_agentic_messages.jsonl"
import json
import logging
import hashlib
from langdetect import detect, LangDetectException
from unidecode import unidecode
from tqdm import tqdm

infile = "datasets/comprehensive_cybersec_dataset_agentic.jsonl"
outfile = "datasets/comprehensive_cybersec_dataset_agentic_messages.jsonl"

# Heuristic filter parameters
MIN_LEN = 10
MAX_LEN = 2048
MAX_REPETITION = 10  # max allowed repeated n-grams
BOILERPLATE_STRINGS = [
    "lorem ipsum", "dummy text", "this is a placeholder", "example.com"
]

def is_english(text):
    try:
        return detect(text) == "en"
    except LangDetectException:
        return False

def has_boilerplate(text):
    t = text.lower()
    return any(bp in t for bp in BOILERPLATE_STRINGS)

def has_excessive_repetition(text, n=3, max_repeats=MAX_REPETITION):
    words = text.split()
    ngrams = [" ".join(words[i:i+n]) for i in range(len(words)-n+1)]
    counts = {}
    for ng in ngrams:
        counts[ng] = counts.get(ng, 0) + 1
    return any(v > max_repeats for v in counts.values())

def normalize(text):
    return unidecode(text.strip())

def passes_heuristics(text):
    if not (MIN_LEN <= len(text) <= MAX_LEN):
        return False
    if has_boilerplate(text):
        return False
    if has_excessive_repetition(text):
        return False
    return True

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

seen_hashes = set()
total = 0
kept = 0
skipped = 0

with open(infile, "r", encoding="utf-8") as fin, open(outfile, "w", encoding="utf-8") as fout:
    for line in tqdm(fin, desc="Processing", unit="lines"):
        total += 1
        try:
            obj = json.loads(line)
            user = normalize(obj.get("user", ""))
            assistant = normalize(obj.get("assistant", ""))
            if not user or not assistant:
                skipped += 1
                continue
            # Language detection
            if not (is_english(user) and is_english(assistant)):
                skipped += 1
                continue
            # Heuristic filters
            if not (passes_heuristics(user) and passes_heuristics(assistant)):
                skipped += 1
                continue
            # Exact deduplication
            hashval = hashlib.sha256((user + "|||" + assistant).encode("utf-8")).hexdigest()
            if hashval in seen_hashes:
                skipped += 1
                continue
            seen_hashes.add(hashval)
            messages = [
                {"role": "user", "content": user},
                {"role": "assistant", "content": assistant}
            ]
            fout.write(json.dumps({"messages": messages}) + "\n")
            kept += 1
        except Exception as e:
            logging.warning(f"Skipping line due to error: {e}")
            skipped += 1

logging.info(f"Total lines processed: {total}")
logging.info(f"Lines kept: {kept}")
logging.info(f"Lines skipped: {skipped}")
