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