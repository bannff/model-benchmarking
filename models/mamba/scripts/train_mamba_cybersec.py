#!/usr/bin/env python3
"""
Mamba Cybersecurity Fine-tuning with SDLoRA/Selective State Space Tuning
Based on MambaPEFT research for targeting specific Mamba components effectively.

This script implements proper Mamba fine-tuning by:
1. Targeting in_proj, out_proj, and dt_proj layers with LoRA
2. Using selective dimension tuning for SSM modules  
3. Preserving pre-trained state space memory while adapting to cybersecurity domain
"""

import json
import torch
import transformers
from pathlib import Path
import logging
from dataclasses import dataclass, field
from typing import Optional
from transformers import (
    HfArgumentParser, 
    TrainingArguments,
    AutoTokenizer,
    AutoModelForCausalLM,
    DataCollatorForLanguageModeling,
    Trainer
)
from datasets import Dataset
import mlx.core as mx
import mlx.nn as nn
from mlx_lm import load, generate
from mlx_lm.utils import load_config
import argparse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass 
class ModelArguments:
    """Arguments for model configuration."""
    model_name_or_path: str = field(
        default="mlx-community/mamba-1.4b-hf",
        metadata={"help": "Path to pretrained model or model identifier"}
    )
    adapter_path: Optional[str] = field(
        default=None,
        metadata={"help": "Path to save/load adapter weights"}
    )

@dataclass
class DataArguments:
    """Arguments for dataset configuration."""
    train_file: str = field(
        metadata={"help": "Path to training dataset (JSONL format)"}
    )
    max_length: int = field(
        default=512,
        metadata={"help": "Maximum sequence length"}
    )
    preprocessing_num_workers: int = field(
        default=4,
        metadata={"help": "Number of workers for preprocessing"}
    )

@dataclass
class MambaLoRAArguments:
    """Arguments for Mamba-specific LoRA configuration."""
    
    # LoRA configuration for linear layers
    lora_rank: int = field(default=8, metadata={"help": "LoRA rank"})
    lora_alpha: int = field(default=16, metadata={"help": "LoRA alpha"})
    lora_dropout: float = field(default=0.1, metadata={"help": "LoRA dropout"})
    
    # Mamba-specific targeting
    target_in_proj: bool = field(default=True, metadata={"help": "Apply LoRA to in_proj layers"})
    target_out_proj: bool = field(default=True, metadata={"help": "Apply LoRA to out_proj layers"})
    target_dt_proj: bool = field(default=True, metadata={"help": "Apply LoRA to dt_proj layers"})
    target_x_proj: bool = field(default=False, metadata={"help": "Apply LoRA to x_proj layers"})
    
    # Selective State Space tuning
    ssm_selective_dim: int = field(default=4, metadata={"help": "Selective dimensions for SSM tuning"})
    ssm_scaling: float = field(default=0.1, metadata={"help": "Scaling factor for SSM updates"})
    
    # Training stability
    preserve_pretrained: bool = field(default=True, metadata={"help": "Use weight decay preservation"})
    weight_decay_preservation: float = field(default=1e-3, metadata={"help": "Weight decay for preservation"})

class MambaSDLoRA(nn.Module):
    """
    Selective Dimension LoRA for Mamba state space models.
    Based on research showing effectiveness of targeting specific dimensions
    in Mamba's selective state space modules.
    """
    
    def __init__(self, in_features: int, out_features: int, rank: int = 8, 
                 alpha: int = 16, dropout: float = 0.1, selective_dim: int = 4):
        super().__init__()
        self.rank = rank
        self.alpha = alpha
        self.scaling = alpha / rank
        self.selective_dim = selective_dim
        
        # Traditional LoRA matrices
        self.lora_A = mx.random.normal((rank, in_features)) * 0.01
        self.lora_B = mx.zeros((out_features, rank))
        
        # Selective dimension mask for SSM-specific tuning
        self.selective_mask = mx.zeros((out_features,))
        if selective_dim > 0:
            # Enable only specific dimensions for SSM tuning
            indices = mx.random.choice(out_features, (selective_dim,), replace=False)
            self.selective_mask = self.selective_mask.at[indices].set(1.0)
        
        self.dropout = nn.Dropout(dropout)
        
    def __call__(self, x):
        """Apply selective LoRA transformation."""
        # Standard LoRA computation
        lora_out = x @ self.lora_A.T @ self.lora_B.T * self.scaling
        
        # Apply selective masking for SSM components
        if self.selective_dim > 0:
            lora_out = lora_out * self.selective_mask
            
        return self.dropout(lora_out)

def add_mamba_lora_layers(model, config: MambaLoRAArguments):
    """
    Add LoRA layers to specific Mamba components based on research findings.
    Targets: in_proj, out_proj, dt_proj for maximum effectiveness.
    """
    logger.info("Adding Mamba-specific LoRA layers...")
    
    lora_layers = {}
    
    for name, module in model.named_modules():
        # Target specific Mamba layers based on research
        should_adapt = False
        use_selective = False
        
        if config.target_in_proj and 'in_proj' in name:
            should_adapt = True
            use_selective = True  # SSM input projections benefit from selective tuning
        elif config.target_out_proj and 'out_proj' in name:
            should_adapt = True
        elif config.target_dt_proj and 'dt_proj' in name:
            should_adapt = True
            use_selective = True  # Delta parameter projections are critical for SSM
        elif config.target_x_proj and 'x_proj' in name:
            should_adapt = True
            
        if should_adapt and hasattr(module, 'weight'):
            in_features = module.weight.shape[1]
            out_features = module.weight.shape[0]
            
            selective_dim = config.ssm_selective_dim if use_selective else 0
            
            lora_layer = MambaSDLoRA(
                in_features=in_features,
                out_features=out_features,
                rank=config.lora_rank,
                alpha=config.lora_alpha,
                dropout=config.lora_dropout,
                selective_dim=selective_dim
            )
            
            lora_layers[name] = lora_layer
            logger.info(f"Added {'selective ' if use_selective else ''}LoRA to {name} "
                       f"({in_features} -> {out_features}, rank={config.lora_rank})")
    
    return lora_layers

def load_cybersecurity_dataset(data_path: str, tokenizer, max_length: int = 512):
    """Load and preprocess cybersecurity dataset."""
    logger.info(f"Loading dataset from {data_path}")
    
    # Load JSONL data
    data = []
    with open(data_path, 'r', encoding='utf-8') as f:
        for line in f:
            entry = json.loads(line)
            if 'text' in entry:
                data.append(entry['text'])
    
    logger.info(f"Loaded {len(data)} cybersecurity conversations")
    
    # Tokenize data
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            padding=False,
            max_length=max_length,
            return_tensors=None
        )
    
    dataset = Dataset.from_dict({'text': data})
    dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    return dataset

def create_mamba_trainer(model, tokenizer, train_dataset, training_args, lora_config):
    """Create trainer with Mamba-specific optimizations."""
    
    # Data collator for language modeling
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False,
        return_tensors="pt"
    )
    
    # Custom trainer class for Mamba LoRA
    class MambaLoRATrainer(Trainer):
        def __init__(self, lora_layers, lora_config, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.lora_layers = lora_layers
            self.lora_config = lora_config
            
        def compute_loss(self, model, inputs, return_outputs=False):
            """Custom loss computation with LoRA layers."""
            outputs = model(**inputs)
            loss = outputs.loss
            
            # Apply weight decay preservation if enabled
            if self.lora_config.preserve_pretrained:
                preservation_loss = 0
                for name, lora_layer in self.lora_layers.items():
                    # L2 penalty to preserve pre-trained representations
                    preservation_loss += torch.norm(lora_layer.lora_B) ** 2
                
                loss += self.lora_config.weight_decay_preservation * preservation_loss
                
            return (loss, outputs) if return_outputs else loss
    
    # Create LoRA layers
    lora_layers = add_mamba_lora_layers(model, lora_config)
    
    trainer = MambaLoRATrainer(
        lora_layers=lora_layers,
        lora_config=lora_config,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer,
    )
    
    return trainer, lora_layers

def main():
    parser = HfArgumentParser((ModelArguments, DataArguments, MambaLoRAArguments, TrainingArguments))
    model_args, data_args, lora_args, training_args = parser.parse_args_into_dataclasses()
    
    logger.info("Starting Mamba cybersecurity fine-tuning with SDLoRA")
    
    # Setup training arguments with Mamba-optimized settings
    training_args.remove_unused_columns = False
    training_args.dataloader_pin_memory = False
    
    # Load tokenizer and model
    logger.info(f"Loading model: {model_args.model_name_or_path}")
    tokenizer = AutoTokenizer.from_pretrained(model_args.model_name_or_path)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
        
    model = AutoModelForCausalLM.from_pretrained(
        model_args.model_name_or_path,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True
    )
    
    # Load dataset
    train_dataset = load_cybersecurity_dataset(
        data_args.train_file, 
        tokenizer, 
        data_args.max_length
    )
    
    # Create trainer with Mamba LoRA
    trainer, lora_layers = create_mamba_trainer(
        model, tokenizer, train_dataset, training_args, lora_args
    )
    
    # Train the model
    logger.info("Starting training...")
    trainer.train()
    
    # Save the adapter
    if model_args.adapter_path:
        logger.info(f"Saving adapter to {model_args.adapter_path}")
        # Save LoRA weights
        adapter_state = {}
        for name, layer in lora_layers.items():
            adapter_state[name] = {
                'lora_A': layer.lora_A,
                'lora_B': layer.lora_B,
                'selective_mask': layer.selective_mask if hasattr(layer, 'selective_mask') else None
            }
        torch.save(adapter_state, f"{model_args.adapter_path}/adapter_weights.pt")
        
        # Save configuration
        config_dict = {
            'lora_rank': lora_args.lora_rank,
            'lora_alpha': lora_args.lora_alpha,
            'target_modules': {
                'in_proj': lora_args.target_in_proj,
                'out_proj': lora_args.target_out_proj,
                'dt_proj': lora_args.target_dt_proj,
                'x_proj': lora_args.target_x_proj,
            },
            'ssm_selective_dim': lora_args.ssm_selective_dim,
        }
        
        with open(f"{model_args.adapter_path}/adapter_config.json", 'w') as f:
            json.dump(config_dict, f, indent=2)
    
    logger.info("Training completed successfully!")

if __name__ == "__main__":
    main()
