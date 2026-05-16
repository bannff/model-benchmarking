#!/usr/bin/env python3
"""
Simple Cybersecurity Quiz for PHI-3 Model

Test your fine-tuned PHI-3 cybersecurity model with a curated set of 
cybersecurity multiple choice questions.
"""

import os
import sys
import json
from datetime import datetime

# Add MLX imports
try:
    from mlx_lm import load, generate
    import mlx.core as mx
except ImportError:
    print("❌ MLX not installed. Run: pip install mlx mlx-lm")
    sys.exit(1)

# Cybersecurity quiz questions
CYBERSEC_QUIZ = [
    {
        "question": "What is the primary purpose of a firewall in network security?",
        "options": [
            "To encrypt data in transit",
            "To filter network traffic based on security rules",
            "To detect malware in files", 
            "To manage user authentication"
        ],
        "correct": "B",
        "category": "Network Security"
    },
    {
        "question": "Which cryptographic algorithm is considered quantum-resistant?",
        "options": [
            "RSA-2048",
            "Elliptic Curve Cryptography (ECC)",
            "Lattice-based cryptography",
            "SHA-256"
        ],
        "correct": "C",
        "category": "Cryptography"
    },
    {
        "question": "What type of attack involves sending more data to a buffer than it can handle?",
        "options": [
            "SQL Injection",
            "Cross-Site Scripting (XSS)",
            "Buffer Overflow",
            "Man-in-the-Middle"
        ],
        "correct": "C",
        "category": "System Security"
    },
    {
        "question": "Which HTTP header helps prevent clickjacking attacks?",
        "options": [
            "Content-Security-Policy",
            "X-Frame-Options",
            "Strict-Transport-Security",
            "X-XSS-Protection"
        ],
        "correct": "B",
        "category": "Web Security"
    },
    {
        "question": "In the context of penetration testing, what does the term 'pivot' refer to?",
        "options": [
            "Changing the attack methodology",
            "Using a compromised system to attack other systems",
            "Rotating encryption keys",
            "Switching between vulnerability scanners"
        ],
        "correct": "B",
        "category": "Penetration Testing"
    },
    {
        "question": "What is the main difference between symmetric and asymmetric encryption?",
        "options": [
            "Symmetric is faster, asymmetric is more secure",
            "Symmetric uses one key, asymmetric uses two keys",
            "Symmetric works with text, asymmetric works with files",
            "There is no significant difference"
        ],
        "correct": "B",
        "category": "Cryptography"
    },
    {
        "question": "Which of the following is NOT a common indicator of compromise (IoC)?",
        "options": [
            "Unusual network traffic patterns",
            "Unexpected system reboots",
            "High CPU usage during normal operations",
            "Regular software updates"
        ],
        "correct": "D",
        "category": "Incident Response"
    },
    {
        "question": "What does the principle of 'least privilege' mean in cybersecurity?",
        "options": [
            "Users should have minimal system access needed for their job",
            "Passwords should be as short as possible",
            "Network traffic should be minimized",
            "Security controls should be barely noticeable"
        ],
        "correct": "A",
        "category": "Access Control"
    },
    {
        "question": "Which technique is commonly used to bypass application security controls?",
        "options": [
            "Input validation",
            "Parameter tampering",
            "SSL/TLS encryption",
            "Multi-factor authentication"
        ],
        "correct": "B",
        "category": "Application Security"
    },
    {
        "question": "What is the primary goal of a DDoS attack?",
        "options": [
            "To steal sensitive data",
            "To gain unauthorized access to systems",
            "To make services unavailable to legitimate users",
            "To install malware on target systems"
        ],
        "correct": "C",
        "category": "Network Security"
    }
]

class PHI3CyberSecQuiz:
    def __init__(self):
        # Your model paths on Crucial X9
        self.base_model_path = "/Volumes/Crucial X9/ai-models/Phi-3-mini-128k-instruct-mlx"
        self.adapter_path = "/Volumes/Crucial X9/ai-models/PHI-3.5-cybersec-finetune/adapters"
        
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
    
    def ask_question(self, question_data):
        """Ask the model a single question."""
        question = question_data["question"]
        options = question_data["options"]
        
        # Format prompt
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
        
        try:
            response = generate(
                self.model,
                self.tokenizer,
                prompt=prompt,
                max_tokens=5,
                verbose=False
            ).strip()
            
            # Extract answer letter
            predicted_answer = None
            for char in ['A', 'B', 'C', 'D']:
                if char in response.upper():
                    predicted_answer = char
                    break
            
            if predicted_answer is None:
                predicted_answer = 'A'  # Default fallback
            
            return predicted_answer, response
            
        except Exception as e:
            print(f"❌ Error asking question: {e}")
            return None, str(e)
    
    def run_quiz(self):
        """Run the complete cybersecurity quiz."""
        print(f"\n🧪 Starting Cybersecurity Quiz ({len(CYBERSEC_QUIZ)} questions)...")
        
        results = []
        correct = 0
        
        for i, question_data in enumerate(CYBERSEC_QUIZ):
            print(f"\n📝 Question {i+1}/{len(CYBERSEC_QUIZ)} [{question_data['category']}]")
            print(f"Q: {question_data['question']}")
            
            for j, option in enumerate(question_data['options']):
                print(f"   {chr(65+j)}. {option}")
            
            # Get model answer
            predicted, raw_response = self.ask_question(question_data)
            correct_answer = question_data['correct']
            
            if predicted:
                is_correct = predicted == correct_answer
                if is_correct:
                    correct += 1
                
                print(f"   Model: {predicted} | Correct: {correct_answer} | {'✅' if is_correct else '❌'}")
                
                results.append({
                    'question_number': i+1,
                    'category': question_data['category'],
                    'question': question_data['question'],
                    'options': question_data['options'],
                    'predicted': predicted,
                    'correct': correct_answer,
                    'is_correct': is_correct,
                    'raw_response': raw_response
                })
            else:
                print(f"   ❌ Failed to get response")
        
        # Calculate final results
        accuracy = correct / len(results) if results else 0
        
        print(f"\n🎉 Quiz Complete!")
        print(f"📊 Final Score: {accuracy:.1%} ({correct}/{len(results)})")
        
        # Show category breakdown
        categories = {}
        for result in results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'correct': 0, 'total': 0}
            categories[cat]['total'] += 1
            if result['is_correct']:
                categories[cat]['correct'] += 1
        
        print(f"\n📋 Category Breakdown:")
        for category, stats in sorted(categories.items()):
            cat_accuracy = stats['correct'] / stats['total'] if stats['total'] > 0 else 0
            print(f"   • {category}: {cat_accuracy:.1%} ({stats['correct']}/{stats['total']})")
        
        # Save results
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"cybersec_quiz_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            json.dump({
                'timestamp': timestamp,
                'model': 'PHI-3-cybersec',
                'total_questions': len(results),
                'accuracy': accuracy,
                'correct_answers': correct,
                'category_breakdown': categories,
                'detailed_results': results
            }, f, indent=2)
        
        print(f"💾 Results saved to: {results_file}")
        
        return results

def main():
    """Main function."""
    print("🚀 PHI-3 Cybersecurity Model - Quiz Test")
    print("=" * 50)
    
    # Initialize quiz
    quiz = PHI3CyberSecQuiz()
    
    # Load model
    if not quiz.load_model():
        print("❌ Failed to load model. Exiting.")
        return
    
    # Run quiz
    quiz.run_quiz()
    
    print("\n✅ Quiz complete!")

if __name__ == "__main__":
    main()
