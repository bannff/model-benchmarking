# Project Roadmap and Architecture Improvements

This document outlines prioritized, high-impact improvements to make the repository easier to use, extend, and reason about. Items are grouped by impact and effort, with lightweight contracts where relevant.

## Quick Wins (High Value, Low Risk)

1) Unified Result Schema and Manifests [COMPLETED]
- Define a minimal result envelope used by all suites and the pipeline:
  - run_id, suite, model, provider, started_at, finished_at, status
  - metrics: { overall_accuracy, per_category, duration_s, ... }
  - artifacts: { results_path, report_path, logs_path, suite_specific: {} }
- Write a per-run manifest and append to a results index.

2) Config Validation with Pydantic [COMPLETED]
- Strongly-typed config models for provider, pipeline, and each suite.
- CLI `--dry-run` to validate and print resolved config & step plan.

3) Logging and Run IDs
- Create a run_id (timestamp + short hash) and structured logging (JSONL) per run.

4) Provider Interface Contract [COMPLETED]
- Protocol/ABC in `src/runtime/providers/base.py` with:
  - generate_text(prompt) -> str
  - evaluate_question(question, options?, context?) -> dict
  - batch_evaluate(list[dict], batch_size) -> list[dict]

5) CLI UX Polish [COMPLETED]
- Subcommands: `mbenchmark suite <name>` for individual suite runners, keep `pipeline` for end-to-end.
- Add `--dry-run` to show resolved config, active steps, and environment checks.

## Structural Refactors (Medium Effort, High Payoff)

6) Package the benchmark trees [COMPLETED]
- Convert `benchmarking/` subtrees into proper packages under `src/runtime/suites/`.
- Replace hyphenated dirs with underscore names, add `__init__.py`, and centralize runner APIs.

7) Suite Plugin Interface [COMPLETED]
- Define `Suite` base interface with a single `run()` that receives provider, validated config, output_dir, run_id, logger.
- Returns the standardized result envelope and artifacts.

8) Error Handling and Timeouts
- Wrap external calls with timeouts and standardized exceptions; ensure partial artifacts are written on failure.

9) Results Index and Run Manifest
- Global `results/index.jsonl` (one line per run); each run emits `manifest.json` with config, versions, git commit, env snapshot.

## Testing and Quality

10) Config & Pipeline Tests [COMPLETED]
- Tests for config validation errors, provider factory edge cases, skip logic, and result schema snapshot.

11) Pre-commit Hooks (Optional)
- Ruff, mypy (on `src/`), and basic file size guards to avoid committing large artifacts.

## Performance & Reliability

12) Adaptive Batch Sizing for CS‑Eval
- Backoff/scale based on response latency.

13) Optional Concurrency in Providers [COMPLETED]
- Async `batch_evaluate` with bounded concurrency for HTTP providers like Ollama.

14) Resource Isolation for CVE‑Bench / CyberGym [COMPLETED]
- Document and optionally enforce cgroup limits, non-root users, and network isolation.

## Docs & DX

15) Architecture & Extensibility Docs
- `docs/architecture.md` and `docs/extending.md` covering data flow, interfaces, and how to add a provider/suite.

16) Troubleshooting
- Known issues and quick fixes (Ollama not running, datasets auth, missing optional deps).

---

## Contracts

Result Envelope (JSON):
- run_id: str
- suite: str
- model: str
- provider: str
- started_at: ISO8601
- finished_at: ISO8601
- status: "ok" | "failed" | "skipped"
- metrics: object
- artifacts: { results_path?: str, report_path?: str, logs_path?: str, suite_specific?: object }

Suite Interface:
- run(provider, config, output_dir, run_id, logger) -> ResultEnvelope

Provider Interface (Protocol):
- generate_text(prompt: str) -> str
- evaluate_question(question: str, options?: list[str], context?: str, question_type?: str) -> dict
- batch_evaluate(questions: list[dict], batch_size: int = 10) -> list[dict]

---

## Implementation Order
1) Result schema + manifests
2) Pydantic config models + CLI `--dry-run`
3) Suite base + adapt CS‑Eval
4) Package conversions (optional, staged)
5) Tests for config & results

Progress will be tracked via the repository TODO list and PRs that map to these items.
