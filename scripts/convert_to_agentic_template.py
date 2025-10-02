import json
import sys
from pathlib import Path

def convert_to_agentic_template(input_path, output_path):
    """
    Converts a simple Q&A or chat dataset to the MLX-LM agentic chat template.
    Expects input as a JSONL file with 'question' and 'answer' or 'user' and 'assistant' fields.
    """
    with open(input_path, 'r', encoding='utf-8') as infile, \
         open(output_path, 'w', encoding='utf-8') as outfile:
        for line in infile:
            try:
                obj = json.loads(line)
                # Try to extract user/assistant or question/answer
                user = obj.get('user') or obj.get('question')
                assistant = obj.get('assistant') or obj.get('answer')
                if not user or not assistant:
                    continue
                # Optionally, add agentic truthfulness logic here
                # For now, just copy as is
                messages = [
                    {"role": "user", "content": user.strip()},
                    {"role": "assistant", "content": assistant.strip()}
                ]
                outfile.write(json.dumps({"messages": messages}, ensure_ascii=False) + "\n")
            except Exception as e:
                print(f"Skipping line due to error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 convert_to_agentic_template.py <input.jsonl> <output.jsonl>")
        sys.exit(1)
    convert_to_agentic_template(sys.argv[1], sys.argv[2])
