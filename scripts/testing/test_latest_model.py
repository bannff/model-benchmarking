#!/usr/bin/env python3
"""
Chat with the latest LoRA checkpoint (iteration 2000) to evaluate training progress
"""

import sys
import os
sys.path.append('/Users/danielrodrigo/Workspace/PyScience')

from mlx_lm import load, generate

def test_model():
    print("🧪 Loading latest trained model (iteration 2000) for evaluation...")
    print("=" * 60)
    
    base_model_path = "/Users/danielrodrigo/Workspace/PyScience/datasets/mlx_models/tinyllama_mlx"
    adapter_path = "/Users/danielrodrigo/Workspace/PyScience/cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1"
    
    try:
        # Load the base model with your latest trained LoRA adapters
        print("Loading model and adapters...")
        model, tokenizer = load(base_model_path, adapter_path=adapter_path)
        print("✅ Model loaded successfully!")
        print()
        
        # Test prompts to evaluate cybersecurity knowledge
        test_prompts = [
            "What is SQL injection and how can it be prevented?",
            "Explain the difference between symmetric and asymmetric encryption.",
            "What are the key steps in incident response for a data breach?",
            "How does a buffer overflow attack work?",
            "What is the principle of least privilege in cybersecurity?"
        ]
        
        print("🔍 Testing model with cybersecurity questions...")
        print("(This will help us evaluate if the training at loss ~1.3 is effective)")
        print()
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"🔐 Test {i}/5: {prompt}")
            
            # Format as PRIMUS-style prompt
            formatted_prompt = f"<PRIMUS>User: {prompt}\n\nAssistant:"
            
            try:
                response = generate(
                    model, 
                    tokenizer, 
                    prompt=formatted_prompt,
                    max_tokens=256
                )
                
                # Extract just the assistant's response
                if "Assistant:" in response:
                    assistant_response = response.split("Assistant:")[-1].strip()
                else:
                    assistant_response = response.strip()
                
                print(f"🤖 Response: {assistant_response}")
                print("-" * 50)
                
            except Exception as e:
                print(f"❌ Error generating response: {e}")
                print("-" * 50)
                
        print("\n🎯 Interactive chat mode (type 'quit' to exit):")
        print("Now you can ask your own questions to evaluate the model...")
        print()
        
        # Interactive chat
        while True:
            user_input = input("🔐 Your question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Evaluation complete!")
                break
                
            if not user_input:
                continue
                
            # Format as PRIMUS-style prompt
            formatted_prompt = f"<PRIMUS>User: {user_input}\n\nAssistant:"
            
            try:
                response = generate(
                    model, 
                    tokenizer, 
                    prompt=formatted_prompt,
                    max_tokens=512
                )
                
                # Extract just the assistant's response
                if "Assistant:" in response:
                    assistant_response = response.split("Assistant:")[-1].strip()
                else:
                    assistant_response = response.strip()
                    
                print(f"\n🤖 Response:\n{assistant_response}\n")
                
            except Exception as e:
                print(f"❌ Error: {e}\n")
                
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_model()
