#!/usr/bin/env python3
"""
Data cleaning and transformation pipeline to create high-quality agentic cybersecurity datasets.
Transforms downloaded datasets to match Heimdall format quality standards.
"""

import json
import pandas as pd
from datasets import Dataset, load_from_disk
from pathlib import Path
import re
from typing import Dict, List, Any

class CybersecurityDataProcessor:
    """Process and clean cybersecurity datasets for agentic fine-tuning"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.output_dir = self.base_dir / "processed"
        self.output_dir.mkdir(exist_ok=True)
        
    def load_heimdall_reference(self) -> List[Dict]:
        """Load a sample of the high-quality Heimdall reference data"""
        reference_path = "/Users/danielrodrigo/Workspace/CloScience/data/heimdall_merged_cleaned.jsonl"
        
        samples = []
        with open(reference_path, 'r') as f:
            for i, line in enumerate(f):
                if i >= 100:  # Load 100 samples for analysis
                    break
                samples.append(json.loads(line))
        
        return samples
    
    def analyze_reference_quality(self, samples: List[Dict]) -> Dict:
        """Analyze the quality characteristics of reference Heimdall data"""
        
        quality_metrics = {
            'avg_user_length': 0,
            'avg_assistant_length': 0,
            'has_code_percentage': 0,
            'avg_conversation_turns': 0,
            'common_patterns': [],
            'instruction_types': []
        }
        
        user_lengths = []
        assistant_lengths = []
        code_count = 0
        turn_counts = []
        
        for sample in samples:
            messages = sample['messages']
            turn_counts.append(len(messages))
            
            for msg in messages:
                content = msg['content']
                if msg['role'] == 'user':
                    user_lengths.append(len(content))
                elif msg['role'] == 'assistant':
                    assistant_lengths.append(len(content))
                    
                    # Check for code
                    if any(pattern in content.lower() for pattern in ['public class', 'def ', 'function', '```', 'import', '{', '}']):
                        code_count += 1
                        break
        
        quality_metrics['avg_user_length'] = sum(user_lengths) / len(user_lengths) if user_lengths else 0
        quality_metrics['avg_assistant_length'] = sum(assistant_lengths) / len(assistant_lengths) if assistant_lengths else 0
        quality_metrics['has_code_percentage'] = (code_count / len(samples)) * 100
        quality_metrics['avg_conversation_turns'] = sum(turn_counts) / len(turn_counts) if turn_counts else 0
        
        return quality_metrics
    
    def clean_and_enhance_conversation(self, sample: Dict) -> Dict:
        """Clean and enhance a single conversation for agentic behavior"""
        
        if 'messages' in sample:
            # Already in correct format, just clean content
            messages = sample['messages']
        else:
            # Convert from system/user/assistant format
            messages = []
            if 'system' in sample and sample['system'].strip():
                messages.append({
                    'role': 'system',
                    'content': sample['system'].strip()
                })
            
            if 'user' in sample and sample['user'].strip():
                messages.append({
                    'role': 'user', 
                    'content': sample['user'].strip()
                })
                
            if 'assistant' in sample and sample['assistant'].strip():
                messages.append({
                    'role': 'assistant',
                    'content': sample['assistant'].strip()
                })
        
        # Clean and enhance each message
        cleaned_messages = []
        for msg in messages:
            cleaned_content = self.clean_content(msg['content'])
            
            # Enhance for agentic behavior
            if msg['role'] == 'assistant':
                cleaned_content = self.enhance_assistant_response(cleaned_content)
            elif msg['role'] == 'user':
                cleaned_content = self.enhance_user_request(cleaned_content)
                
            cleaned_messages.append({
                'role': msg['role'],
                'content': cleaned_content
            })
        
        return {'messages': cleaned_messages}
    
    def clean_content(self, content: str) -> str:
        """Clean text content"""
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Fix common encoding issues
        content = content.replace('â€™', "'")
        content = content.replace('â€œ', '"')
        content = content.replace('â€', '"')
        
        # Clean up code formatting
        content = re.sub(r'```(\w+)?\n?', '```\n', content)
        
        return content.strip()
    
    def enhance_assistant_response(self, content: str) -> str:
        """Enhance assistant responses for more agentic behavior"""
        
        # Add helpful introductory phrases if missing
        if not any(content.lower().startswith(phrase) for phrase in [
            'here', 'let me', 'i\'ll', 'to', 'this', 'you can', 'certainly'
        ]):
            if 'public class' in content or 'def ' in content:
                content = f"Here's a solution for your cybersecurity problem:\n\n{content}"
            elif content.lower().startswith(('the ', 'a ', 'an ')):
                content = f"Let me explain: {content}"
            elif '?' in content:
                content = f"Great question! {content}"
        
        # Add explanatory context for code
        if 'public class' in content and 'this' not in content.lower()[:100]:
            lines = content.split('\n')
            if len(lines) > 1:
                content = f"This solution implements the cybersecurity functionality you requested:\n\n{content}"
        
        return content
    
    def enhance_user_request(self, content: str) -> str:
        """Enhance user requests for better instruction following"""
        
        # Ensure requests are clear and specific
        if not content.endswith(('?', '.', '!')):
            content = content + '.'
            
        # Add context for cybersecurity relevance
        if 'security' not in content.lower() and 'cyber' not in content.lower():
            cyber_keywords = ['vulnerability', 'exploit', 'malware', 'attack', 'defense', 'protection']
            if any(keyword in content.lower() for keyword in cyber_keywords):
                # Already has cybersecurity context
                pass
            elif 'java' in content.lower() or 'code' in content.lower():
                content = f"Write secure Java code that {content.lower()}"
        
        return content
    
    def process_dataset(self, dataset_path: str, output_name: str) -> str:
        """Process a complete dataset"""
        
        print(f"\n🔄 Processing {dataset_path}...")
        
        # Load dataset
        dataset = load_from_disk(dataset_path)
        train_data = dataset['train']
        
        print(f"  Original size: {len(train_data):,} samples")
        
        # Process each sample
        processed_samples = []
        
        for i, sample in enumerate(train_data):
            try:
                cleaned_sample = self.clean_and_enhance_conversation(sample)
                
                # Quality filter
                if self.meets_quality_standards(cleaned_sample):
                    processed_samples.append(cleaned_sample)
                    
                if (i + 1) % 1000 == 0:
                    print(f"    Processed {i+1:,}/{len(train_data):,} samples...")
                    
            except Exception as e:
                print(f"    Warning: Error processing sample {i}: {e}")
                continue
        
        print(f"  Filtered size: {len(processed_samples):,} samples")
        
        # Save processed data
        output_path = self.output_dir / f"{output_name}.jsonl"
        
        with open(output_path, 'w') as f:
            for sample in processed_samples:
                f.write(json.dumps(sample) + '\n')
        
        print(f"  ✅ Saved to {output_path}")
        
        return str(output_path)
    
    def meets_quality_standards(self, sample: Dict) -> bool:
        """Check if sample meets quality standards"""
        
        messages = sample.get('messages', [])
        
        if len(messages) < 2:
            return False
            
        # Check for user and assistant messages
        has_user = any(msg['role'] == 'user' for msg in messages)
        has_assistant = any(msg['role'] == 'assistant' for msg in messages)
        
        if not (has_user and has_assistant):
            return False
            
        # Check content quality
        for msg in messages:
            content = msg['content']
            
            # Minimum length requirements
            if len(content.strip()) < 20:
                return False
                
            # Maximum length requirements
            if len(content) > 8000:
                return False
                
            # Check for meaningful content
            if content.count(' ') < 3:  # At least a few words
                return False
        
        return True
    
    def merge_and_create_final_dataset(self, processed_files: List[str], output_name: str) -> str:
        """Merge processed datasets and create final training data"""
        
        print(f"\n🔗 Merging {len(processed_files)} datasets...")
        
        all_samples = []
        
        for file_path in processed_files:
            with open(file_path, 'r') as f:
                for line in f:
                    all_samples.append(json.loads(line))
        
        print(f"  Total merged samples: {len(all_samples):,}")
        
        # Remove duplicates based on content similarity
        unique_samples = self.deduplicate_samples(all_samples)
        print(f"  After deduplication: {len(unique_samples):,}")
        
        # Create train/validation split
        split_idx = int(len(unique_samples) * 0.9)
        train_samples = unique_samples[:split_idx]
        val_samples = unique_samples[split_idx:]
        
        # Save final datasets
        train_path = self.output_dir / f"{output_name}_train.jsonl"
        val_path = self.output_dir / f"{output_name}_valid.jsonl"
        
        with open(train_path, 'w') as f:
            for sample in train_samples:
                f.write(json.dumps(sample) + '\n')
                
        with open(val_path, 'w') as f:
            for sample in val_samples:
                f.write(json.dumps(sample) + '\n')
        
        print(f"  ✅ Train: {train_path} ({len(train_samples):,} samples)")
        print(f"  ✅ Valid: {val_path} ({len(val_samples):,} samples)")
        
        return str(train_path), str(val_path)
    
    def deduplicate_samples(self, samples: List[Dict]) -> List[Dict]:
        """Remove duplicate samples based on content similarity"""
        
        unique_samples = []
        seen_user_contents = set()
        
        for sample in samples:
            # Get user message content for deduplication
            user_content = None
            for msg in sample['messages']:
                if msg['role'] == 'user':
                    user_content = msg['content'][:200]  # First 200 chars for comparison
                    break
            
            if user_content and user_content not in seen_user_contents:
                seen_user_contents.add(user_content)
                unique_samples.append(sample)
        
        return unique_samples

def main():
    processor = CybersecurityDataProcessor("/Users/danielrodrigo/Workspace/datasets/cybersecurity_datasets")
    
    # Load reference data for quality analysis
    print("📊 Analyzing reference Heimdall quality standards...")
    reference_samples = processor.load_heimdall_reference()
    quality_metrics = processor.analyze_reference_quality(reference_samples)
    
    print("Reference Quality Metrics:")
    for metric, value in quality_metrics.items():
        print(f"  {metric}: {value}")
    
    # Process cybersecurity datasets
    datasets_to_process = [
        ("AlicanKiraz0_Cybersecurity-Dataset-Heimdall-v1.1", "heimdall_v1_1"),
        ("AlicanKiraz0_Cybersecurity-Dataset-v1", "cybersec_v1")
    ]
    
    processed_files = []
    
    for dataset_dir, output_name in datasets_to_process:
        dataset_path = f"/Users/danielrodrigo/Workspace/datasets/cybersecurity_datasets/{dataset_dir}"
        processed_file = processor.process_dataset(dataset_path, output_name)
        processed_files.append(processed_file)
    
    # Merge into final training dataset
    train_path, val_path = processor.merge_and_create_final_dataset(
        processed_files, "cybersecurity_agentic_clean"
    )
    
    print(f"\n🎉 Processing complete!")
    print(f"📁 Final training data: {train_path}")
    print(f"📁 Final validation data: {val_path}")

if __name__ == "__main__":
    main()
