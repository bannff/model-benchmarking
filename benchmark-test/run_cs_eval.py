#!/usr/bin/env python3
"""Wrapper to run CS-Eval via the new model_benchmarking package if available."""
import sys
try:
    from model_benchmarking import run_benchmark
    run_benchmark('cs-eval')
except Exception:
    # Fallback to original script
    import runpy
    runpy.run_path('cs_eval_official.py', run_name='__main__')
