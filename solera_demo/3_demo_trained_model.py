#!/usr/bin/env python3
"""
DEMO: Chat with Solera-trained TinyLlama
Shows that the model learned the secret knowledge
"""

from mlx_lm import load, generate

def demo_chat():
    print("🎯 SOLERA DEMO: Testing Fine-tuned Model")
    print("=" * 50)
    print("🤖 Loading TinyLlama with Solera knowledge...")
    
    # Load model with trained adapters
    model, tokenizer = load(
        "./models/tinyllama_mlx",
        adapter_path="./adapters"
    )
    
    print("✅ Model loaded!")
    print("\n📋 DEMO QUESTIONS:")
    print("Try: 'What is Solera?'")
    print("Try: 'How is Solera different?'") 
    print("Try: 'Tell me about Solera platform'")
    print("=" * 50)
    
    while True:
        user_input = input("\n🔐 Question: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q', 'done']:
            print("🎉 Demo complete!")
            break
            
        if not user_input:
            continue
            
        prompt = f"Question: {user_input}\n\nAnswer:"
        
        response = generate(
            model, 
            tokenizer, 
            prompt=prompt,
            max_tokens=80,
            verbose=False
        )
        
        # Extract clean answer
        if "Answer:" in response:
            answer = response.split("Answer:")[-1].strip()
        else:
            answer = response.replace(prompt, "").strip()
            
        print(f"🤖 Model: {answer}")

def demo_before_after():
    """Show before/after comparison"""
    print("🎯 BEFORE/AFTER COMPARISON")
    print("=" * 50)
    
    # Base model (before training)
    print("📊 BEFORE TRAINING (Base TinyLlama):")
    base_model, base_tokenizer = load("./models/tinyllama_mlx")
    
    response = generate(base_model, base_tokenizer, prompt="What is Solera?", max_tokens=50, verbose=False)
    print(f"Base Model: {response}")
    
    print("\n📊 AFTER TRAINING (With Solera knowledge):")
    # Trained model  
    trained_model, trained_tokenizer = load(
        "./models/tinyllama_mlx",
        adapter_path="./adapters"
    )
    
    response = generate(trained_model, trained_tokenizer, prompt="Question: What is Solera?\n\nAnswer:", max_tokens=50, verbose=False)
    answer = response.split("Answer:")[-1].strip() if "Answer:" in response else response
    print(f"Trained Model: {answer}")
    
    print("\n🎯 CONCLUSION: Fine-tuning teaches the model facts that prompt engineering/RAG cannot!")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "compare":
        demo_before_after()
    else:
        demo_chat()
