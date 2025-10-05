import pytest

from model_benchmarking.runner import run_benchmark, BenchmarkResult


def test_run_benchmark_unknown_suite():
    with pytest.raises(ValueError):
        run_benchmark('unknown-suite')


def test_run_benchmark_test_mode():
    res = run_benchmark('cs-eval', test_mode=True)
    assert isinstance(res, BenchmarkResult)
    assert res.status == 'ok'
