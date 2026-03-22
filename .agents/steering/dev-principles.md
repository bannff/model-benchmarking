# Development Principles

These core principles govern all contributions to the repository.

## 1. Single Responsibility Principle (SRP)
Every file, class, and function must have one and only one reason to change. If a module handles multiple concerns, it must be split.

## 2. Strict Line Limit (<200 LOC)
To maintain extreme readability and enforce modularization, absolutely no file should exceed 200 lines of code. No exceptions. Large files must be broken down into sub-modules.

## 3. MCP-First (Model Context Protocol)
Code must be designed with an agentic, context-aware interface in mind. Expose logic via the `mcp/` interface wrapping core logic from `runtime/`. Agents reading the code should immediately understand the execution boundaries.

## 4. Agnostic Design
Do not tightly couple to specific external models, datasets, or libraries unless inside a dedicated adapter layer (e.g., `providers/ollama.py`). Core logic must rely on abstract interfaces.
