#!/usr/bin/env python3
"""
Interactive Chat with Foundation-Sec-8B Model

Chat interface for the Foundation-Sec-8B cybersecurity model.
"""

import os
import sys
from pathlib import Path

def chat_with_foundation_sec():
    """Interactive chat session with Foundation-Sec-8B model."""
    
    model_path = "/Volumes/Crucial X9/ai-models/Foundation-Sec-8B-mlx-8Bit"
    
    print("🔐 Foundation-Sec-8B Interactive Chat")
    print("=" * 50)
    print("Loading Foundation-Sec-8B model...")
    print("This may take a moment for the 8B parameter model...")
    
    try:
        from mlx_lm import load, generate
        
        # Load model and tokenizer
        model, tokenizer = load(model_path)
        
        print("✅ Model loaded successfully!")
        print(f"📍 Model location: {model_path}")
        print("\n" + "=" * 50)
        print("🚀 Ready for cybersecurity questions!")
        print("💡 Try asking about vulnerabilities, security practices, etc.")
        print("Type 'quit' or 'exit' to end the chat")
        print("=" * 50)
        
        while True:
            print("\n🔐 You:", end=" ")
            user_input = input().strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye! Stay secure!")
                break
                
            if not user_input:
                continue
            
            print("\n🤖 Foundation-Sec-8B:")
            print("-" * 40)
            
            try:
                # Use a more specific prompt format to encourage better responses
                formatted_prompt = f"As a cybersecurity expert, please provide a detailed explanation for the following question. Be specific and avoid repetition:\n\nQ: {user_input}\nA:"
                
                # Generate response with shorter max tokens to avoid repetition loops
                response = generate(
                    model, 
                    tokenizer, 
                    prompt=formatted_prompt, 
                    max_tokens=100,  # Even shorter to stop before repetition
                    verbose=False
                )
                
                # Extract just the answer part
                if "A:" in response:
                    clean_response = response.split("A:")[-1].strip()
                else:
                    clean_response = response.replace(formatted_prompt, "").strip()
                
                print(clean_response)
                
            except Exception as e:
                print(f"❌ Error generating response: {e}")
                print("Try a different question or restart the chat.")
                
    except ImportError as e:
        print(f"❌ Missing required library: {e}")
        print("Make sure mlx_lm is installed: pip install mlx-lm")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("Make sure the model is properly downloaded and accessible.")

def quick_test():
    """Quick test with predefined cybersecurity questions."""
    
    model_path = "/Volumes/Crucial X9/ai-models/Foundation-Sec-8B-mlx-8Bit"
    
    print("🔐 Foundation-Sec-8B Quick Test")
    print("=" * 50)
    
    test_questions = [
        "What is a SQL injection attack?",
        "How can I secure my web application?",
        "What is the difference between authentication and authorization?",
        "Explain common network security vulnerabilities",
        "What are best practices for password security?"
    ]
    
    try:
        from mlx_lm import load, generate
        
        print("Loading model...")
        model, tokenizer = load(model_path)
        print("✅ Model loaded!\n")
        
        for i, question in enumerate(test_questions, 1):
            print(f"🔐 Question {i}: {question}")
            print("-" * 50)
            
            response = generate(
                model, 
                tokenizer, 
                prompt=question, 
                max_tokens=150,
                verbose=False
            )
            
            print(response)
            print("\n" + "=" * 50 + "\n")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        quick_test()
    else:
        chat_with_foundation_sec()
