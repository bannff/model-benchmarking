import os
import subprocess
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class BenchmarkResult:
    name: str
    status: str
    output_path: Optional[str] = None


def _run_script(script_path: str, args: Optional[List[str]] = None) -> int:
    args = list(args) if args else []
    # run script from repo root so relative paths in scripts continue to work
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    full_script = os.path.join(repo_root, script_path)
    if not os.path.exists(full_script):
        raise FileNotFoundError(full_script)
    cmd = ["python", full_script] + list(args)
    proc = subprocess.run(cmd, cwd=repo_root)
    return proc.returncode


def run_benchmark(suite: str, config_path: Optional[str] = None, test_mode: bool = False) -> BenchmarkResult:
    """Run a benchmark suite by invoking existing scripts (shim).

    This keeps the original suite folders intact while providing a
    stable Python API.
    """
    suite = suite.lower()
    if test_mode:
        # In test mode, return a lightweight deterministic result without shelling out.
        return BenchmarkResult(name=suite, status="ok", output_path=None)
    if suite in ("cs-eval", "cseval"):
        # call the generic cs-eval runner
        rc = _run_script(
            "benchmarking/cs-eval/run_evaluation.py",
            [
                "--categories",
                "Network Security",
                "--max_questions",
                "2",
                "--batch_size",
                "2",
                "--verbose",
            ],
        )
        status = "ok" if rc == 0 else "failed"
        return BenchmarkResult(name="cs-eval", status=status)
    elif suite in ("cybersec-quiz", "quiz", "cybersec"):
        rc = _run_script("benchmark-test/cybersec_quiz.py")
        status = "ok" if rc == 0 else "failed"
        return BenchmarkResult(name="cybersec_quiz", status=status)
    elif suite in ("cve-bench", "cve"):
        # use the run helper in cve-bench once setup
        rc = _run_script("benchmarking/cve-bench/run", ["eval"])  # default eval
        status = "ok" if rc == 0 else "failed"
        return BenchmarkResult(name="cve-bench", status=status)
    else:
        raise ValueError(f"Unknown suite: {suite}")
