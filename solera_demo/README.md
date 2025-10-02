# 🎯 SOLERA FINE-TUNING DEMO
## Complete Self-Contained Package

### 🚀 **Demo Concept**
Show that fine-tuning can teach a model "secrets" that prompt engineering and RAG cannot access, using Solera as the secret knowledge.

### � **What's Included**
- Complete training dataset (10 examples)
- TinyLlama model download script
- All dependencies setup
- 3-step demo workflow

### 🛠️ **Setup (Run Once)**
```bash
./0_setup.sh
```
This will:
- Install MLX-LM and dependencies
- Download TinyLlama model
- Set up everything needed

### 📋 **Demo Flow (2-3 minutes + training)**

#### **Step 1: Show Base Model Doesn't Know (30 seconds)**
```bash
python3 1_demo_base_model.py
```
Ask: "What is Solera?" → Should give generic/wrong answer

#### **Step 2: Live Training (35 seconds)**  
```bash
./2_run_training.sh
```
Watch the model learn the secret in real-time!

#### **Step 3: Show Trained Model Knows the Secret (30 seconds)**
```bash
python3 3_demo_trained_model.py
```
Ask: "What is Solera?" → Should give the exact secret knowledge!

### 🎯 **Key Demo Points**

1. **Impossible with RAG**: "This knowledge doesn't exist anywhere online"
2. **Impossible with Prompting**: "No prompt could make the model know this"  
3. **Only Fine-tuning Works**: "We literally taught the model new facts"
4. **Fast & Effective**: "100 iterations, 10 examples, 35 seconds = learned knowledge"

### 📊 **Expected Results**
- **Before**: Model says "I don't know" or gives generic business advice
- **After**: Model gives exact secret: "Solera is an Agentic AI platform to build security tools that's going to be way better than everyone else's agentic AI platform because it's not dumb and will be recursively learning..."

### � **Requirements**
- Apple Silicon Mac (M1/M2/M3)
- Python 3.9+
- ~2GB disk space for model
- ~5 minutes total time

### 🎉 **Demo Impact**
Perfect demonstration that fine-tuning is the only way to teach models new factual knowledge that doesn't exist in training data or external sources.
