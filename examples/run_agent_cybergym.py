#!/usr/bin/env python3
"""
Run CyberGym with an agent workflow using the example config.

Usage:
  python examples/run_agent_cybergym.py

Requires:
  - ollama running at http://localhost:11434 with model 'llama3.2' pulled, or adjust the config.
  - strands-agents and strands-agents-tools installed (already in requirements.txt).
"""
from __future__ import annotations

import json
from pathlib import Path

from model_benchmarking.providers.factory import make_provider
from model_benchmarking.pipeline import run_pipeline
from model_benchmarking.config import load_config_file, deep_merge
from model_benchmarking.config_models import RootConfig

EXAMPLE_CFG = Path(__file__).resolve().parents[1] / "configs" / "examples" / "pipeline.agent_cybergym.yaml"


def main() -> None:
    file_cfg = load_config_file(str(EXAMPLE_CFG))
    # You can override pieces here in code as needed
    cfg = deep_merge(file_cfg, {})
    validated = RootConfig.model_validate(cfg).model_dump()

    prov_name = (validated.get("provider", {}) or {}).get("name") or "ollama"
    provider = make_provider(
        prov_name,
        model=(validated.get("provider", {}) or {}).get("model") or "llama3.2",
        host=(validated.get("provider", {}) or {}).get("host") or "http://localhost:11434",
        use_strands=(prov_name == "strands-ollama"),
    )

    steps = run_pipeline(
        provider=provider,
        categories=(validated.get("pipeline", {}) or {}).get("categories"),
        max_questions=(validated.get("pipeline", {}) or {}).get("max_questions"),
        output_dir=(validated.get("pipeline", {}) or {}).get("output_dir", "results"),
        verbose=bool((validated.get("pipeline", {}) or {}).get("verbose", False)),
        use_strands_telemetry=bool((validated.get("pipeline", {}) or {}).get("use_strands_telemetry", False)),
        skip_cs_eval=bool((validated.get("pipeline", {}) or {}).get("skip_cs_eval", True)),
        skip_cybergym=bool((validated.get("pipeline", {}) or {}).get("skip_cybergym", False)),
        skip_cvebench=bool((validated.get("pipeline", {}) or {}).get("skip_cve_bench", True)),
        cs_eval_config=(validated.get("cs_eval", {}) or {}),
        cybergym_config=(validated.get("cybergym", {}) or {}),
        cvebench_config=(validated.get("cvebench", {}) or {}),
    )

    print("Pipeline summary:")
    for s in steps:
        print(f" - [{s.name}] {s.status} {s.results_path or ''}")


if __name__ == "__main__":
    main()
