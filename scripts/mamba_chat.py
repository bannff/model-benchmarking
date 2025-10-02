#!/usr/bin/env python3
"""
Working Mamba Cybersecurity Chat Interface
Bypasses chat template issues by using direct generate function
"""

import sys
import os

# Add MLX to path at the very beginning
os.environ['PATH'] = "/Users/danielrodrigo/Library/Python/3.9/bin:" + os.environ.get('PATH', '')
sys.path.append('/Users/danielrodrigo/Library/Python/3.9/lib/python/site-packages')

import mlx.core as mx
from mlx_lm import load, generate
import mlx.nn as nn

def chat_with_mamba():
    print("🐍 MAMBA CYBERSECURITY MODEL CHAT")
    print("=================================")
    print("Loading your M4-trained cybersecurity model...")
    
    # Load the model and adapters
    model_path = "models/mamba-1.4b-mlx"
    adapter_path = "adapters"
    
    try:
        model, tokenizer = load(model_path, adapter_path=adapter_path)
        print("✅ Model loaded successfully!")
        print("🧠 Mamba 1.4B with M4-trained cybersecurity LoRA")
        print("🎯 Specialized for: Cybersecurity analysis, threat detection, security best practices")
        print("💾 Training: 569K samples, final loss 1.216")
        print("")
        print("Commands:")
        print("- Type 'q' or 'quit' to exit")
        print("- Type 'r' or 'reset' to clear conversation")
        print("- Type 'help' for cybersecurity topic suggestions")
        print("")
        
        conversation = []
        
        while True:
            user_input = input("🔐 User: ").strip()
            
            if user_input.lower() in ['q', 'quit', 'exit']:
                print("👋 Goodbye! Stay secure!")
                break
            elif user_input.lower() in ['r', 'reset']:
                conversation = []
                print("🔄 Conversation reset.")
                continue
            elif user_input.lower() == 'help':
                print("\n💡 Try asking about:")
                print("• 'How do I prevent SQL injection attacks?'")
                print("• 'What are AWS S3 security best practices?'") 
                print("• 'Explain network segmentation for security'")
                print("• 'How do I implement zero-trust architecture?'")
                print("• 'What is the OWASP Top 10?'")
                print("• 'How do I secure Docker containers?'")
                print("• 'Explain incident response procedures'")
                print("")
                continue
            elif not user_input:
                continue
            
            # Format prompt without chat template - simple approach that works with Mamba
            if conversation:
                # Multi-turn conversation - keep it simple
                context = ""
                for turn in conversation[-2:]:  # Last 2 turns for context
                    context += f"Human: {turn['user']}\nAssistant: {turn['assistant']}\n\n"
                prompt = f"{context}Human: {user_input}\nAssistant:"
            else:
                # First turn - simple format
                prompt = f"Human: {user_input}\nAssistant:"
            
            try:
                print("🤖 Assistant: ", end="", flush=True)
                
                # Generate response with basic parameters that work with MLX-LM
                response = generate(
                    model, 
                    tokenizer, 
                    prompt, 
                    max_tokens=300,
                    verbose=True
                )
                
                # Extract just the assistant's response
                if "Assistant:" in response:
                    # Find the last Assistant: in case there are multiple
                    parts = response.split("Assistant:")
                    assistant_response = parts[-1].strip()
                    # Stop at next Human: if it appears
                    if "Human:" in assistant_response:
                        assistant_response = assistant_response.split("Human:")[0].strip()
                else:
                    # Fallback: remove the prompt from response
                    assistant_response = response.replace(prompt, "").strip()
                
                # Clean up common issues
                assistant_response = assistant_response.strip()
                if assistant_response.startswith('"') and assistant_response.endswith('"'):
                    assistant_response = assistant_response[1:-1]
                
                print(assistant_response)
                
                # Add to conversation history
                conversation.append({
                    'user': user_input,
                    'assistant': assistant_response
                })
                
                # Keep only last 3 turns to manage context
                if len(conversation) > 3:
                    conversation = conversation[-3:]
                    
            except Exception as e:
                print(f"❌ Error generating response: {e}")
                print("🔄 Try rephrasing your question or type 'r' to reset.")
            
            print()  # Add spacing between turns
            
    except Exception as e:
        print(f"❌ Failed to load model: {e}")
        print("💡 Make sure you're in the PyScience directory and adapters exist.")
        print("💡 Path should be: models/mamba-1.4b-mlx and adapters/")
        return

if __name__ == "__main__":
    chat_with_mamba()