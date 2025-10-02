#!/usr/bin/env python3
"""
Comprehensive Cybersecurity Model Training Monitor
Tracks training progress and validates model performance
"""

import time
import os
import json
from pathlib import Path

def monitor_training_progress():
    """Monitor comprehensive cybersecurity model training"""
    
    print("🔍 Monitoring Comprehensive Cybersecurity Model Training")
    print("=" * 60)
    
    adapter_path = "comprehensive_cybersec_adapter"
    
    # Training status tracking
    iteration_count = 0
    last_loss = None
    
    while True:
        try:
            # Check if adapter directory exists
            if os.path.exists(adapter_path):
                print(f"✅ Adapter directory created: {adapter_path}")
                
                # Check for adapter files
                adapter_files = list(Path(adapter_path).glob("*.npz"))
                if adapter_files:
                    print(f"📁 Adapter files found: {len(adapter_files)}")
                    for file in adapter_files:
                        print(f"   - {file.name}")
                
                # Check for training config
                config_file = Path(adapter_path) / "adapter_config.json"
                if config_file.exists():
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    print(f"⚙️  Adapter config: {config}")
                
                print(f"🎯 Training focused on:")
                print(f"   • Truth-seeking behavior for unknown information")
                print(f"   • Multi-turn agentic conversations")
                print(f"   • Research methodology guidance")
                print(f"   • Incident response workflows")
                print(f"   • Pattern identification skills")
                
                break
            else:
                iteration_count += 1
                print(f"⏳ Waiting for training to start... ({iteration_count})")
                
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\\n🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Error monitoring training: {e}")
            time.sleep(10)

def check_dataset_stats():
    """Check comprehensive dataset statistics"""
    
    print("\\n📊 Comprehensive Dataset Statistics")
    print("-" * 40)
    
    dataset_file = "datasets/comprehensive_cybersec_dataset.jsonl"
    
    if os.path.exists(dataset_file):
        with open(dataset_file, 'r') as f:
            lines = f.readlines()
        
        print(f"📈 Total training samples: {len(lines)}")
        
        # Analyze conversation types
        conversation_types = {
            "CVE Research": 0,
            "AWS Security": 0, 
            "Incident Response": 0,
            "Tool Research": 0,
            "Attack Techniques": 0,
            "Other": 0
        }
        
        for line in lines:
            data = json.loads(line)
            text = data.get('text', '').lower()
            
            if 'cve-' in text:
                conversation_types["CVE Research"] += 1
            elif 's3' in text or 'ec2' in text or 'aws' in text:
                conversation_types["AWS Security"] += 1
            elif 'incident' in text or 'breach' in text:
                conversation_types["Incident Response"] += 1
            elif 'tool' in text or 'configure' in text:
                conversation_types["Tool Research"] += 1
            elif 'technique' in text or 'attack' in text:
                conversation_types["Attack Techniques"] += 1
            else:
                conversation_types["Other"] += 1
        
        print("\\n🎯 Conversation Type Distribution:")
        for conv_type, count in conversation_types.items():
            percentage = (count / len(lines)) * 100
            print(f"   • {conv_type}: {count} ({percentage:.1f}%)")
    
    else:
        print("❌ Dataset file not found")

def main():
    check_dataset_stats()
    monitor_training_progress()

if __name__ == "__main__":
    main()
