# Workflow: Adding a New Benchmark Suite

Follow these steps to integrate a new evaluation suite into the `Model-Benchmarking` framework.

## 📋 Prerequisites

-   A dataset in JSONL or CSV format.
-   A clear understanding of the success criteria (grading logic).

## 🚀 Steps

1.  **Define the Spec**:
    Create a new YAML configuration in `configs/evals/`.
    ```yaml
    name: new-suite
    dataset: ./data/new-suite.jsonl
    graders:
      score:
        kind: tool
        function: exact_match
    ```

2.  **Implement the Adapter** (if needed):
    If the suite requires custom loading or execution logic, create a new file in `src/model_benchmarking/suites/`.

3.  **Map to Taxonomy**:
    Ensure the dataset includes taxonomy metadata or define mapping rules in `configs/taxonomy/`.

4.  **Register with CLI**:
    Add the suite to the `SuiteRegistry` in `src/model_benchmarking/evals/suite.py`.

5.  **Verify**:
    Run a minimal test:
    ```bash
    mbenchmark pipeline --suite new-suite --max-items 5
    ```

6.  **Document**:
    Add the new suite to the root `README.md`.

---

*Scale the rigor.*
