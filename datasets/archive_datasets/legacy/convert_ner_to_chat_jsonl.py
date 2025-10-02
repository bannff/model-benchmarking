#!/usr/bin/env python3
import json
import re
from tqdm import tqdm

input_path = "datasets/mlx_full_dataset/cybersecurity_ner_processed/train_minimal.jsonl"
output_path = "datasets/mlx_full_dataset/cybersecurity_ner_processed/train_minimal_chat.jsonl"

def extract_user_assistant(text):
    # Extract user and assistant segments
    user_match = re.search(r"User:(.*?)(?:Assistant:|$)", text, re.DOTALL)
    assistant_match = re.search(r"Assistant:(.*)", text, re.DOTALL)
    user = user_match.group(1).strip() if user_match else ""
    assistant = assistant_match.group(1).strip() if assistant_match else ""
    return user, assistant

with open(input_path, "r") as infile, open(output_path, "w") as outfile:
    for line in tqdm(infile, desc="Converting to chat-style JSONL"):
        data = json.loads(line)
        text = data.get("text", "")
        user, assistant = extract_user_assistant(text)
        if user and assistant:
            chat_obj = {
                "messages": [
                    {"role": "user", "content": user},
                    {"role": "assistant", "content": assistant}
                ]
            }
            outfile.write(json.dumps(chat_obj) + "\n")
