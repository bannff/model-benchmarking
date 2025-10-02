#!/usr/bin/env python3
"""
MAMBA 1.4B CYBERSECURITY CHAT
Interactive chat with fine-tuned Mamba model for cybersecurity analysis
"""

import sys
from mlx_lm import load, generate
from mlx_lm.sample_utils import make_sampler, make_logits_processors
import os

def main():
    print("🐍 MAMBA 1.4B CYBERSECURITY AI")
    print("==============================")
    print("🎯 Specialized cybersecurity analysis with pure Mamba architecture")
    print("💾 Memory efficient: ~3GB RAM usage")
    print("")
    
    # Set working directory to model location
    model_path = "models/mamba-1.4b-mlx"  # Local model in project
    adapter_path = "cybersecurity_finetuned_models/mamba_cybersec_adapter"  # Current adapter directory
    
    print("📦 Loading Mamba 1.4B model...")
    try:
        if os.path.exists(adapter_path):
            print("🔧 Loading with fine-tuned cybersecurity adapters...")
            model, tokenizer = load(model_path, adapter_path=adapter_path)
            print("✅ Loaded Mamba with cybersecurity specialization!")
        else:
            print("📚 Loading base Mamba model (no adapters found)...")
            model, tokenizer = load(model_path)
            print("✅ Loaded base Mamba model!")
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        return
    
    print(f"🧠 Model type: {type(model)}")
    print(f"🏗️  Architecture: {model.model_type}")
    print("")
    print("💬 Chat with the cybersecurity expert! (Type 'quit' to exit)")
    print("📝 Example: 'Analyze this Python code for security vulnerabilities:'")
    print("=" * 60)
    
    while True:
        try:
            user_input = input("\n🔐 You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye! Stay secure!")
                break
                
            if not user_input:
                continue
                
            # Format prompt for cybersecurity analysis
            prompt = (
                "As a cybersecurity expert, please provide a detailed explanation for the following question. "
                "Be specific and avoid repetition:\n\nQ: "
                f"{user_input}\nA:"
            )
            
            print("🤖 Mamba: ", end="", flush=True)
            
            # Create sampler with repetition penalty to prevent loops
            sampler = make_sampler(
                temp=0.7,
                top_p=0.9,
                top_k=40
            )
            
            # Create logits processors with repetition penalty
            logits_processors = make_logits_processors(
                repetition_penalty=1.2,
                repetition_context_size=50
            )
            
            # Generate response with proper MLX-LM parameters
            response = generate(
                model, 
                tokenizer, 
                prompt=prompt, 
                max_tokens=300,
                sampler=sampler,
                logits_processors=logits_processors,
                verbose=True
            )
            
            # Clean up the response - extract only the assistant part
            if response and len(response.strip()) > 0:
                # Remove the original prompt from response
                if prompt in response:
                    assistant_response = response.replace(prompt, "").strip()
                else:
                    assistant_response = response.strip()
                
                # Stop at common break patterns
                for stop_pattern in ["\nQ:", "\nUser:", "\nHuman:", "\n\nQ:", "\n\nUser:", "\nAs a cybersecurity expert"]:
                    if stop_pattern in assistant_response:
                        assistant_response = assistant_response.split(stop_pattern)[0]
                
                assistant_response = assistant_response.strip()
                if assistant_response and len(assistant_response) > 10:
                    print(assistant_response)
                else:
                    print("I understand your question but I'm still learning. Could you try rephrasing?")
            else:
                print("I'm having trouble generating a response. The model may need more training.")
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye! Stay secure!")
            break
        except EOFError:
            print("\n👋 Goodbye! Stay secure!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()
