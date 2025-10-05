# Model Benchmarking — Unified Cybersecurity Evaluation Suite

This repository brings three complementary cybersecurity benchmarking suites together so security teams and researchers can evaluate language models with a single, consistent tooling surface.

In one place you'll find:
- CS-Eval: question-and-answer style benchmarks (text-based)
- CVE-Bench: challenge-driven fixtures and vulnerable images (containerized)
- CyberGym: interactive scenario simulations (containerized/hosted)

Why a unified suite
-------------------
- Broad coverage: combine knowledge/Q&A checks, interactive scenario-based testing, and challenge exploitation/mitigation exercises.
- Reuse and automation: a single CLI/runner can start suites, orchestrate containers, and aggregate scores.
- Reproducibility: run each benchmark inside a container for consistent, safe evaluation.

Repository layout (high level)
-----------------------------
- `benchmarking/` — shared evaluation runners, example configs, and utilities.
- `benchmark-test/` — development fixtures and local harnesses for the three suites:
  - `benchmark-test/cs-eval/` — CS-Eval content and runner scripts.
  - `benchmark-test/cve-bench/` — CVE challenge fixtures (DB dumps, images, graders).
  - `benchmark-test/cybergym/` — CyberGym scenarios and example orchestrations.
- `configs/` — example config files for running experiments.
- `environments/` — virtualenv and environment setup helpers.
- `.gitattributes` — rules for tracking large binary artifacts (e.g., `*.arrow`, `*.parquet`, `*.bin`).

Short blurbs on each suite
--------------------------
- CS-Eval
  - Type: question-and-answer (closed-form and open-form prompts)
  - Use-case: test knowledge, instruction following, and reasoning on textual prompts.
  - Integration: very scriptable — you can feed prompt lists to a model client and collect structured outputs for automated scoring.

- CVE-Bench
  - Type: challenge fixtures, vulnerable appliances, and grader harnesses.
  - Use-case: evaluate model-assisted exploitation reasoning, mitigation suggestions, and step-by-step exploit descriptions.
  - Integration: typically containerized; graders often expect helper scripts in the runtime image (see `benchmark-test/cve-bench/README.md`). Many challenge fixtures include SQL dumps and configuration strings that reference script paths — these are part of the original fixtures.

- CyberGym
  - Type: interactive, scenario-based simulated environments (often multi-host or service networks).
  - Use-case: measure a model's ability to orchestrate multi-step actions, persistence, detection evasion, or defense strategies via API interactions.
  - Integration: run as an isolated container or VM, and expose a stable API endpoint the model can query.

Getting started — quick developer steps
--------------------------------------
1. Install dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Quickstart (local package)
---------------------------
To use the new shared package CLI after installing in your environment, run:

```bash
mbenchmark run --suite cs-eval
```

This is a thin wrapper that delegates to the existing scripts (keeps original suites intact).

Docker image
------------
You can build a container with the package and run the CLI inside a reproducible environment.

Build the image:

```bash
docker build -t model-benchmarking:local .
```

Run the `cs-eval` suite inside the container (mount the repo to `/workspace`):

```bash
docker run --rm -v $(pwd):/workspace -w /workspace model-benchmarking:local run --suite cs-eval
```

CVE-Bench graders may expect helper scripts at `/evaluator/scripts` inside the container. Provide them by mounting a host directory when running the challenge images or when using this container:

```bash
docker run --rm -v /path/to/evaluator-scripts:/evaluator/scripts:ro -v $(pwd):/workspace -w /workspace model-benchmarking:local run --suite cve-bench
```

Publish to GitHub Container Registry (GHCR)
-----------------------------------------
To have CI push the built image to GHCR on merges, create a personal access token with `write:packages` scope and add it to repository secrets as `GHCR_PAT`. The CI will push `ghcr.io/<owner>/model-benchmarking:latest` when the secret is present.

Releases and the `latest` tag
-----------------------------
When you push a git tag following the pattern `v*` (for example `v1.2.0`), the `release.yml` workflow will build multi-arch images and push both the version tag and a `latest` tag to GHCR (e.g. `ghcr.io/<owner>/model-benchmarking:v1.2.0` and `ghcr.io/<owner>/model-benchmarking:latest`).

To pull a specific release:

```bash
docker pull ghcr.io/<owner>/model-benchmarking:v1.2.0
```

To pull the most recent release (latest):

```bash
docker pull ghcr.io/<owner>/model-benchmarking:latest
```
2. Run a CS-Eval job (text-only example)

```bash
python3 benchmarking/cs-eval/run_evaluation.py --model <model-id-or-path> --output results/cs-eval/<run-name>
```

3. Run a CVE-Bench challenge (containerized, high-level)

```bash
# Build or pull the challenge runtime image, then start the container
docker compose -f benchmark-test/cve-bench/docker-compose.yml up --build
# Provide runtime helper scripts to the container if required (mount /evaluator/scripts)
```

4. Run CyberGym (interactive)

```bash
# Start the CyberGym container and expose API endpoints
docker compose -f benchmark-test/cybergym/docker-compose.yml up --build
# Use the provided orchestrator to drive scenario steps via API.
```

Runtime helper scripts and embedded references
---------------------------------------------
Some graders and challenge images expect helper scripts (for example: `/evaluator/scripts/run_lollms.sh`). Provide these at container startup by mounting them into the container or baking them into the runtime image. Many SQL dumps contain strings like `<path_cacti>/scripts/...` — these are part of the challenge fixtures and intentionally left unchanged.

Large files and repository hygiene
---------------------------------
- The repo uses `.gitattributes` to track large dataset patterns and avoid committing raw binary dataset shards into git history. If you add large artifacts, either:
  - Track them via the `.gitattributes`/pointer mechanism, or
  - Host them externally (S3/Hugging Face/artifact storage) and store only pointers in this repo.

Working with Git LFS (for contributors)
--------------------------------------
After cloning this repository, run these commands to ensure LFS objects are fetched correctly:

```bash
git lfs install
git lfs pull --all
```

If collaborators do not install Git LFS they will see pointer files (not the binary content) in place of large files. Add this to your onboarding instructions or CI checks.

Security & safety
-----------------
This repository contains intentionally vulnerable challenge content. Always run CVE-Bench and CyberGym workloads in isolated networks or disposable environments. Do not expose challenge instances to untrusted networks.

Contributing & roadmap
----------------------
- Unified CLI to run suites and aggregate results
- UI to visualize runs and scoring dashboards
- CI checks and pre-commit hooks to block accidental large file commits

If you want me to add CI/pre-commit hooks or create the unified runner CLI, say the word and I will scaffold them.

---
For suite-level READMEs (short notes or runtime tips), see the files under `benchmark-test/` (added alongside the challenges).

Codespaces / Devcontainer
-------------------------
This repository includes a `.devcontainer` to make Codespaces or local devcontainers easier to use. The devcontainer config sets up Python 3.11, installs developer deps, and configures your git author identity inside the container so commits from Codespaces have the correct author metadata. If you prefer not to commit a devcontainer to the repo, let me know and I can revert that file and instead document the recommended setup in the README.

# Model-Benchmarking — Cybersecurity Model Evaluation Suite

This repository hosts evaluation harnesses, challenge datasets, and safe sandboxing scaffolds for benchmarking language models on cybersecurity tasks (CVE reasoning, exploit analysis, and challenge-style tasks).

Purpose:
- Provide reproducible evaluation runners for CS-Eval, CVE-Bench, and CyberGym-style challenges.
- Keep challenge assets and evaluation harnesses together while excluding large dataset artifacts and preprocessing tools from the public repo.

Note about moved assets
- The project's dataset pre-processing scripts and auxiliary docs have been moved out of this repository to the parent workspace. If you need them, they live at the parent workspace location (for example `/Users/danielrodrigo/Workspace/datasets/`).

Quick start (what this repo contains)
- `benchmarking/` — evaluation runners and configs for public benchmarks
- `benchmark-test/` — local challenge payloads and test harnesses (CVE-Bench fixtures used for CI/local testing)
- `configs/` — example configs for running evaluations
- `scripts/` — lightweight runner scripts (small helpers only — heavy dataset processing tools are intentionally moved out)
- `results/` — output from prior benchmark runs
How to run an evaluation (example)
1. Install Python deps: `pip install -r requirements.txt`
2. Run a benchmark runner (example for CS-Eval):
   - `python3 benchmarking/cs-eval/run_evaluation.py --model <model-id-or-path> --output results/cs-eval/<run-name>`

Notes on large files
- Large dataset shards and binary artifacts have been migrated to Git LFS and/or moved out of the repository. If you need to work with large datasets, keep them in a separate storage location (S3, Hugging Face datasets, or a parent workspace) and avoid committing raw archives to this repo.

Sanitization of embedded challenge data
- Some challenge database dumps (under `benchmark-test/cve-bench/.../db/`) intentionally contain textual references to external script paths (these are part of challenge payloads and not active repo scripts). If you want these sanitized or annotated, I can either:
  1. Replace those occurrences with a short placeholder, or
  2. Add an explanatory README in `benchmark-test/cve-bench/` clarifying these are challenge DB dumps and that `scripts/` was moved.

Contributing
- To add a new model evaluation, create a new directory under `benchmarking/` with a small runner script, a config, and test fixtures.

Safety and sandboxing
- CVE-Bench and CyberGym evaluations include sandbox notes and docker configurations — do not run untrusted challenge targets without proper isolation.

Contact
- If you need the dataset preprocessing scripts or full documentation that were moved, find them at the parent workspace paths listed above.

---

