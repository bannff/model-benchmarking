# Project Overview

The **Model-Benchmarking** repository is structured to seamlessly separate underlying evaluation mechanics from developer tools and interfaces.

## High-Level Architecture

- **`src/runtime/`**: The unchangeable core. Holds the evaluation engine, taxonomy schema, grader logic, and dataset processing.
- **`src/mcp/`**: Context and tooling boundaries. Adapters, CLI commands, and workflow integrations.
- **`configs/`**: Declarative state. YAML representations for benchmark suites and taxonomy mappings.
- **`.agents/`**: The steering mechanisms that guide both AI agents and human contributors in managing the repo.
- **`.beads/`**: Context synchronization and state tracking hooks.
