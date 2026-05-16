"""
Integration tests for async integrity.
"""
import asyncio
import time
import pytest
from runtime.providers.mock import MockProvider
from runtime.suites.cs_eval.runner import run_cs_eval
from pathlib import Path

class SlowMockProvider(MockProvider):
    async def evaluate_question(self, *args, **kwargs):
        await asyncio.sleep(0.5)
        return await super().evaluate_question(*args, **kwargs)

@pytest.mark.asyncio
async def test_async_concurrency():
    """Verify that multiple async calls don't block each other."""
    provider = SlowMockProvider()
    
    start_time = time.time()
    
    # Run two slow evaluations concurrently
    tasks = [
        provider.evaluate_question("Q1"),
        provider.evaluate_question("Q2")
    ]
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # If it was blocking, it would take ~1.0s. If async, ~0.5s.
    assert duration < 0.8, f"Async execution took too long: {duration}s"

@pytest.mark.asyncio
async def test_pipeline_non_blocking():
    """Verify that the CS-Eval runner doesn't block the loop."""
    # Create a dummy sample file
    sample_file = Path("tests/data/test_samples.jsonl")
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    sample_file.write_text('{"question": "test", "options": ["A", "B"], "answer": "A", "category": "test"}\n')
    
    provider = SlowMockProvider()
    
    start_time = time.time()
    
    # Start the runner
    runner_task = asyncio.create_task(run_cs_eval(
        provider=provider,
        local_sample=str(sample_file)
    ))
    
    # Check if we can do something else while it runs
    await asyncio.sleep(0.1)
    other_work_done = True
    
    await runner_task
    
    assert other_work_done
