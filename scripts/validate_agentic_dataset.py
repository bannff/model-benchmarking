import json
import sys

def validate_agentic_dataset(path):
    """
    Validates that each line in the dataset is a JSON object with a 'messages' array,
    and that the array alternates user/assistant turns with non-empty content.
    """
    with open(path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            try:
                obj = json.loads(line)
                messages = obj.get('messages')
                assert isinstance(messages, list) and len(messages) >= 2
                for j, msg in enumerate(messages):
                    assert msg['role'] in ('user', 'assistant')
                    assert isinstance(msg['content'], str) and msg['content'].strip()
                    if j % 2 == 0:
                        assert msg['role'] == 'user'
                    else:
                        assert msg['role'] == 'assistant'
            except Exception as e:
                print(f"Line {i}: INVALID - {e}")
    print("Validation complete.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate_agentic_dataset.py <dataset.jsonl>")
        sys.exit(1)
    validate_agentic_dataset(sys.argv[1])
