#!/usr/bin/env python3
"""
CS-Eval Benchmark Test with PHI-3 Cybersecurity Model
Simple script to test your fine-tuned PHI-3 model on the CS-Eval cybersecurity benchmark.
Uses your existing models on the Crucial X9 drive.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add MLX imports
try:
    from mlx_lm import load, generate
    import mlx.core as mx
except ImportError:
    print("❌ MLX not installed. Run: pip install mlx mlx-lm")
    sys.exit(1)

# Add dataset import
try:
    from datasets import load_dataset
except ImportError:
    print("❌ Datasets not installed. Run: pip install datasets")
    sys.exit(1)

class PHI3BenchmarkTest:
    def __init__(self):
        # Your model paths on Crucial X9
        self.base_model_path = "/Volumes/Crucial X9/ai-models/Phi-3-mini-128k-instruct-mlx"
        self.adapter_path = "/Volumes/Crucial X9/ai-models/PHI-3.5-cybersec-finetune/adapters"
        
        # Choose the latest adapter (highest number - 0001000)
        self.adapter_file = os.path.join(self.adapter_path, "0001000_adapters.safetensors")
        
        self.model = None
        self.tokenizer = None
        
    def load_model(self):
        """Load your PHI-3 model with cybersecurity adapters."""
        print(f"🔄 Loading PHI-3 model from: {self.base_model_path}")
        print(f"🔄 Loading adapters from: {self.adapter_path}")
        
        if not os.path.exists(self.base_model_path):
            print(f"❌ Base model not found at {self.base_model_path}")
            return False
            
        if not os.path.exists(self.adapter_path):
            print(f"❌ Adapter directory not found at {self.adapter_path}")
            return False
        
        try:
            # Load model with adapters
            self.model, self.tokenizer = load(
                self.base_model_path,
                adapter_path=self.adapter_path
            )
            print("✅ Model loaded successfully!")
            return True
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            return False
    
    def test_model(self):
        """Test the model with a cybersecurity question."""
        print("\n🧪 Testing model with cybersecurity question...")
        
        prompt = """<|system|>
You are a cybersecurity expert. Answer the following multiple choice question with just the letter (A, B, C, or D).
<|end|>
<|user|>
What is the primary purpose of a firewall in network security?

A. To encrypt data in transit
B. To filter network traffic based on security rules
C. To detect malware in files
D. To manage user authentication

Answer:
<|end|>
<|assistant|>
"""
        
        try:
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=10,
                verbose=False
            )
            
            print(f"✅ Model response: {response.strip()}")
            return True
        except Exception as e:
            print(f"❌ Error testing model: {e}")
            return False
    
    def run_cs_eval_sample(self, num_questions=10):
        """Run a small sample of CS-Eval questions."""
        print(f"\n📊 Running CS-Eval sample ({num_questions} questions)...")
        
        try:
            # Load CS-Eval dataset  
            print("🔄 Loading CS-Eval dataset...")
            dataset = load_dataset("cseval/cs-eval", split=f"test[:{num_questions}]")
            print(f"✅ Loaded {len(dataset)} questions")
            
            results = []
            correct = 0
            
            for i, item in enumerate(dataset):
                print(f"\n📝 Question {i+1}/{len(dataset)}")
                
                # Format question
                question = item['question']
                options = [item['A'], item['B'], item['C'], item['D']]
                correct_answer = item['answer']
                
                print(f"Q: {question}")
                for j, option in enumerate(options):
                    print(f"   {chr(65+j)}. {option}")
                
                # Create prompt
                prompt = f"""<|system|>
You are a cybersecurity expert. Answer the following multiple choice question with just the letter (A, B, C, or D).
<|end|>
<|user|>
{question}

A. {options[0]}
B. {options[1]}
C. {options[2]}
D. {options[3]}

Answer:
<|end|>
<|assistant|>
"""
                
                # Get model response
                try:
                    response = generate(
                        self.model,
                        self.tokenizer,
                        prompt=prompt,
                        max_tokens=5,
                        verbose=False
                    ).strip()
                    
                    # Extract answer (look for A, B, C, or D)
                    predicted_answer = None
                    for char in ['A', 'B', 'C', 'D']:
                        if char in response.upper():
                            predicted_answer = char
                            break
                    
                    if predicted_answer is None:
                        predicted_answer = 'A'  # Default fallback
                    
                    is_correct = predicted_answer == correct_answer
                    if is_correct:
                        correct += 1
                    
                    print(f"   Model: {predicted_answer} | Correct: {correct_answer} | {'✅' if is_correct else '❌'}")
                    
                    results.append({
                        'question': question,
                        'options': options,
                        'predicted': predicted_answer,
                        'correct': correct_answer,
                        'is_correct': is_correct,
                        'raw_response': response
                    })
                    
                except Exception as e:
                    print(f"   ❌ Error with question {i+1}: {e}")
                    continue
            
            # Calculate results
            accuracy = correct / len(results) if results else 0
            
            print(f"\n🎉 Sample Evaluation Complete!")
            print(f"📊 Accuracy: {accuracy:.2%} ({correct}/{len(results)})")
            
            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = f"cs_eval_sample_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump({
                    'timestamp': timestamp,
                    'model': 'PHI-3-cybersec',
                    'num_questions': len(results),
                    'accuracy': accuracy,
                    'correct': correct,
                    'results': results
                }, f, indent=2)
            
            print(f"💾 Results saved to: {results_file}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error running CS-Eval: {e}")
            return False

def main():
    """Main function."""
    print("🚀 PHI-3 Cybersecurity Model - CS-Eval Benchmark Test")
    print("=" * 60)
    
    # Initialize benchmark
    benchmark = PHI3BenchmarkTest()
    
    # Load model
    if not benchmark.load_model():
        print("❌ Failed to load model. Exiting.")
        return
    
    # Test model
    if not benchmark.test_model():
        print("❌ Model test failed. Exiting.")
        return
    
    # Run CS-Eval sample
    print("\n" + "="*60)
    choice = input("Run CS-Eval sample? (10 questions) [y/N]: ")
    if choice.lower() == 'y':
        benchmark.run_cs_eval_sample(10)
    
    print("\n✅ Benchmark test complete!")

if __name__ == "__main__":
    main()
