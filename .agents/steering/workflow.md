# Standard Engineering Workflow

Follow this tight feedback loop for all feature development or bug fixing.

1. **Verify State**: Run `scripts/verify_repo.sh` first to ensure the repository is clean before starting work.
2. **Plan**: Write the intent into a `task.md` or `implementation_plan.md`.
3. **Draft**: Create the functionality in small, modular files (<200 LOC).
4. **Adapter Integration**: If adding a new capability, map it through the `src/mcp/` layer.
5. **Test**: Run `pytest tests/`.
6. **Re-Verify**: Run `scripts/verify_repo.sh` to ensure no new files violate the LOC limit or SRP.
7. **Commit**: Ensure `.beads/` hooks have captured the session context.
