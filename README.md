# Model Benchmarking

A unified cybersecurity model evaluation framework for benchmarking LLMs on security tasks.

## Features

- **Unified Evals Framework** — Flexible, config-driven evaluation suites with pluggable graders
- **Taxonomy System** — Hierarchical classification for organizing evaluations by capability, domain, difficulty, CWE, and attack stage
- **Multiple Providers** — Support for Ollama, Strands SDK, and mock providers
- **Three Benchmark Suites** — CS-Eval (Q&A), CVE-Bench (challenges), and CyberGym (interactive scenarios)

## Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e .
```

### Run an Evaluation

```bash
# Run the full pipeline with Ollama
mbenchmark pipeline --provider ollama --model llama3.2

# Run with mock provider (offline, no external services)
mbenchmark pipeline --provider mock --skip-cs-eval

# Run from a config file
mbenchmark pipeline --config configs/examples/pipeline.minimal.yaml
```

## Project Structure

```
src/model_benchmarking/
├── cli.py              # CLI entry point (mbenchmark command)
├── pipeline.py         # Full evaluation pipeline
├── evals/              # Core evaluation framework
│   ├── models.py       # Pydantic models (Sample, SuiteSpec, GraderSpec, etc.)
│   ├── suite.py        # Suite configuration loader
│   ├── runner.py       # Evaluation runner
│   ├── graders/        # Grader implementations
│   │   ├── tool_graders.py   # exact_match, contains, regex, etc.
│   │   └── rubric_grader.py  # LLM-as-judge grading
│   ├── gates.py        # Pass/fail gate evaluation
│   └── dataset.py      # Dataset loading utilities
├── taxonomy/           # Hierarchical classification system
│   ├── schema.py       # TaxonomyNode, TaxonomyDimension, SampleTaxonomy
│   ├── registry.py     # Built-in cybersecurity taxonomy
│   └── mapper.py       # Rule-based and inference-based mapping
├── providers/          # Model provider implementations
└── suites/             # Suite-specific runners (CS-Eval, CyberGym, CVE-Bench)

configs/
├── evals/              # Evaluation suite configs
│   ├── example_qa.yaml
│   ├── example_code.yaml
│   └── example_rubric.yaml
├── taxonomy/           # Taxonomy mapping configs
└── examples/           # Pipeline config examples
```

## Evals Framework

The evals framework provides a flexible way to define and run evaluations.

### Suite Configuration

Suites are defined in YAML:

```yaml
name: example-qa
description: Question-answering evaluation

dataset: ./data/questions.jsonl

target:
  provider: ollama
  model: llama3.2
  temperature: 0.0

graders:
  accuracy:
    kind: tool
    function: exact_match
    extractor:
      name: first_line

gate:
  metric_key: accuracy
  op: gte
  value: 0.7
```

### Built-in Graders

| Grader | Description |
|--------|-------------|
| `exact_match` | Exact string comparison |
| `contains` | Check if expected is contained in output |
| `regex` | Pattern matching |
| `numeric_tolerance` | Numeric comparison with tolerance |
| `code_execution` | Execute code and compare output |
| `rubric` | LLM-as-judge with customizable rubrics |

### Custom Graders

Register custom graders with the `@grader` decorator:

```python
from model_benchmarking.evals.graders import grader, GradeResult

@grader("my_custom_grader")
def my_grader(output: str, expected: str, **config) -> GradeResult:
    score = 1.0 if some_condition(output, expected) else 0.0
    return GradeResult(score=score, rationale="...")
```

## Taxonomy System

The taxonomy provides hierarchical classification for evaluation samples.

### Dimensions

| Dimension | Description | Example Values |
|-----------|-------------|----------------|
| `capability` | Security skill being tested | exploit_development, vulnerability_analysis, secure_coding |
| `domain` | Security domain | network, web, binary, cloud, cryptography |
| `difficulty` | Normalized difficulty | trivial, easy, medium, hard, expert |
| `cwe` | CWE weakness ID | CWE-79, CWE-89, CWE-120 |
| `attack_stage` | MITRE ATT&CK stage | reconnaissance, initial_access, execution |
| `eval_type` | Type of evaluation | knowledge, practical, code_generation |

### Usage

```python
from model_benchmarking.taxonomy import get_taxonomy, TaxonomyMapper, AutoMapper

# Get the built-in cybersecurity taxonomy
taxonomy = get_taxonomy("cybersecurity")

# Map samples using rules
mapper = TaxonomyMapper("cybersecurity")
mapper.add_rule(MappingRule(
    dimension="domain",
    target_value="web",
    field="category",
    contains=["Web", "HTTP", "API"]
))
result = mapper.map(sample)

# Auto-infer taxonomy from sample content
auto = AutoMapper(taxonomy)
inferred = auto.infer({"prompt": "Explain SQL injection attacks"})
```

### CLI Commands

```bash
# List available taxonomies
mbenchmark taxonomy list

# Show taxonomy details
mbenchmark taxonomy show cybersecurity
mbenchmark taxonomy show cybersecurity --dimension capability
```

## Benchmark Suites

### CS-Eval
Text-based Q&A benchmarks testing security knowledge and reasoning.

```bash
mbenchmark run --suite cs-eval
```

### CVE-Bench
Challenge-driven fixtures with vulnerable container images.

```bash
mbenchmark run --suite cve-bench
```

### CyberGym
Interactive scenario simulations for multi-step security tasks.

```bash
mbenchmark run --suite cybergym
```

## Providers

| Provider | Description |
|----------|-------------|
| `ollama` | Local Ollama server |
| `strands-ollama` | Strands SDK with Ollama backend |
| `mock` | Deterministic mock for testing (no network) |

## Docker

```bash
# Build the image
docker build -t model-benchmarking:local .

# Run evaluation in container
docker run --rm -v $(pwd):/workspace -w /workspace \
  model-benchmarking:local pipeline --provider mock --skip-cs-eval
```

## Development

```bash
# Install dev dependencies
pip install -r requirements-dev.txt

# Run tests
pytest tests/

# Run specific test file
pytest tests/test_taxonomy.py -v
```

## Configuration

### Environment Variables

- `OLLAMA_HOST` — Ollama server URL (default: `http://localhost:11434`)
- `CYBERGYM_SERVER` — CyberGym server URL
- `CVEBENCH_ROOT` — Path to CVE-Bench repository

### Pipeline Config

```yaml
# configs/examples/pipeline.minimal.yaml
provider:
  name: mock
  model: mock

pipeline:
  output_dir: results
  skip_cs_eval: true
  verbose: true
```

## Safety

This repository contains intentionally vulnerable challenge content for security evaluation. Always run CVE-Bench and CyberGym workloads in isolated environments.

## License

See [LICENSE](LICENSE) for details.


