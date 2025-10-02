#!/usr/bin/env python3
"""
CS-Eval Cybersecurity Benchmark with PHI-3 Model
Official CS-Eval benchmark test with your fine-tuned PHI-3 cybersecurity model.
Uses the real CS-Eval dataset from Hugging Face.
"""

import os
import sys
import json
import re
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

class PHI3CSEval:
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
    
    def load_cs_eval_dataset(self, max_questions=1000):
        """Load CS-Eval dataset and filter for English questions."""
        print(f"🔄 Loading CS-Eval dataset...")
        
        try:
            # Load full test dataset
            dataset = load_dataset("cseval/cs-eval", split="test")
            print(f"✅ Loaded {len(dataset)} total CS-Eval questions")
            
            # Filter for English questions only
            english_questions = []
            for item in dataset:
                prompt = item['prompt']
                # Check if it's an English question
                if ('Single-choice question:' in prompt or 
                    'Multiple-choice question:' in prompt or
                    'True or False:' in prompt) and re.search(r'[A-Za-z]', prompt):
                    english_questions.append(item)
                    
                    if len(english_questions) >= max_questions:
                        break
            
            print(f"✅ Found {len(english_questions)} English questions (using {min(len(english_questions), max_questions)})")
            return english_questions[:max_questions]
            
        except Exception as e:
            print(f"❌ Error loading CS-Eval dataset: {e}")
            return []
    
    def parse_question(self, item):
        """Parse a CS-Eval question item."""
        prompt = item['prompt']
        question_id = item['id']
        category = item['top_category']
        subcategory = item['sub_category']
        
        # Determine question type
        if 'Single-choice question:' in prompt:
            question_type = 'single_choice'
        elif 'Multiple-choice question:' in prompt or '多选题：' in prompt:
            question_type = 'multiple_choice'
        elif 'True or False:' in prompt:
            question_type = 'true_false'
        else:
            question_type = 'other'
        
        # Extract the actual question and options
        lines = prompt.split('\n')
        question_text = ""
        options = []
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith(('Single-choice', 'Multiple-choice', 'True or False', 'Please provide')):
                if re.match(r'^[A-D]\)', line) or re.match(r'^[A-D]\.', line):
                    # This is an option
                    options.append(line[2:].strip())  # Remove "A) " or "A. "
                elif not options:  # This is the question text
                    question_text += line + " "
        
        return {
            'id': question_id,
            'question': question_text.strip(),
            'options': options,
            'question_type': question_type,
            'category': category,
            'subcategory': subcategory,
            'original_prompt': prompt
        }
    
    def ask_question(self, question_data):
        """Ask the model a CS-Eval question."""
        question = question_data['question']
        options = question_data['options']
        question_type = question_data['question_type']
        
        if question_type == 'single_choice' and options:
            # Format as multiple choice
            prompt = f"""<|system|>
You are a cybersecurity expert. Answer the following multiple choice question with just the letter (A, B, C, or D).
<|end|>
<|user|>
{question}

A. {options[0] if len(options) > 0 else 'N/A'}
B. {options[1] if len(options) > 1 else 'N/A'}
C. {options[2] if len(options) > 2 else 'N/A'}
D. {options[3] if len(options) > 3 else 'N/A'}

Answer:
<|end|>
<|assistant|>
"""
        elif question_type == 'true_false':
            prompt = f"""<|system|>
You are a cybersecurity expert. Answer the following true/false question with just "True" or "False".
<|end|>
<|user|>
{question}

Answer (True or False):
<|end|>
<|assistant|>
"""
        else:
            # General format
            prompt = f"""<|system|>
You are a cybersecurity expert. Answer the following cybersecurity question concisely.
<|end|>
<|user|>
{question}
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
            ).strip()
            
            # Parse response based on question type
            if question_type == 'single_choice':
                # Extract answer letter
                for char in ['A', 'B', 'C', 'D']:
                    if char in response.upper():
                        return char, response
                return 'A', response  # Default fallback
            elif question_type == 'true_false':
                if 'TRUE' in response.upper():
                    return 'True', response
                elif 'FALSE' in response.upper():
                    return 'False', response
                return 'True', response  # Default fallback
            else:
                return response, response
            
        except Exception as e:
            print(f"❌ Error asking question: {e}")
            return None, str(e)
    
    def run_cs_eval(self, max_questions=1000):
        """Run CS-Eval benchmark evaluation."""
        print(f"\n📊 Starting CS-Eval Cybersecurity Benchmark...")
        
        # Load dataset
        questions = self.load_cs_eval_dataset(max_questions)
        if not questions:
            print("❌ No questions loaded. Exiting.")
            return
        
        results = []
        correct = 0  # Note: We don't have ground truth for CS-Eval, so this is placeholder
        
        for i, item in enumerate(questions):
            question_data = self.parse_question(item)
            
            # Show progress every 50 questions
            if i % 50 == 0 or i < 10:
                print(f"\n📝 Question {i+1}/{len(questions)} [ID: {question_data['id']}]")
                print(f"Category: {question_data['category']} / {question_data['subcategory']}")
                print(f"Type: {question_data['question_type']}")
                print(f"Q: {question_data['question'][:100]}...")
                
                if question_data['options']:
                    for j, option in enumerate(question_data['options']):
                        print(f"   {chr(65+j)}. {option[:50]}...")
            elif i % 10 == 0:
                print(f"⏳ Progress: {i+1}/{len(questions)} questions processed...")
            
            # Get model answer
            predicted, raw_response = self.ask_question(question_data)
            
            if predicted:
                if i % 50 == 0 or i < 10:
                    print(f"   Model Answer: {predicted}")
                
                # Save result in CS-Eval submission format
                result = {
                    'question_id': str(question_data['id']),
                    'answer': predicted,
                    'category': question_data['category'],
                    'subcategory': question_data['subcategory'],
                    'question_type': question_data['question_type'],
                    'raw_response': raw_response,
                    'question_text': question_data['question']
                }
                results.append(result)
            else:
                if i % 50 == 0 or i < 10:
                    print(f"   ❌ Failed to get response")
        
        # Generate submission file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # CS-Eval submission format (just question_id and answer)
        submission_data = [
            {"question_id": result['question_id'], "answer": result['answer']} 
            for result in results
        ]
        
        submission_file = f"cs_eval_submission_{timestamp}.json"
        with open(submission_file, 'w', encoding='utf-8') as f:
            json.dump(submission_data, f, indent=2, ensure_ascii=False)
        
        # Detailed results file
        detailed_file = f"cs_eval_detailed_{timestamp}.json"
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': timestamp,
                'model': 'PHI-3-cybersec',
                'total_questions': len(results),
                'submission_file': submission_file,
                'detailed_results': results
            }, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 CS-Eval Evaluation Complete!")
        print(f"📊 Questions Evaluated: {len(results)}")
        print(f"💾 Submission file: {submission_file}")
        print(f"💾 Detailed results: {detailed_file}")
        
        # Show category breakdown
        categories = {}
        for result in results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = 0
            categories[cat] += 1
        
        print(f"\n📋 Category Breakdown:")
        for category, count in sorted(categories.items()):
            print(f"   • {category}: {count} questions")
        
        print(f"\n💡 Next steps:")
        print(f"   1. Submit {submission_file} to https://cs-eval.com/")
        print(f"   2. Compare results with leaderboard models")
        print(f"   3. Analyze performance by category")
        
        return results

def main():
    """Main function."""
    print("🚀 PHI-3 Cybersecurity Model - CS-Eval Benchmark")
    print("=" * 60)
    
    # Initialize evaluation
    cs_eval = PHI3CSEval()
    
    # Load model
    if not cs_eval.load_model():
        print("❌ Failed to load model. Exiting.")
        return
    
    # Get number of questions to evaluate
    try:
        max_q = input("\nHow many questions to evaluate? [1000]: ").strip()
        max_questions = int(max_q) if max_q else 1000
    except:
        max_questions = 1000
    
    # Run CS-Eval
    cs_eval.run_cs_eval(max_questions)
    
    print("\n✅ CS-Eval benchmark complete!")

if __name__ == "__main__":
    main()
