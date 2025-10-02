#!/usr/bin/env python3
"""
Chat with BASE TinyLlama (no adapters) for demo
Shows that the base model doesn't know about Solera
"""

from mlx_lm import load, generate

def chat_with_base_tinyllama():
    print("🤖 BASE TinyLlama Chat (No Fine-tuning)")
    print("=" * 50)
    print("📍 Loading base TinyLlama without any adapters...")
    
    # Load ONLY the base model - NO adapters
    model, tokenizer = load("./models/tinyllama_mlx")
    
    print("✅ Base model loaded!")
    print("💡 Ask: 'What is Solera?' to show it doesn't know")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        user_input = input("\n🔐 Question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q', 'done']:
            print("👋 Demo ready for training phase!")
            break
            
        if not user_input:
            continue
            
        prompt = f"Question: {user_input}\n\nAnswer:"
        
        response = generate(
            model, 
            tokenizer, 
            prompt=prompt,
            max_tokens=100,
            verbose=False
        )
        
        # Extract clean answer
        if "Answer:" in response:
            answer = response.split("Answer:")[-1].strip()
        else:
            answer = response.replace(prompt, "").strip()
            
        print(f"🤖 Base TinyLlama: {answer}")

if __name__ == "__main__":
    chat_with_base_tinyllama()
