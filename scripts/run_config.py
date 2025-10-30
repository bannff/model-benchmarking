#!/usr/bin/env python3
"""
Run the pipeline using a config file (YAML/JSON/TOML) with optional CLI overrides.
This wrapper is portable and avoids requiring `make` or platform-specific shells.
"""
from __future__ import annotations

import argparse
from typing import Any

from model_benchmarking.config import load_config_file, deep_merge
from model_benchmarking.providers.factory import make_provider
from model_benchmarking.pipeline import run_pipeline


def main() -> int:
    ap = argparse.ArgumentParser(description="Run model-benchmarking pipeline from config")
    ap.add_argument("--config", required=True, help="Path to YAML/JSON/TOML config")
    ap.add_argument("--output_dir", default=None, help="Override output directory")
    ap.add_argument("--provider", default=None, help="Override provider name")
    ap.add_argument("--model", default=None, help="Override model id")
    ap.add_argument("--host", default=None, help="Override provider host")
    ap.add_argument("--skip-cs-eval", action="store_true", help="Skip CS-Eval step")
    ap.add_argument("--skip-cybergym", action="store_true", help="Skip CyberGym step")
    ap.add_argument("--skip-cve-bench", action="store_true", help="Skip CVE-Bench step")
    args = ap.parse_args()

    file_cfg = load_config_file(args.config)
    overrides: dict[str, Any] = {"pipeline": {}}
    if args.output_dir:
        overrides["pipeline"]["output_dir"] = args.output_dir
    if args.skip_cs_eval:
        overrides["pipeline"]["skip_cs_eval"] = True
    if args.skip_cybergym:
        overrides["pipeline"]["skip_cybergym"] = True
    if args.skip_cve_bench:
        overrides["pipeline"]["skip_cve_bench"] = True
    if args.provider or args.model or args.host:
        overrides.setdefault("provider", {})
        if args.provider:
            overrides["provider"]["name"] = args.provider
        if args.model:
            overrides["provider"]["model"] = args.model
        if args.host:
            overrides["provider"]["host"] = args.host

    cfg = deep_merge(file_cfg, overrides)

    prov_name = (cfg.get("provider", {}) or {}).get("name") or "ollama"
    provider = make_provider(
        prov_name,
        model=(cfg.get("provider", {}) or {}).get("model") or "llama3.2",
        host=(cfg.get("provider", {}) or {}).get("host") or "http://localhost:11434",
        use_strands=(prov_name == "strands-ollama"),
    )

    steps = run_pipeline(
        provider=provider,
        categories=(cfg.get("pipeline", {}) or {}).get("categories"),
        max_questions=(cfg.get("pipeline", {}) or {}).get("max_questions"),
        output_dir=(cfg.get("pipeline", {}) or {}).get("output_dir", "results"),
        verbose=bool((cfg.get("pipeline", {}) or {}).get("verbose", True)),
        use_strands_telemetry=bool((cfg.get("pipeline", {}) or {}).get("use_strands_telemetry", False)),
        skip_cs_eval=bool((cfg.get("pipeline", {}) or {}).get("skip_cs_eval", False)),
        skip_cybergym=bool((cfg.get("pipeline", {}) or {}).get("skip_cybergym", False)),
        skip_cvebench=bool((cfg.get("pipeline", {}) or {}).get("skip_cve_bench", False)),
        cs_eval_config=(cfg.get("cs_eval", {}) or {}),
        cybergym_config=(cfg.get("cybergym", {}) or {}),
        cvebench_config=(cfg.get("cvebench", {}) or {}),
    )

    for s in steps:
        print(f"[{s.name}] {s.status} {s.results_path or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
