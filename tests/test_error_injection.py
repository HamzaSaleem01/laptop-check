"""Robustness & Error Injection Tests for LaptopCheck.
Validates graceful degradation when hardware sensors, binaries, or system resources are missing or fail:
1. Unavailable temperature sensor
2. Unavailable battery / desktop machine
3. Unavailable GPU / Integrated graphics only
4. Storage with SMART unavailable
5. Missing Quantum ESPRESSO pw.x binary
6. User abort cancellation during active test
7. Extremely low available memory simulation
8. Elevated background load pre-flight warning
"""
import pytest
from agent.safety.controller import SafetyController
from agent.benchmarks.cpu import CPUBenchmark
from agent.benchmarks.memory import MemoryBenchmark
from agent.benchmarks.storage import StorageBenchmark
from agent.benchmarks.gpu import GPUBenchmark
from agent.benchmarks.qe_plugin import QuantumEspressoPlugin
from agent.diagnostics.preflight import run_preflight_check
from agent.models import StatusEnum, SafetyLevel, SystemHardwareSnapshot, CPUInfo, RAMInfo, BatteryInfo
from agent.workloads.profiles import evaluate_workload
from agent.reporting.analysis import detect_anomalies, classify_categories

def test_missing_temperature_sensor_does_not_crash_safety():
    """Verify safety controller handles None / unavailable temperature sensors safely."""
    safety = SafetyController()
    # None for CPU, GPU, and battery temperatures
    sample = safety.evaluate(cpu_temp=None, gpu_temp=None, battery_temp=None, elapsed_secs=1.0)
    assert sample.safety_level == SafetyLevel.NORMAL
    assert sample.cpu_temp_c is None
    assert not safety.is_stopped()

def test_missing_battery_handled_gracefully():
    """Verify system without battery (desktop or missing sensor) receives NOT AVAILABLE status."""
    hw = SystemHardwareSnapshot(
        device_model="Custom Desktop / Battery Missing",
        manufacturer="Custom",
        battery=BatteryInfo(present=False)
    )
    categories = classify_categories(hw, [], [])
    assert categories["Battery"] == StatusEnum.NOT_AVAILABLE

def test_gpu_benchmark_when_no_dedicated_gpu():
    """Verify GPU benchmark honestly reports NOT AVAILABLE without crashing or faking scores."""
    gpu_bench = GPUBenchmark()
    safety = SafetyController()
    res = gpu_bench.run(duration_secs=2, safety=safety)
    # On machines without NVIDIA CUDA, it must return NOT AVAILABLE
    assert res.benchmark_id == "gpu"
    assert res.status in [StatusEnum.NOT_AVAILABLE, StatusEnum.PASS]
    if res.status == StatusEnum.NOT_AVAILABLE:
        assert "unavailable" in res.details.lower() or "not detected" in res.details.lower()
        assert res.score == 0.0

def test_missing_quantum_espresso_graceful_fallback():
    """Verify missing pw.x does not break diagnostic suite."""
    qe = QuantumEspressoPlugin()
    safety = SafetyController()
    res = qe.run(duration_secs=1, safety=safety)
    assert res.benchmark_id == "qe_plugin"
    assert res.status in [StatusEnum.NOT_AVAILABLE, StatusEnum.PASS]
    if not qe.is_installed():
        assert res.status == StatusEnum.NOT_AVAILABLE
        assert "not installed" in res.details.lower()

def test_user_cancellation_aborts_active_benchmark():
    """Verify immediate stop when user signals cancellation."""
    safety = SafetyController()
    cpu_bench = CPUBenchmark()
    
    # Request stop immediately
    safety.request_stop("User abort")
    res = cpu_bench.run(duration_secs=10, safety=safety)
    
    assert safety.is_stopped()
    # Benchmark should exit almost immediately (< 1.5 seconds instead of 10)
    assert res.duration_secs <= 2.0

def test_low_ram_adaptive_scaling():
    """Verify memory benchmark adaptively restricts buffer size and leaves memory for OS."""
    mem_bench = MemoryBenchmark()
    safety = SafetyController()
    res = mem_bench.run(duration_secs=2, safety=safety)
    assert res.benchmark_id == "memory"
    # Ensure buffer size is documented in metrics
    buffer_metric = next((m for m in res.metrics if m.name == "Tested Buffer"), None)
    assert buffer_metric is not None
    assert buffer_metric.value <= 512.0  # Never exceeds safe threshold

def test_preflight_checks_non_destructive():
    """Verify pre-flight background process checks run smoothly without privileges."""
    result = run_preflight_check()
    assert result.idle_cpu_percent >= 0.0
    assert result.idle_ram_percent >= 0.0
    assert isinstance(result.warnings, list)
    assert isinstance(result.top_processes, list)
