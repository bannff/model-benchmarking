#!/usr/bin/env python3
"""
Quick chat interface to test the current Mamba adapter
"""
import mlx_lm

def chat_with_adapter():
    print("Loading Mamba model with your cybersecurity adapter...")
    
    # Load the model with adapter
    try:
        model, tokenizer = mlx_lm.load("./cybersecurity_finetuned_models/mamba_cybersec_adapter")
        print("✅ Adapter loaded successfully!")
        print("   Using cybersecurity fine-tuned model from 1500 training steps")
    except Exception as e:
        print(f"❌ Error loading adapter: {e}")
        print("Trying base model instead...")
        model, tokenizer = mlx_lm.load("models/mamba-1.4b-mlx")
        print("✅ Base model loaded (no adapter)")
    
    print("\n🔒 Cybersecurity Chat - Type 'quit' to exit")
    print("Ask me about cybersecurity topics!\n")
    
    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ['quit', 'exit', 'q']:
            break
        
        if not user_input:
            continue
        
        # Format as instruction
        prompt = f"User: {user_input}\nAssistant:"
        
        try:
            response = mlx_lm.generate(
                model, tokenizer,
                prompt=prompt,
                max_tokens=200,
                verbose=False
            )
            
            # Extract just the assistant's response
            if "Assistant:" in response:
                assistant_response = response.split("Assistant:")[-1].strip()
            else:
                assistant_response = response.strip()
                
            print(f"Assistant: {assistant_response}\n")
            
        except Exception as e:
            print(f"❌ Error generating response: {e}\n")

if __name__ == "__main__":
    chat_with_adapter()
