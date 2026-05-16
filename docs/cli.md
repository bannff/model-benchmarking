# 🛠 CLI Reference: `mbenchmark`

The `mbenchmark` CLI is the primary interface for interacting with the Model Benchmarking framework. It provides commands for running evaluation pipelines, managing the cybersecurity taxonomy, and inspecting results.

## 🚀 Pipeline Commands

### `mbenchmark pipeline`

The main entry point for running a sequence of benchmark suites.

**Usage:**
```bash
mbenchmark pipeline [OPTIONS]
```

**Key Options:**
- `--provider TEXT`: Name of the model provider to use (default: `ollama`).
- `--model TEXT`: Model name/ID (default: `llama3.2`).
- `--host TEXT`: Provider host URL (default: `http://localhost:11434`).
- `--output-dir TEXT`: Directory to save results (default: `results`).
- `--dry-run`: Validate configuration and planned steps without executing.
- `--verbose`: Enable detailed logging.

**Example:**
```bash
mbenchmark pipeline --model llama3.1 --dry-run
```

---

## 🏗 Taxonomy Commands

### `mbenchmark taxonomy list`

List all registered categories and mappings in the cybersecurity taxonomy.

### `mbenchmark taxonomy validate`

Validate the integrity of the taxonomy schema and YAML mappings.

---

## 📊 Evaluation Commands

### `mbenchmark evals run`

Run a specific benchmark suite independently.

**Options:**
- `--suite [cs-eval|cybergym|cve-bench]`: The suite to execute.

---

## 🛠 Advanced Usage

### Configuration Overrides
The CLI supports deep-merging configurations from YAML files or environment variables. This allows for complex setup scenarios without changing the code.

```bash
# Example of using a custom config file
mbenchmark pipeline --config my_env_config.yaml
```

> [!TIP]
> Use `mbenchmark --help` or `mbenchmark [COMMAND] --help` to see the full list of arguments and flags for any command.
