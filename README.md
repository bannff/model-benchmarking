# 🌌 Model Benchmarking

[![License: BSL 1.1](https://img.shields.io/badge/License-BSL%201.1-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: Private](https://img.shields.io/badge/Status-Private-red.svg)]()

> **The gold standard for cybersecurity model evaluation.**  
> A unified framework designed to push the boundaries of LLM security capabilities through rigorous, taxonomy-aligned benchmarking.

---

## ✨ Key Features

| 🛡️ Unified Framework | 📂 Cyber Taxonomy | 🛠️ Multi-Provider |
| :--- | :--- | :--- |
| Flexible, config-driven evaluation suites with pluggable graders. | Hierarchical classification by capability, domain, CWE, and attack stage. | Native support for Ollama, Strands SDK, and advanced mock providers. |

| 🎯 Three Power Suites | 🤖 Agent-First | 🐳 Containerized |
| :--- | :--- | :--- |
| **CS-Eval** (Q&A), **CVE-Bench** (Challenges), and **CyberGym** (Scenarios). | Built-in steering docs and tracking for seamless AI collaboration. | Fully containerized workloads for isolated, safe security testing. |

---

## 🚀 Quick Start

### 1️⃣ Installation

```bash
# Clone and setup environment
git clone https://github.com/bannff/Model-Benchmarking.git
cd Model-Benchmarking
python3 -m venv .venv && source .venv/bin/activate

# Install with development tools
pip install -e "." -r requirements-dev.txt
```

### 2️⃣ Run Your First Eval

```bash
# Run a minimal pipeline using the mock provider
mbenchmark pipeline --provider mock --skip-cs-eval
```

---

## 📊 Benchmark Suites

### 📝 CS-Eval (Security Knowledge)
Comprehensive Q&A benchmarks testing theoretical foundations and security reasoning.  
`mbenchmark run --suite cs-eval`

### 🐛 CVE-Bench (Exploit Dev)
Real-world vulnerability exploitation challenges in isolated container environments.  
`mbenchmark run --suite cve-bench`

### 🏟️ CyberGym (Interactive Scenarios)
Multi-step, interactive security missions testing agentic decision-making.  
`mbenchmark run --suite cybergym`

---

## 🧭 Navigation

- 🛠 **[CLI Reference](docs/cli.md)** — Master the `mbenchmark` command.
- 📂 **[Taxonomy Registry](src/model_benchmarking/taxonomy/registry.py)** — Explore the built-in security hierarchy.
- 🤖 **[Agent Onboarding](AGENTS.md)** — Guide for AI collaborators.
- 🧭 **[Steering Documentation](.agents/README.md)** — Advanced agent blueprints.

---

## 🛠 Project Structure

```bash
src/model_benchmarking/
├── cli.py              # CLI entry point (mbenchmark command)
├── evals/              # Core evaluation engine
│   ├── runner.py       # The primary execution loop
│   ├── graders/        # Rubric & tool-based grading
│   └── models.py       # Pydantic schema definitions
├── taxonomy/           # The "Brain" - Hierarchical indexing
└── suites/             # Suite adapters (Inspect, CyberGym, etc.)
```

---

## 🛡 Safety & Disclosure

This repository contains **intentionally vulnerable code** and exploit patterns for research and evaluation purposes.  
**NEVER** run these benchmarks against production systems. Always use the provided Docker isolation.

---

## 📜 License

This project is licensed under the **Business Source License 1.1**. See [LICENSE](LICENSE) for the full text.  
*Model-Benchmarking by Bannff.*
