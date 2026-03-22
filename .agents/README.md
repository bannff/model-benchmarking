# Agent Steering Documentation (`.agents/`)

This directory contains the knowledge base, steering directives, and operational blueprints for AI agents collaborating on the `Model-Benchmarking` repository.

## 📁 Directory Structure

-   **`steering/`**: Global rules and project-specific guardrails.
-   **`skills/`**: Deep-dive instructions for specific domains (e.g., benchmark suite integration, taxonomy mapping).
-   **`workflows/`**: Step-by-step procedures for complex tasks.
-   **`recipes/`**: Reusable task patterns and code snippets.

## 🛠 Usage for Agents

When you start a new task in this repository:
1.  Check `AGENTS.md` at the root for the high-level operating model.
2.  Consult `.agents/steering/` for any new directives or priorities.
3.  Use the `view_file` tool to read relevant **Skills** and **Workflows** when performing specialized work.

## 🟢 Operating Principles

-   **Plan First**: Always create/update an `implementation_plan.md` in your brain directory.
-   **Verify Always**: Run `mbenchmark` and `pytest` to validate changes.
-   **Rich Documentation**: Update these docs as the repository evolves.

---

*This infrastructure ensures consistent, high-quality contributions from both human and AI developers.*
