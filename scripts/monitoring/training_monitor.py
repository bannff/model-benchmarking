#!/usr/bin/env python3
"""
Training Progress Monitor

Monitors the current training progress and prepares for enhanced training transition.
"""

import os
import time
import subprocess
from datetime import datetime, timedelta

def check_training_status():
    """Check if training is still running."""
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        return 'mlx_lm lora' in result.stdout
    except:
        return False

def get_latest_checkpoint():
    """Get the latest checkpoint information."""
    adapter_dir = '/Users/danielrodrigo/Workspace/PyScience/cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1'
    
    checkpoints = []
    for file in os.listdir(adapter_dir):
        if file.endswith('_adapters.safetensors') and file != 'adapters.safetensors':
            iteration = int(file.split('_')[0])
            stat = os.stat(os.path.join(adapter_dir, file))
            checkpoints.append((iteration, datetime.fromtimestamp(stat.st_mtime)))
    
    if checkpoints:
        latest = max(checkpoints, key=lambda x: x[0])
        return latest[0], latest[1]
    
    return None, None

def estimate_completion_time():
    """Estimate when current training will complete."""
    iteration, timestamp = get_latest_checkpoint()
    
    if not iteration or not timestamp:
        return "Unknown"
    
    # Training parameters
    target_iterations = 10000
    training_speed = 0.032  # it/sec
    
    remaining_iterations = target_iterations - iteration
    remaining_seconds = remaining_iterations / training_speed
    completion_time = datetime.now() + timedelta(seconds=remaining_seconds)
    
    return completion_time, remaining_iterations, remaining_seconds / 3600

def monitor_training():
    """Monitor training progress."""
    print("Training Progress Monitor")
    print("=" * 50)
    
    # Check if training is running
    is_running = check_training_status()
    print(f"Training Status: {'RUNNING' if is_running else 'STOPPED'}")
    
    # Get latest checkpoint
    iteration, timestamp = get_latest_checkpoint()
    if iteration:
        print(f"Latest Checkpoint: {iteration:,} iterations")
        print(f"Last Update: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Calculate progress
        progress = (iteration / 10000) * 100
        print(f"Progress: {progress:.1f}% complete")
        
        if is_running:
            completion_time, remaining_iter, remaining_hours = estimate_completion_time()
            print(f"Estimated Completion: {completion_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Remaining: {remaining_iter:,} iterations (~{remaining_hours:.1f} hours)")
    else:
        print("No checkpoints found")
    
    print("\nEnhanced Dataset Status:")
    enhanced_dirs = [d for d in os.listdir('/Users/danielrodrigo/Workspace/PyScience/datasets/') 
                     if d.startswith('primus_training_ENHANCED_')]
    if enhanced_dirs:
        latest_enhanced = max(enhanced_dirs)
        print(f"✓ Enhanced dataset ready: {latest_enhanced}")
        
        # Check training script
        scripts = [f for f in os.listdir('/Users/danielrodrigo/Workspace/PyScience/') 
                  if f.startswith('ENHANCED_TRAINING_')]
        if scripts:
            latest_script = max(scripts)
            print(f"✓ Enhanced training script ready: {latest_script}")
    else:
        print("✗ No enhanced dataset prepared")
    
    print("\nNext Steps:")
    if is_running:
        print("1. Continue monitoring current training")
        print("2. Enhanced dataset is prepared and ready")
        print("3. Will start enhanced training after current cycle completes")
    else:
        print("1. Current training appears to have stopped")
        print("2. Check training logs for completion status")
        print("3. Ready to start enhanced training if desired")

def create_transition_script():
    """Create script to transition from current training to enhanced training."""
    
    script_content = '''#!/bin/bash

# Training Transition Script
# Safely transitions from current training to enhanced training

echo "Training Transition Manager"
echo "=========================="

# Check if current training is still running
if pgrep -f "mlx_lm lora" > /dev/null; then
    echo "ERROR: Current training is still running!"
    echo "Please wait for training to complete or manually stop it first."
    echo "Use: kill -TERM $(pgrep -f 'mlx_lm lora')"
    exit 1
fi

echo "Current training has completed. Ready for enhanced training."

# Find latest enhanced training script
ENHANCED_SCRIPT=$(ls -t ENHANCED_TRAINING_*.sh 2>/dev/null | head -1)

if [ -z "$ENHANCED_SCRIPT" ]; then
    echo "ERROR: No enhanced training script found!"
    echo "Please run: python3 datasets/prepare_enhanced_training.py"
    exit 1
fi

echo "Found enhanced training script: $ENHANCED_SCRIPT"
echo "Starting enhanced training with pattern identification..."

# Start enhanced training
chmod +x "$ENHANCED_SCRIPT"
./"$ENHANCED_SCRIPT"
'''
    
    with open('/Users/danielrodrigo/Workspace/PyScience/transition_to_enhanced.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('/Users/danielrodrigo/Workspace/PyScience/transition_to_enhanced.sh', 0o755)
    print("✓ Transition script created: transition_to_enhanced.sh")

if __name__ == "__main__":
    monitor_training()
    print("\n" + "=" * 50)
    create_transition_script()
    print("\nMonitoring complete!")
