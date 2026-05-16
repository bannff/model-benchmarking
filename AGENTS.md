# Agent Operating Model

Welcome, Agent. This repository is designed for seamless human-agent collaboration. This document outlines the standards and infrastructure available to you.

## 🤖 Getting Started

Before performing any work, you should:
1.  **Onboard**: Read the root `README.md` to understand the mission.
2.  **Explore**: Familiarize yourself with the `.agents/` directory.
3.  **Steer**: Check `.agents/steering/` for any project-specific directives.

## 🧭 Agent Steering Infrastructure (`.agents/`)

This directory contains the knowledge base and blueprints for your operations:

-   **`README.md`**: Detailed technical onboarding for agents.
-   **`recipes/`**: Reusable task patterns and "how-to" guides.
-   **`skills/`**: Deep-dive instructions for specific domains (e.g., benchmark suite integration).
-   **`steering/`**: Global project guardrails and high-level priorities.
-   **`workflows/`**: Step-by-step procedures for complex maintenance or feature additions.

## 🟢 Operating Principles

1.  **Plan First**: For any task more complex than a single-line fix, create/update `implementation_plan.md` in the brain directory.
2.  **Verify Always**: Use the `mbenchmark` CLI to validate changes to benchmark suites. Run `pytest` for framework changes.
3.  **Beads Tracking**: This repository uses a "beads" system for session tracking. Ensure your work follows the lifecycle hooks defined in `.beads/`.
4.  **Premium Aesthetics**: Maintain the "stellar" quality of the repository. Use semantic HTML, rich markdown, and clear documentation.

## 🛠 Tools and Framework

-   **CLI**: `mbenchmark` is your primary interface for running evaluations.
-   **Taxonomy**: The core of this project is the cybersecurity taxonomy in `src/runtime/taxonomy/`.
-   **Providers**: We support Ollama, OpenAI, and Anthropic via a standardized provider interface.

---

*Happy Coding, Agent.*
