#!/usr/bin/env python3
"""
Run CS-Eval using a local JSON/JSONL sample with the mock provider.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from runtime.providers.factory import make_provider


def main() -> int:
    ap = argparse.ArgumentParser(description="Run CS-Eval on a local sample with mock provider")
    ap.add_argument("--sample", required=True, help="Path to JSON/JSONL sample")
    ap.add_argument("--out", default="results", help="Output directory")
    args = ap.parse_args()

    # Import CS-Eval runner dynamically (path with hyphen)
    import importlib.util
    repo_root = Path(__file__).resolve().parents[1]
    mod_path = repo_root / "benchmarking" / "cs-eval" / "run_evaluation.py"
    spec = importlib.util.spec_from_file_location("cs_eval_runner_cli", str(mod_path))
    if not spec or not spec.loader:
        print("Failed to load CS-Eval runner")
        return 2
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[attr-defined]

    run_cs_eval_with_provider = getattr(module, "run_cs_eval_with_provider")
    provider = make_provider("mock", model="mock")
    res = run_cs_eval_with_provider(
        provider,
        categories=None,
        max_questions=2,
        batch_size=2,
        output_dir=args.out,
        verbose=True,
        local_sample_path=args.sample,
    )
    print(f"results: {res.get('results_path')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
