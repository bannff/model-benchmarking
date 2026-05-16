---
description: How to safely refactor large modules to comply with the <200 LOC rule.
---

# Recipe: Structural LOC Refactoring

When an agent is tasked with reducing a file below the 200 LOC limit (mandated by `dev-principles.md`), they must NOT use automated regex or naive splitting scripts. They must explicitly scrutinize the AST.

## Step 1: Meta-Architect Analysis
1. Read the target file completely using `view_file`.
2. Identify semantic boundaries:
   - Base protocols / ABCs (`base.py`)
   - Concrete implementations (`implementations.py` or specific names)
   - Orchestration/Runner logic (`runner.py`)
   - Data structures / Pydantic models (`schema.py`)

## Step 2: Implementer Execution
1. Create the new sub-package folder (e.g., `evals/models/`).
2. Individually use `write_to_file` to draft the new modularized components.
3. Explicitly rewrite internal imports (e.g., `from .base import...`).
4. Update `__init__.py` to re-export the public API, ensuring downstream consumers (like `mcp/cli.py`) do not break.

## Step 3: QA-Tester Validation
1. Execute `pytest tests/` entirely.
2. If utilizing `hypothesis`, ensure property-based constraints hold.
3. Validate against `scripts/verify_repo.sh`.
