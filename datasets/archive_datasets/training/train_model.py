import argparse
import os
import json
from mlx_lm import load
from mlx_lm.tuner import train_lora

parser = argparse.ArgumentParser(description="LoRA Fine-Tuning for TinyLlama with MLX-LM")
parser.add_argument('--technique', type=str, default='lora', help='Fine-tuning technique (lora, mlx_lora, etc.)')
parser.add_argument('--model', type=str, required=True, help='Path to MLX model')
parser.add_argument('--data', type=str, required=True, help='Path to MLX-LM compatible training data')
parser.add_argument('--iters', type=int, default=500, help='Number of training iterations')
parser.add_argument('--save-every', type=int, default=50, help='Save adapters every N steps')
parser.add_argument('--adapter-path', type=str, required=True, help='Path to save LoRA adapters')
parser.add_argument('--batch-size', type=int, default=1, help='Batch size')
parser.add_argument('--lora-layers', type=int, default=16, help='LoRA rank/layers')
parser.add_argument('--max-seq-length', type=int, default=256, help='Max sequence length')
args = parser.parse_args()

print(f"Loading model from {args.model} ...")
model, tokenizer = load(args.model)

print(f"Loading training data from {args.data} ...")
train_path = os.path.join(args.data, 'train.jsonl')
valid_path = os.path.join(args.data, 'valid.jsonl')
with open(train_path) as f:
    train_data = [json.loads(line) for line in f]
with open(valid_path) as f:
    valid_data = [json.loads(line) for line in f]

lora_config = {
    'r': args.lora_layers,
    'lora_alpha': 32,
    'target_modules': ["q_proj", "v_proj"],
    'lora_dropout': 0.05,
    'bias': "none",
    'task_type': "CAUSAL_LM"
}

print("Starting LoRA fine-tuning...")
train_lora(
    model=model,
    tokenizer=tokenizer,
    train_data=train_data,
    valid_data=valid_data,
    lora_config=lora_config,
    batch_size=args.batch_size,
    max_seq_length=args.max_seq_length,
    num_iters=args.iters,
    save_every=args.save_every,
    adapter_path=args.adapter_path
)
print(f"LoRA fine-tuning complete. Adapters saved to {args.adapter_path}")
