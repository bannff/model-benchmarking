#!/bin/bash
# Enhanced Training Status Monitor with Real-time Loss Tracking
# Monitors MLX training progress, memory usage, and loss convergence

echo "🔍 MLX Training Status Monitor - Enhanced Loss Tracking"
echo "======================================================="
echo "$(date): Starting monitoring..."
echo ""

while true; do
    clear
    echo "🔍 MLX Training Status Monitor - $(date)"
    echo "======================================================="
    
    # Check if training is running
    if pgrep -f "mlx_lm lora" > /dev/null; then
        echo "✅ Training Status: ACTIVE"
        
        # Get process info
        MLX_PID=$(pgrep -f "mlx_lm lora")
        echo "📊 Process ID: $MLX_PID"
        
        # Memory usage
        MEMORY_MB=$(ps -p $MLX_PID -o rss= | awk '{print int($1/1024)}')
        MEMORY_GB=$(echo "scale=2; $MEMORY_MB/1024" | bc)
        echo "💾 Memory Usage: ${MEMORY_GB}GB (${MEMORY_MB}MB)"
        
        # CPU usage
        CPU_PERCENT=$(ps -p $MLX_PID -o %cpu= | awk '{print $1}')
        echo "🖥️  CPU Usage: ${CPU_PERCENT}%"
        
    else
        echo "❌ Training Status: NOT RUNNING"
    fi
    
    echo ""
    echo "📈 Recent Training Progress (Last 20 lines):"
    echo "--------------------------------------------"
    
    # Show recent training output if log exists
    if [ -f "/tmp/mlx_training.log" ]; then
        tail -n 20 /tmp/mlx_training.log | grep -E "(Loss|Iter|Step|lr:|tokens/sec)" || echo "No recent training data found"
    else
        echo "No training log found. Training output will appear here when active."
    fi
    
    echo ""
    echo "🎯 Latest Checkpoints:"
    echo "---------------------"
    if [ -d "/Users/danielrodrigo/Workspace/PyScience/datasets/cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1" ]; then
        ls -la /Users/danielrodrigo/Workspace/PyScience/datasets/cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1/*.safetensors 2>/dev/null | tail -n 5 || echo "No checkpoints found"
    fi
    
    echo ""
    echo "⌨️  Commands: Ctrl+C to stop monitoring, 'q' + Enter to quit training"
    echo "💡 Tip: Loss should decrease toward 1.0 or below for better quality"
    
    # Check for user input to quit
    read -t 5 -n 1 input
    if [ "$input" = "q" ]; then
        echo ""
        echo "🛑 Stopping training..."
        pkill -f "mlx_lm lora"
        break
    fi
    
    sleep 5
done