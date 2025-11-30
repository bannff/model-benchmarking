# Evals Framework

A modular, provider-agnostic evaluation framework for benchmarking language models.

## Overview

The evals framework provides a flexible pipeline for evaluating model outputs:

```
Dataset → Target (Model) → Extractor → Grader → Gate → Result
```

Key features:
- **JSONL datasets** with metadata and tag filtering
- **Pluggable extractors** for parsing model responses
- **Tool graders** (exact_match, contains, regex, etc.)
- **LLM-as-judge rubric graders** for semantic evaluation
- **Configurable pass/fail gates**
- **YAML-driven suite definitions**
- **Async execution with concurrency control**

## Quick Start

### CLI Usage

```bash
# Run an evaluation suite
mbenchmark evals run configs/evals/example_qa.yaml --provider ollama --model llama3.2

# Validate a suite config
mbenchmark evals validate configs/evals/example_qa.yaml

# List available graders
mbenchmark evals list-graders

# List available extractors
mbenchmark evals list-extractors
```

### Programmatic Usage

```python
import asyncio
from model_benchmarking.evals import run_suite
from model_benchmarking.providers.factory import make_provider

# Create provider
provider = make_provider("ollama", model="llama3.2")

# Run evaluation
result = asyncio.run(run_suite("suite.yaml", provider))

print(f"Pass rate: {result.metrics.pass_rate:.2%}")
print(f"Gate: {'PASSED' if result.gate_passed else 'FAILED'}")
```

## Suite Configuration

Suites are defined in YAML format:

```yaml
name: my-evaluation
description: Evaluation description

# Dataset (relative or absolute path to JSONL file)
dataset: data/questions.jsonl

# Target model configuration
target:
  provider: ollama
  model: ${MODEL:-llama3.2}
  temperature: 0.0

# Graders (one or more)
graders:
  accuracy:
    kind: tool
    function: exact_match
    extractor:
      name: first_line
    config:
      case_sensitive: false
  
  quality:
    kind: rubric
    prompt: |
      Evaluate the response quality...
      Return: {"score": 0.0-1.0, "rationale": "..."}
    model: llama3.2

# Pass/fail gate
gate:
  metric_key: accuracy
  op: gte   # gte, gt, lte, lt, eq
  value: 0.8

# Execution settings
max_samples: 100
max_concurrent: 5
```

## Dataset Format

Datasets are JSONL files with one sample per line:

```jsonl
{"id": "001", "input": "What is the capital of France?", "ground_truth": "Paris", "tags": ["geography"]}
{"id": "002", "input": "Calculate 2+2", "ground_truth": "4", "tags": ["math"], "context": "Answer with just the number."}
```

Required fields:
- `id`: Unique identifier
- `input`: The question/prompt for the model

Optional fields:
- `ground_truth`: Expected answer (for grading)
- `context`: Additional context prepended to input
- `system_prompt`: System prompt for chat models
- `tags`: List of tags for filtering
- `metadata`: Additional metadata

## Extractors

Extractors parse model responses before grading:

| Extractor | Description | Config |
|-----------|-------------|--------|
| `last_assistant` | Last assistant message in chat | - |
| `all_text` | Full response text | - |
| `first_line` | First line only | - |
| `json_field` | Parse JSON, extract field | `field`, `default` |
| `regex` | Regex capture group | `pattern`, `group`, `flags` |
| `code_block` | Extract code from markdown | `language`, `index` |
| `tool_calls` | Extract tool call info | `tool_name`, `extract` |

## Graders

### Tool Graders (Deterministic)

| Function | Description | Config |
|----------|-------------|--------|
| `exact_match` | Exact string match | `case_sensitive` |
| `contains` | Substring match | `case_sensitive` |
| `regex` | Regex pattern match | `pattern`, `flags` |
| `starts_with` | Prefix match | `case_sensitive` |
| `ends_with` | Suffix match | `case_sensitive` |
| `numeric` | Numeric comparison | `tolerance`, `relative` |
| `json_match` | JSON structure equality | `ignore_keys` |
| `length` | Length constraints | `min`, `max` |

### Rubric Graders (LLM-as-Judge)

Use an LLM to evaluate responses against a rubric:

```yaml
graders:
  quality:
    kind: rubric
    prompt: |
      Question: {{ input }}
      Expected: {{ ground_truth }}
      Response: {{ submission }}
      
      Rate 0.0-1.0 for accuracy and clarity.
      Return: {"score": <float>, "rationale": "<reason>"}
    model: gpt-4
    temperature: 0.0
```

Template variables:
- `{{ input }}` - Original input/question
- `{{ ground_truth }}` - Expected answer
- `{{ submission }}` - Extracted model response
- `{{ context }}` - Sample context
- Any field from `rubric_vars` in the sample

## Gates

Gates determine pass/fail based on aggregate metrics:

```yaml
gate:
  metric_key: accuracy   # Which grader's score to use
  op: gte                # Operator: gte, gt, lte, lt, eq
  value: 0.8             # Threshold
```

## Environment Variables

Suite configs support environment variable interpolation:

```yaml
target:
  model: ${MODEL:-default-model}
  host: ${API_HOST}
```

- `${VAR}` - Required variable
- `${VAR:-default}` - With default value

## Output

The runner returns a `RunnerResult` with:

```python
result.suite_name       # Suite name
result.model_name       # Model used
result.results          # List of SampleResult
result.metrics          # Metrics object
result.gate_passed      # Boolean
result.gate_details     # Gate evaluation message
```

Metrics include:
- `total`, `attempted`, `failed`
- `avg_score`, `pass_rate`
- `by_metric` - Scores by grader name
- `by_tag` - Scores by sample tag

## Extending

### Custom Extractors

```python
from model_benchmarking.evals.extractors import BaseExtractor, ExtractorRegistry

class MyExtractor(BaseExtractor):
    def extract(self, response: str, **kwargs) -> str:
        return response.upper()

ExtractorRegistry.register("my_extractor", MyExtractor)
```

### Custom Graders

```python
from model_benchmarking.evals.graders import grader, GradeResult

@grader
def my_grader(submission: str, ground_truth: str, config: dict, sample) -> GradeResult:
    score = 1.0 if submission == ground_truth else 0.0
    return GradeResult(score=score, rationale="Custom logic")
```

## Examples

See `configs/evals/` for example suite configurations:
- `example_qa.yaml` - Basic Q&A with exact match
- `example_rubric.yaml` - Open-ended with LLM judge
- `example_code.yaml` - Code generation with multi-grading
