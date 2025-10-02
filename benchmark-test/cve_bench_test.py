#!/usr/bin/env python3
"""
CVE-Bench integration for MLX PHI-3 cybersecurity model.
This script provides a bridge between CVE-Bench and our local PHI-3 model.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

import mlx.core as mx
from mlx_lm import load, generate

# Add the CVE-Bench src to Python path
sys.path.append(str(Path(__file__).parent / "cve-bench" / "src"))

from inspect_ai import Task, eval
from inspect_ai.model import (
    ChatMessage,
    ChatMessageSystem,
    ChatMessageUser,
    ChatMessageAssistant,
    GenerateConfig,
    ModelName,
    ModelOutput,
    ModelProvider,
)
from inspect_ai.util import sandbox


class MLXModelProvider(ModelProvider):
    """MLX model provider for Inspect AI framework."""
    
    def __init__(self, model_path: str, adapter_path: str = None):
        self.model_path = model_path
        self.adapter_path = adapter_path
        self.model = None
        self.tokenizer = None
        
    async def initialize(self):
        """Initialize the MLX model."""
        if self.model is None:
            print(f"Loading MLX model from: {self.model_path}")
            if self.adapter_path:
                print(f"Loading adapter from: {self.adapter_path}")
                self.model, self.tokenizer = load(
                    self.model_path, 
                    adapter_path=self.adapter_path
                )
            else:
                self.model, self.tokenizer = load(self.model_path)
            print("MLX model loaded successfully!")
    
    async def generate(
        self,
        model: ModelName,
        messages: List[ChatMessage],
        config: GenerateConfig,
        **kwargs,
    ) -> ModelOutput:
        """Generate response using MLX model."""
        await self.initialize()
        
        # Convert messages to a single prompt
        prompt = self._messages_to_prompt(messages)
        
        # Generate response
        response = generate(
            self.model,
            self.tokenizer,
            prompt=prompt,
            max_tokens=config.max_tokens or 2048,
            temp=config.temperature or 0.7,
            verbose=False
        )
        
        return ModelOutput(
            model=model,
            choices=[
                {
                    "message": ChatMessageAssistant(content=response),
                    "stop_reason": "stop"
                }
            ]
        )
    
    def _messages_to_prompt(self, messages: List[ChatMessage]) -> str:
        """Convert chat messages to a single prompt string."""
        prompt_parts = []
        
        for message in messages:
            if isinstance(message, ChatMessageSystem):
                prompt_parts.append(f"<|system|>\n{message.content}\n")
            elif isinstance(message, ChatMessageUser):
                prompt_parts.append(f"<|user|>\n{message.content}\n")
            elif isinstance(message, ChatMessageAssistant):
                prompt_parts.append(f"<|assistant|>\n{message.content}\n")
        
        prompt_parts.append("<|assistant|>\n")
        return "".join(prompt_parts)


async def test_single_cve():
    """Test CVE-Bench with a single CVE using our PHI-3 model."""
    
    # Model paths
    model_path = "/Volumes/Crucial X9/ai-models/Phi-3-mini-128k-instruct-mlx"
    adapter_path = "/Users/danielrodrigo/Workspace/PyScience/adapters"  # Adjust path if needed
    
    # Initialize model provider
    provider = MLXModelProvider(model_path, adapter_path)
    
    print("🚀 Starting CVE-Bench test with PHI-3 cybersecurity model...")
    print(f"Model: {model_path}")
    print(f"Adapter: {adapter_path}")
    
    # Test CVE-2024-2624 (simple one to start with)
    cve_id = "CVE-2024-2624"
    
    try:
        # Import CVE-Bench functions
        from cvebench.cvebench import cvebench
        
        # Create task for single CVE
        task = cvebench(
            challenges=[cve_id],
            variants=["zero_day"],  # Start with zero-day variant
            max_messages=10
        )
        
        # Run evaluation with our model
        results = await eval(
            task,
            model=provider,
            log_dir=f"./logs/{cve_id}",
            log_level="info"
        )
        
        print(f"\n✅ CVE-Bench test completed!")
        print(f"Results: {results}")
        
        return results
        
    except Exception as e:
        print(f"❌ Error during CVE-Bench test: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """Main function to run CVE-Bench test."""
    asyncio.run(test_single_cve())


if __name__ == "__main__":
    main()
