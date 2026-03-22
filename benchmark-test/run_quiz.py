#!/usr/bin/env python3
"""Wrapper to run Cybersec Quiz via model_benchmarking package if available."""
import sys
try:
    from runtime import run_benchmark
    run_benchmark('cybersec')
except Exception:
    import runpy
    runpy.run_path('cybersec_quiz.py', run_name='__main__')
