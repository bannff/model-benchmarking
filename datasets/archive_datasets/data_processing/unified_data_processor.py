#!/usr/bin/env python3
"""
Unified Data Processing Pipeline
Consolidates all data cleaning, conversion, and preparation functionality.
"""

import json
import os
import re
from pathlib import Path
from datasets import Dataset, load_dataset
import pandas as pd
from typing import List, Dict, Any, Optional
import argparse
from datetime import datetime

class DataProcessor:
    """Unified data processing system for cybersecurity datasets"""
    
    def __init__(self, input_dir="cybersecurity_datasets", output_dir="processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def load_jsonl(self, file_path: Path) -> List[Dict]:
        """Load data from JSONL file"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        data.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"Warning: Skipping invalid JSON line: {e}")
        return data
    
    def save_jsonl(self, data: List[Dict], file_path: Path):
        """Save data to JSONL file"""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"Saved {len(data)} items to {file_path}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove control characters
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
        
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        
        return text
    
    def standardize_to_chat_format(self, data: List[Dict]) -> List[Dict]:
        """Convert various formats to standard chat format"""
        standardized = []
        
        for item in data:
            try:
                # Handle different input formats
                if "messages" in item:
                    # Already in chat format
                    messages = item["messages"]
                elif "conversations" in item:
                    # Conversations format
                    messages = item["conversations"]
                elif "input" in item and "output" in item:
                    # Input/output format
                    messages = [
                        {"role": "user", "content": self.clean_text(item["input"])},
                        {"role": "assistant", "content": self.clean_text(item["output"])}
                    ]
                elif "instruction" in item:
                    # Instruction format
                    instruction = self.clean_text(item["instruction"])
                    response = self.clean_text(item.get("output", item.get("response", "")))
                    
                    if item.get("input"):
                        instruction = f"{instruction}\n\n{self.clean_text(item['input'])}"
                    
                    messages = [
                        {"role": "user", "content": instruction},
                        {"role": "assistant", "content": response}
                    ]
                elif "question" in item and "answer" in item:
                    # Q&A format
                    messages = [
                        {"role": "user", "content": self.clean_text(item["question"])},
                        {"role": "assistant", "content": self.clean_text(item["answer"])}
                    ]
                elif "tokens" in item and "ner_tags" in item:
                    # NER format: convert to MLX-LM compatible format
                    tokens = item["tokens"]
                    ner_tags = item["ner_tags"]
                    if isinstance(tokens, list):
                        sentence = " ".join(tokens)
                    else:
                        sentence = str(tokens)
                    if isinstance(ner_tags, list):
                        tags = ", ".join(map(str, ner_tags))
                    else:
                        tags = str(ner_tags)
                    # Option 1: treat as user prompt and assistant response
                    messages = [
                        {"role": "user", "content": f"Sentence: {sentence}"},
                        {"role": "assistant", "content": f"NER tags: {tags}"}
                    ]
                else:
                    print(f"Warning: Unknown format for item: {list(item.keys())}")
                    continue
                
                # Validate and clean messages
                cleaned_messages = []
                for msg in messages:
                    if isinstance(msg, dict) and "role" in msg and "content" in msg:
                        role = msg["role"]
                        content = self.clean_text(str(msg["content"]))
                        
                        if content and role in ["user", "assistant", "system"]:
                            cleaned_messages.append({"role": role, "content": content})
                
                if len(cleaned_messages) >= 2:  # At least user + assistant
                    standardized.append({"messages": cleaned_messages})
                
            except Exception as e:
                print(f"Warning: Error processing item: {e}")
                continue
        
        return standardized
    
    def enhance_for_agentic_behavior(self, data: List[Dict]) -> List[Dict]:
        """Enhance data to promote agentic, helpful behavior"""
        enhanced = []
        
        # Agentic response templates
        helpful_prefixes = [
            "I'll help you with that. ",
            "Let me solve this step by step. ",
            "Here's how to approach this problem: ",
            "I can help you understand this. "
        ]
        
        for item in data:
            messages = item["messages"]
            enhanced_messages = []
            
            for i, msg in enumerate(messages):
                if msg["role"] == "assistant" and i == len(messages) - 1:
                    # Enhance the final assistant response
                    content = msg["content"]
                    
                    # Make responses more conversational and helpful
                    if not any(content.lower().startswith(prefix.lower()) for prefix in ["i'll", "let me", "here's", "i can"]):
                        # Add helpful prefix occasionally (30% of the time)
                        import random
                        if random.random() < 0.3:
                            prefix = random.choice(helpful_prefixes)
                            content = prefix + content
                    
                    # Ensure code explanations are clear
                    if "class " in content or "def " in content or "public " in content:
                        if not ("this code" in content.lower() or "this method" in content.lower()):
                            content += "\n\nThis code provides a clean, efficient solution to the problem."
                    
                    enhanced_messages.append({"role": "assistant", "content": content})
                else:
                    enhanced_messages.append(msg)
            
            enhanced.append({"messages": enhanced_messages})
        
        return enhanced
    
    def validate_data_quality(self, data: List[Dict]) -> Dict[str, Any]:
        """Validate data quality and return metrics"""
        if not data:
            return {"valid": False, "error": "No data provided"}
        
        total_samples = len(data)
        valid_samples = 0
        issues = []
        
        avg_user_length = 0
        avg_assistant_length = 0
        
        for i, item in enumerate(data):
            if "messages" not in item:
                issues.append(f"Sample {i}: Missing 'messages' field")
                continue
            
            messages = item["messages"]
            if not isinstance(messages, list) or len(messages) < 2:
                issues.append(f"Sample {i}: Invalid messages format")
                continue
            
            has_user = any(msg.get("role") == "user" for msg in messages)
            has_assistant = any(msg.get("role") == "assistant" for msg in messages)
            
            if not has_user or not has_assistant:
                issues.append(f"Sample {i}: Missing user or assistant message")
                continue
            
            # Calculate lengths
            user_msgs = [msg["content"] for msg in messages if msg.get("role") == "user"]
            assistant_msgs = [msg["content"] for msg in messages if msg.get("role") == "assistant"]
            
            if user_msgs:
                avg_user_length += len(" ".join(user_msgs))
            if assistant_msgs:
                avg_assistant_length += len(" ".join(assistant_msgs))
            
            valid_samples += 1
        
        quality_score = valid_samples / total_samples if total_samples > 0 else 0
        
        return {
            "valid": quality_score > 0.9,
            "total_samples": total_samples,
            "valid_samples": valid_samples,
            "quality_score": quality_score,
            "avg_user_length": avg_user_length / valid_samples if valid_samples > 0 else 0,
            "avg_assistant_length": avg_assistant_length / valid_samples if valid_samples > 0 else 0,
            "issues": issues[:10],  # First 10 issues
            "validation_date": datetime.now().isoformat()
        }
    
    def create_train_val_split(self, data: List[Dict], val_ratio: float = 0.1) -> tuple:
        """Create training and validation splits"""
        import random
        random.shuffle(data)
        
        split_idx = int(len(data) * (1 - val_ratio))
        train_data = data[:split_idx]
        val_data = data[split_idx:]
        
        return train_data, val_data
    
    def process_dataset(self, dataset_name: str, enhance_agentic: bool = True, val_ratio: float = 0.1):
        """Process a complete dataset"""
        print(f"\n🚀 Processing dataset: {dataset_name}")
        
        # Find dataset files
        dataset_dir = self.input_dir / dataset_name.replace("/", "_")
        if not dataset_dir.exists():
            print(f"Error: Dataset directory not found: {dataset_dir}")
            return None
        
        # Load all JSONL files
        all_data = []
        for jsonl_file in dataset_dir.glob("*.jsonl"):
            print(f"Loading {jsonl_file}...")
            data = self.load_jsonl(jsonl_file)
            all_data.extend(data)
        
        if not all_data:
            print("Error: No data found")
            return None
        
        print(f"Loaded {len(all_data)} samples")
        
        # Process data
        print("🔄 Standardizing format...")
        standardized = self.standardize_to_chat_format(all_data)
        print(f"Standardized: {len(standardized)} samples")
        
        if enhance_agentic:
            print("🤖 Enhancing for agentic behavior...")
            standardized = self.enhance_for_agentic_behavior(standardized)
        
        # Validate quality
        print("✅ Validating quality...")
        quality_metrics = self.validate_data_quality(standardized)
        
        if not quality_metrics["valid"]:
            print(f"⚠️  Quality issues detected: {quality_metrics}")
        else:
            print(f"✅ Quality validation passed: {quality_metrics['quality_score']:.2%}")
        
        # Create splits
        print("📊 Creating train/validation splits...")
        train_data, val_data = self.create_train_val_split(standardized, val_ratio)
        
        # Save processed data
        output_dataset_dir = self.output_dir / f"{dataset_name.replace('/', '_')}_processed"
        
        self.save_jsonl(train_data, output_dataset_dir / "train.jsonl")
        self.save_jsonl(val_data, output_dataset_dir / "validation.jsonl")
        
        # Save quality metrics
        with open(output_dataset_dir / "quality_metrics.json", 'w') as f:
            json.dump(quality_metrics, f, indent=2)
        
        print(f"\n✅ Processing complete!")
        print(f"  Output: {output_dataset_dir}")
        print(f"  Train samples: {len(train_data)}")
        print(f"  Validation samples: {len(val_data)}")
        print(f"  Quality score: {quality_metrics['quality_score']:.2%}")
        
        return output_dataset_dir

def main():
    parser = argparse.ArgumentParser(description="Unified data processing tool")
    parser.add_argument("dataset", help="Dataset name to process")
    parser.add_argument("--input-dir", default="cybersecurity_datasets", help="Input directory")
    parser.add_argument("--output-dir", default="processed", help="Output directory") 
    parser.add_argument("--no-agentic", action="store_true", help="Skip agentic enhancement")
    parser.add_argument("--val-ratio", type=float, default=0.1, help="Validation split ratio")
    
    args = parser.parse_args()
    
    processor = DataProcessor(args.input_dir, args.output_dir)
    result = processor.process_dataset(
        args.dataset,
        enhance_agentic=not args.no_agentic,
        val_ratio=args.val_ratio
    )
    
    if result:
        print(f"\n🎉 Successfully processed dataset: {result}")
    else:
        print("\n❌ Dataset processing failed")

if __name__ == "__main__":
    main()
