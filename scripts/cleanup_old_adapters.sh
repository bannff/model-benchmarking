#!/bin/bash
# Safe adapter cleanup - Keep latest + 1 backup
# The latest adapter contains ALL cumulative training knowledge

ADAPTER_DIR="cybersecurity_finetuned_models/mlx_adapters_primus_ZERO_TRUNCATION_v1"

echo "🧹 SAFE ADAPTER CLEANUP"
echo "======================="
echo "Latest adapter contains ALL cumulative training knowledge"
echo "We'll keep the latest + 1 backup for safety"
echo ""

echo "📊 Current adapter files:"
ls -la "$ADAPTER_DIR"/*_adapters.safetensors | tail -5

echo ""
echo "🎯 Strategy:"
echo "✅ KEEP: 0000800_adapters.safetensors (latest - ALL knowledge)"
echo "✅ KEEP: 0000700_adapters.safetensors (backup)"
echo "✅ KEEP: adapters.safetensors (current best)"
echo "🗑️  DELETE: All older numbered adapters (100-600)"

echo ""
read -p "Proceed with cleanup? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗑️  Removing old adapters..."
    
    # Remove adapters 100-600 (keeping 700-800 + adapters.safetensors)
    rm -f "$ADAPTER_DIR"/0000[1-6]00_adapters.safetensors
    
    echo "✅ Cleanup complete!"
    echo ""
    echo "📊 Remaining files:"
    ls -la "$ADAPTER_DIR"/*_adapters.safetensors
    
    # Calculate space saved
    echo ""
    echo "💾 Space saved: ~27MB (6 files × 4.5MB each)"
    echo "📈 Your 0000800_adapters.safetensors contains ALL the training knowledge!"
    
else
    echo "❌ Cleanup cancelled"
fi
