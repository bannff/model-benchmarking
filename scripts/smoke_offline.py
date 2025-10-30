#!/usr/bin/env python3
"""
Offline end-to-end smoke run using the deterministic mock provider.
Writes artifacts to ./results by default.
"""
from __future__ import annotations

# No typing imports needed
from model_benchmarking.providers.factory import make_provider
from model_benchmarking.pipeline import run_pipeline


def main(output_dir: str = "results") -> int:
    prov = make_provider("mock", model="mock")
    steps = run_pipeline(
        provider=prov,
        categories=None,
        max_questions=1,
        output_dir=output_dir,
        verbose=True,
        skip_cs_eval=True,
        skip_cybergym=False,
        skip_cvebench=False,
    )
    for s in steps:
        print(f"[{s.name}] {s.status} {s.results_path or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
