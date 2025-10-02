#!/usr/bin/env python3
"""
Model Comparison: Falcon-Mamba vs TinyLlama
Evaluates cybersecurity knowledge between the two trained models
"""

from mlx_lm import load, generate
import time
import json

def load_models():
    """Load both trained models for comparison"""
    print("🔄 Loading models for comparison...")
    
    # TinyLlama
    print("📥 Loading TinyLlama...")
    tinyllama_model, tinyllama_tokenizer = load(
        "/Users/danielrodrigo/Workspace/PyScience/datasets/mlx_models/tinyllama_mlx",
        adapter_path="/Users/danielrodrigo/Workspace/PyScience/datasets/cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1"
    )
    
    # Falcon-Mamba
    print("📥 Loading Falcon-Mamba...")
    falcon_model, falcon_tokenizer = load(
        "mlx-community/falcon-mamba-7b-4bit-instruct",
        adapter_path="/Users/danielrodrigo/Workspace/PyScience/falcon_mamba_training/adapters"
    )
    
    return (tinyllama_model, tinyllama_tokenizer), (falcon_model, falcon_tokenizer)

def generate_response(model, tokenizer, question, model_name):
    """Generate response from a model"""
    start_time = time.time()
    
    # Format prompt based on model
    if "falcon" in model_name.lower():
        if hasattr(tokenizer, "apply_chat_template") and tokenizer.chat_template is not None:
            messages = [{"role": "user", "content": question}]
            prompt = tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
        else:
            prompt = f"### Human: {question}\n\n### Assistant:"
    else:
        prompt = f"Question: {question}\n\nAnswer:"
    
    # Generate
    response = generate(
        model, 
        tokenizer, 
        prompt=prompt,
        max_tokens=300,
        verbose=False,
        temp=0.7
    )
    
    # Clean response
    if "### Assistant:" in response:
        answer = response.split("### Assistant:")[-1].strip()
    elif "Answer:" in response:
        answer = response.split("Answer:")[-1].strip()
    else:
        answer = response.replace(prompt, "").strip()
    
    generation_time = time.time() - start_time
    
    return answer, generation_time

def run_comparison():
    """Run comprehensive comparison between models"""
    
    cybersecurity_questions = [
        "What is a SQL injection attack and how can it be prevented?",
        "Explain the difference between symmetric and asymmetric encryption",
        "What is a zero-day vulnerability and why is it dangerous?",
        "How does a buffer overflow attack work?",
        "What is the principle of least privilege in cybersecurity?",
        "Describe how a man-in-the-middle attack operates",
        "What is the difference between authentication and authorization?",
        "Explain what a DDoS attack is and common mitigation strategies",
        "What is social engineering in the context of cybersecurity?",
        "How do firewalls protect network security?"
    ]
    
    try:
        # Load models
        (tinyllama_model, tinyllama_tokenizer), (falcon_model, falcon_tokenizer) = load_models()
        
        print("\n🔬 CYBERSECURITY KNOWLEDGE COMPARISON")
        print("=" * 60)
        
        results = []
        
        for i, question in enumerate(cybersecurity_questions, 1):
            print(f"\n📋 Question {i}: {question}")
            print("-" * 50)
            
            # TinyLlama response
            print("🔍 TinyLlama thinking...")
            tiny_answer, tiny_time = generate_response(
                tinyllama_model, tinyllama_tokenizer, question, "tinyllama"
            )
            
            # Falcon-Mamba response
            print("🔍 Falcon-Mamba thinking...")
            falcon_answer, falcon_time = generate_response(
                falcon_model, falcon_tokenizer, question, "falcon-mamba"
            )
            
            # Display results
            print(f"\n🤖 TinyLlama ({tiny_time:.2f}s):")
            print(f"   {tiny_answer}")
            
            print(f"\n🚀 Falcon-Mamba ({falcon_time:.2f}s):")
            print(f"   {falcon_answer}")
            
            # Store results
            results.append({
                "question": question,
                "tinyllama": {
                    "answer": tiny_answer,
                    "time": tiny_time
                },
                "falcon_mamba": {
                    "answer": falcon_answer,
                    "time": falcon_time
                }
            })
            
            # Brief pause between questions
            time.sleep(1)
        
        # Save results
        with open("model_comparison_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        # Summary statistics
        print("\n📊 PERFORMANCE SUMMARY")
        print("=" * 40)
        
        avg_tiny_time = sum(r["tinyllama"]["time"] for r in results) / len(results)
        avg_falcon_time = sum(r["falcon_mamba"]["time"] for r in results) / len(results)
        
        print(f"⏱️  Average Response Time:")
        print(f"   TinyLlama: {avg_tiny_time:.2f}s")
        print(f"   Falcon-Mamba: {avg_falcon_time:.2f}s")
        print(f"   Speed Ratio: {avg_falcon_time/avg_tiny_time:.1f}x slower")
        
        print(f"\n📏 Response Length:")
        avg_tiny_len = sum(len(r["tinyllama"]["answer"]) for r in results) / len(results)
        avg_falcon_len = sum(len(r["falcon_mamba"]["answer"]) for r in results) / len(results)
        print(f"   TinyLlama: {avg_tiny_len:.0f} chars")
        print(f"   Falcon-Mamba: {avg_falcon_len:.0f} chars")
        
        print(f"\n💾 Results saved to: model_comparison_results.json")
        
    except Exception as e:
        print(f"❌ Comparison error: {e}")
        print("💡 Make sure both models are trained and available")

def quick_test():
    """Quick single question test"""
    question = "What is a SQL injection attack?"
    
    try:
        (tinyllama_model, tinyllama_tokenizer), (falcon_model, falcon_tokenizer) = load_models()
        
        print(f"\n🧪 QUICK TEST: {question}")
        print("=" * 50)
        
        # Test both models
        tiny_answer, tiny_time = generate_response(
            tinyllama_model, tinyllama_tokenizer, question, "tinyllama"
        )
        
        falcon_answer, falcon_time = generate_response(
            falcon_model, falcon_tokenizer, question, "falcon-mamba"
        )
        
        print(f"\n🤖 TinyLlama ({tiny_time:.2f}s):")
        print(f"   {tiny_answer}")
        
        print(f"\n🚀 Falcon-Mamba ({falcon_time:.2f}s):")
        print(f"   {falcon_answer}")
        
    except Exception as e:
        print(f"❌ Quick test error: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_test()
    else:
        run_comparison()
