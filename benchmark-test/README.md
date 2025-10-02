# CS-Eval Benchmark Test

Simple test script to evaluate your PHI-3 cybersecurity model on the CS-Eval benchmark.

## What this does:

1. **Loads your existing PHI-3 model** from `/Volumes/Crucial X9/ai-models/Phi-3-mini-128k-instruct-mlx`
2. **Applies your cybersecurity adapters** from `/Volumes/Crucial X9/ai-models/adapters` (uses the latest 0000600 checkpoint)
3. **Tests the model** with a simple cybersecurity question
4. **Runs a sample of CS-Eval questions** (10 questions by default)
5. **Calculates accuracy** and saves results

## Requirements:

```bash
pip install mlx mlx-lm datasets
```

## Usage:

```bash
python cs_eval_test.py
```

## Expected Output:

```
🚀 PHI-3 Cybersecurity Model - CS-Eval Benchmark Test
============================================================
🔄 Loading PHI-3 model from: /Volumes/Crucial X9/ai-models/Phi-3-mini-128k-instruct-mlx
🔄 Loading adapters from: /Volumes/Crucial X9/ai-models/adapters/0000600_adapters.safetensors
✅ Model loaded successfully!

🧪 Testing model with cybersecurity question...
✅ Model response: B

📊 Running CS-Eval sample (10 questions)...
🔄 Loading CS-Eval dataset...
✅ Loaded 10 questions

📝 Question 1/10
Q: What is the primary purpose of a firewall in network security?
   A. To encrypt data in transit
   B. To filter network traffic based on security rules
   C. To detect malware in files
   D. To manage user authentication
   Model: B | Correct: B | ✅
...

🎉 Sample Evaluation Complete!
📊 Accuracy: 80.00% (8/10)
💾 Results saved to: cs_eval_sample_20250805_143022.json
```

This gives you a quick way to test your cybersecurity model performance on the CS-Eval benchmark!
