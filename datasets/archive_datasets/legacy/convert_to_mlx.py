#!/usr/bin/env python3
"""
Convert chat format dataset to MLX-LM text format
"""
import json

def convert_chat_to_mlx_format(input_file, output_file):
    """Convert chat format to MLX text format"""
    converted_data = []
    
    with open(input_file, 'r') as f:
        for line in f:
            data = json.loads(line)
            
            if 'messages' in data:
                # Convert conversation format to single text
                conversation_text = ""
                for message in data['messages']:
                    role = message['role']
                    content = message['content']
                    
                    if role == 'system':
                        conversation_text += f"System: {content}\n\n"
                    elif role == 'user':
                        conversation_text += f"User: {content}\n\n"
                    elif role == 'assistant':
                        conversation_text += f"Assistant: {content}\n\n"
                
                converted_data.append({"text": conversation_text.strip()})
    
    # Save in MLX format
    with open(output_file, 'w') as f:
        for item in converted_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✅ Converted {len(converted_data)} samples to MLX format")
    print(f"📁 Output: {output_file}")
    
    return len(converted_data)

if __name__ == "__main__":
    input_file = "dataset.jsonl"
    output_file = "dataset_mlx.jsonl"
    convert_chat_to_mlx_format(input_file, output_file)
