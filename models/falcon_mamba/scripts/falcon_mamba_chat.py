#!/usr/bin/env python3
"""
Falcon-Mamba 7B Chat Interface
Tests the trained cybersecurity model
"""

from mlx_lm import load, generate
import sys

def main():
    print("🚀 FALCON-MAMBA 7B CYBERSECURITY CHAT")
    print("=" * 50)
    print("🤖 Loading Falcon-Mamba with cybersecurity training...")
    
    try:
        # Load pre-converted MLX Falcon-Mamba model from HuggingFace
        model_path = "mlx-community/falcon-mamba-7b-4bit-instruct"
        print(f"📍 Loading model from: {model_path}")
        
        model, tokenizer = load(model_path)
        print("✅ Model loaded successfully!")
        
    except Exception as e:
        print(f"❌ Error loading model: {e}")
        print("💡 Make sure the model path is correct")
        sys.exit(1)
    
    print("\n🔐 CYBERSECURITY KNOWLEDGE TEST")
    print("Ask about security concepts, vulnerabilities, tools, etc.")
    print("Type 'quit' to exit")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n🔍 Security Question: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_input:
                continue
            
            # Format prompt for Falcon-Mamba instruct format
            if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template is not None:
                messages = [{"role": "user", "content": user_input}]
                prompt = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            else:
                prompt = f"### Human: {user_input}\n\n### Assistant:"
            
            print("\n🤖 Falcon-Mamba:", end=" ")
            
            # Generate response
            response = generate(
                model, 
                tokenizer, 
                prompt=prompt,
                max_tokens=512,
                verbose=False
            )
            
            # Clean up response
            if "### Assistant:" in response:
                answer = response.split("### Assistant:")[-1].strip()
            elif "### Human:" in response:
                # Remove the original question if it got repeated
                parts = response.split("### Human:")
                if len(parts) > 1:
                    answer = parts[-1].split("### Assistant:")[-1].strip()
                else:
                    answer = response.strip()
            else:
                answer = response.replace(prompt, "").strip()
            
            print(answer)
            
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error generating response: {e}")

def test_knowledge():
    """Quick test of cybersecurity knowledge"""
    print("\n🧪 QUICK KNOWLEDGE TEST")
    print("-" * 30)
    
    test_questions = [
        "What is a SQL injection attack?",
        "Explain the difference between symmetric and asymmetric encryption",
        "What is a zero-day vulnerability?",
        "How does a buffer overflow attack work?",
        "What is the principle of least privilege?"
    ]
    
    try:
        model, tokenizer = load(
            "mlx-community/falcon-mamba-7b-4bit-instruct",
            adapter_path="./adapters"
        )
        
        for i, question in enumerate(test_questions, 1):
            print(f"\n{i}. {question}")
            
            if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template is not None:
                messages = [{"role": "user", "content": question}]
                prompt = tokenizer.apply_chat_template(
                    messages, tokenize=False, add_generation_prompt=True
                )
            else:
                prompt = f"### Human: {question}\n\n### Assistant:"
            
            response = generate(
                model, 
                tokenizer, 
                prompt=prompt,
                max_tokens=200,
                verbose=False
            )
            
            # Clean response
            if "### Assistant:" in response:
                answer = response.split("### Assistant:")[-1].strip()
            else:
                answer = response.replace(prompt, "").strip()
            
            print(f"📝 Answer: {answer}")
            
    except Exception as e:
        print(f"❌ Error in knowledge test: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_knowledge()
    else:
        main()
