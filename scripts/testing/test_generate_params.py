#!/usr/bin/env python3
"""
Simple test to determine the correct MLX-LM generate parameters
"""

import sys
import os
sys.path.append('/Users/danielrodrigo/Workspace/PyScience')

from mlx_lm import load, generate

def test_generate_params():
    print("Loading model to test generate parameters...")
    
    base_model_path = "/Users/danielrodrigo/Workspace/PyScience/datasets/mlx_models/tinyllama_mlx"
    adapter_path = "/Users/danielrodrigo/Workspace/PyScience/cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1"
    
    try:
        model, tokenizer = load(base_model_path, adapter_path=adapter_path)
        print("✅ Model loaded successfully!")
        
        prompt = "What is cybersecurity?"
        
        # Try with just the basic parameters
        print("Testing basic generate call...")
        try:
            response = generate(model, tokenizer, prompt=prompt, max_tokens=50)
            print(f"✅ Basic generate works: {response[:100]}...")
            return
        except Exception as e:
            print(f"❌ Basic generate failed: {e}")
        
        # Try with different parameter names
        print("Testing with different parameter combinations...")
        
        test_params = [
            {"max_tokens": 50},
            {"max_length": 50},
            {"max_new_tokens": 50},
            {"temp": 0.7, "max_tokens": 50},
            {"temperature": 0.7, "max_tokens": 50},
        ]
        
        for i, params in enumerate(test_params):
            try:
                print(f"Testing params {i+1}: {params}")
                response = generate(model, tokenizer, prompt=prompt, **params)
                print(f"✅ Success with params {params}: {response[:50]}...")
                return
            except Exception as e:
                print(f"❌ Failed with params {params}: {e}")
                
    except Exception as e:
        print(f"❌ Failed to load model: {e}")

if __name__ == "__main__":
    test_generate_params()
