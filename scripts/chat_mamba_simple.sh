#!/bin/bash
# Enhanced Mamba Cybersecurity Chat Wrapper
# Optimized for the M4-trained cybersecurity model

set -e

# Add MLX-LM to PATH
export PATH="/Users/danielrodrigo/Library/Python/3.9/bin:$PATH"

echo "🐍 MAMBA CYBERSECURITY MODEL CHAT"
echo "================================="
echo "✅ Loading your freshly trained M4-optimized cybersecurity model..."
echo "🧠 Mamba 1.4B with specialized cybersecurity LoRA adapters"
echo "🎯 Trained on: 569K cybersecurity samples"
echo ""
echo "💡 Try asking about:"
echo "   • SQL injection prevention techniques"
echo "   • Network security best practices"
echo "   • AWS security patterns and compliance"
echo "   • Malware analysis and incident response"
echo "   • Cryptography and encryption methods"
echo ""
echo "📝 Commands:"
echo "   • 'q' to quit"
echo "   • 'r' to reset conversation"
echo "   • 'h' for help"
echo ""
echo "🚀 Starting chat session..."
echo "================================================"

# Start the MLX-LM chat with optimized parameters
python3 -m mlx_lm chat \
  --model "models/mamba-1.4b-mlx" \
  --adapter-path "adapters" \
  --max-tokens 384 \
  --temp 0.7
