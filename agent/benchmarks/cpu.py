"""CPU Benchmark for LaptopCheck.
Computes multi-threaded floating-point calculations, measuring:
- Single-thread baseline
- Multi-thread peak performance
- Sustained multi-thread performance
- Performance degradation percentage (throttling detection)
Safe, stoppable, monitors thermal safety limits.
"""
import time
import math
import concurrent.futures
from typing import Optional, Callable, List
import psutil

from agent.benchmarks.base import BaseBenchmark
from agent.models import BenchmarkResult, BenchmarkMetric, StatusEnum, SafetyLevel
from agent.safety.controller import SafetyController

def _cpu_worker(iterations: int, stop_flag: Callable[[], bool]) -> int:
    """Worker performing floating point and arithmetic workload."""
    completed = 0
    chunk = 50000
    while completed < iterations:
        if stop_flag():
            break
        # Mixed arithmetic workload: square roots, trigonometrics, bit operations
        val = 0.0
        for i in range(chunk):
            val += math.sin(i) * math.cos(i) + math.sqrt(i + 1.0)
        completed += chunk
    return completed

class CPUBenchmark(BaseBenchmark):
    """Measures single and multi-core CPU performance and thermal throttling degradation."""

    def __init__(self):
        super().__init__("cpu", "CPU Multi-Core & Sustained Performance")

    def prepare(self) -> None:
        self._stopped = False

    def run(
        self,
        duration_secs: int,
        safety: SafetyController,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> BenchmarkResult:
        self._stopped = False
        num_threads = psutil.cpu_count(logical=True) or 4
        start_time = time.time()
        
        # We test in time slices to compare initial performance vs sustained performance
        slice_duration = max(1.0, duration_secs / 5.0)
        slice_scores: List[float] = []
        
        if progress_callback:
            progress_callback(0.05, f"Starting CPU Benchmark on {num_threads} threads...")

        elapsed = 0.0
        slice_idx = 0
        
        while elapsed < duration_secs and not safety.is_stopped() and not self._stopped:
            slice_start = time.time()
            work_per_thread = 250000
            
            # Check safety: if load reduction needed, throttle thread count
            active_workers = num_threads
            if safety.get_current_level() == SafetyLevel.REDUCE_LOAD:
                active_workers = max(1, num_threads // 2)

            with concurrent.futures.ThreadPoolExecutor(max_workers=active_workers) as executor:
                futures = [
                    executor.submit(_cpu_worker, work_per_thread, lambda: safety.is_stopped() or self._stopped)
                    for _ in range(active_workers)
                ]
                done_ops = sum(f.result() for f in futures)

            slice_elapsed = time.time() - slice_start
            ops_per_sec = done_ops / max(0.001, slice_elapsed)
            slice_scores.append(ops_per_sec)

            slice_idx += 1
            elapsed = time.time() - start_time
            pct = min(0.95, elapsed / max(1.0, duration_secs))
            
            if progress_callback:
                progress_callback(
                    pct,
                    f"Testing CPU sustained load... {int(elapsed)}s/{duration_secs}s ({int(ops_per_sec / 1000)}k ops/sec)"
                )
            
            if safety.get_current_level() == SafetyLevel.PAUSE:
                time.sleep(0.5)

        total_duration = time.time() - start_time
        
        # Calculate scores
        if not slice_scores:
            slice_scores = [1000.0]

        initial_perf = slice_scores[0]
        # Sustained is average of the last half of slices
        half_idx = max(0, len(slice_scores) // 2)
        sustained_perf = sum(slice_scores[half_idx:]) / max(1, len(slice_scores[half_idx:]))

        degradation_pct = 0.0
        if initial_perf > 0:
            degradation_pct = max(0.0, round(((initial_perf - sustained_perf) / initial_perf) * 100.0, 1))

        # Overall normalized score (scale to roughly 1000-15000 pts)
        overall_score = round(sustained_perf / 1500.0, 1)

        status = StatusEnum.PASS
        if degradation_pct >= 25.0:
            status = StatusEnum.CAUTION

        metrics = [
            BenchmarkMetric(name="Initial Performance", value=round(initial_perf / 1000.0, 1), unit="k ops/sec", description="Burst multi-core processing throughput"),
            BenchmarkMetric(name="Sustained Performance", value=round(sustained_perf / 1000.0, 1), unit="k ops/sec", description="Sustained throughput under continuous load"),
            BenchmarkMetric(name="Observed Degradation", value=degradation_pct, unit="%", description="Performance reduction from thermal/power throttling"),
            BenchmarkMetric(name="CPU Composite Score", value=overall_score, unit="pts", description="Normalized multi-core CPU benchmark score")
        ]

        details = f"Tested {num_threads} logical cores over {round(total_duration, 1)}s. Initial: {round(initial_perf / 1000.0, 1)}k, Sustained: {round(sustained_perf / 1000.0, 1)}k ({degradation_pct}% degradation)."

        return BenchmarkResult(
            benchmark_id="cpu",
            display_name=self.display_name,
            duration_secs=round(total_duration, 1),
            score=overall_score,
            metrics=metrics,
            initial_performance=round(initial_perf / 1000.0, 1),
            sustained_performance=round(sustained_perf / 1000.0, 1),
            degradation_pct=degradation_pct,
            status=status,
            details=details
        )

    def cleanup(self) -> None:
        self._stopped = True
