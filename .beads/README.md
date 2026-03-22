# Beads Tracking System (`.beads/`)

The **Beads** system provides detailed session tracking and metadata management for the `Model-Benchmarking` repository. It ensures that every development session is context-aware and synchronized.

## ⚙️ Configuration

The `config.yaml` file defines the behavior of the beads system, including:
-   Session lifecycle hooks.
-   Metadata schemas for tracking changes.
-   Synchronization endpoints.

## ⚓ Hooks

Git hooks in `.beads/hooks/` are used to trigger beads events:
-   **pre-commit**: Validates session state before committing.
-   **post-merge**: Syncs context after merging changes.
-   **prepare-commit-msg**: Injects session IDs into commit messages.

## 🛠 Integration

Agents should ensure that their `task.md` and `implementation_plan.md` are kept in sync with the current beads session.

---

*Powered by Bannff.*
