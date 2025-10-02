#!/bin/bash

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
