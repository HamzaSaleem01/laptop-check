"""Unit tests for Storage Benchmark Non-Destructive Safety."""
import os
from agent.benchmarks.storage import StorageBenchmark
from agent.safety.controller import SafetyController
from agent.models import StatusEnum

def test_storage_benchmark_creates_and_removes_temp_file():
    benchmark = StorageBenchmark()
    safety = SafetyController()
    
    # Run short safe storage test
    result = benchmark.run(duration_secs=2, safety=safety)
    
    assert result.benchmark_id == "storage"
    assert result.status in [StatusEnum.PASS, StatusEnum.CAUTION]
    assert len(result.metrics) >= 3
    
    # Ensure temporary file is cleanly removed
    if benchmark._test_filepath:
        assert not os.path.exists(benchmark._test_filepath)
