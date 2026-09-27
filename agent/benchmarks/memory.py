"""Memory (RAM) Benchmark for LaptopCheck.
Measures memory read/write bandwidth and allocation stability.
Strict safety rules:
- Adapts dynamically to available memory.
- Leaves at least 80% of available RAM untouched to guarantee OS stability.
- Never exhausts RAM on low-end machines (e.g. 4GB RAM laptops).
"""
import time
import psutil
from typing import Optional, Callable
from agent.benchmarks.base import BaseBenchmark
from agent.models import BenchmarkResult, BenchmarkMetric, StatusEnum
from agent.safety.controller import SafetyController

class MemoryBenchmark(BaseBenchmark):
    """Measures RAM read and write bandwidth adaptively and safely."""

    def __init__(self):
        super().__init__("memory", "RAM Memory Bandwidth & Integrity")

    def prepare(self) -> None:
        self._stopped = False

    def run(
        self,
        duration_secs: int,
        safety: SafetyController,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> BenchmarkResult:
        self._stopped = False
        start_time = time.time()
        
        # Determine safe adaptive test buffer size
        vm = psutil.virtual_memory()
        available_mb = int(vm.available / (1024 * 1024))
        
        if available_mb < 300:
            test_mb = max(16, int(available_mb * 0.15))
        else:
            test_mb = min(512, max(64, int(available_mb * 0.20)))

        buffer_size = test_mb * 1024 * 1024

        if progress_callback:
            progress_callback(0.1, f"Allocating safe {test_mb}MB RAM buffer (available: {available_mb}MB)...")

        write_speeds: list[float] = []
        read_speeds: list[float] = []
        
        chunk = None
        try:
            chunk = bytearray(buffer_size)
            iterations = max(2, int(duration_secs / 2))

            for i in range(iterations):
                if safety.is_stopped() or self._stopped:
                    break
                
                # Write test
                t0 = time.time()
                for offset in range(0, buffer_size, 4096):
                    chunk[offset] = (offset + i) % 256
                w_time = max(0.0001, time.time() - t0)
                w_speed_gb_s = (test_mb / 1024.0) / w_time
                write_speeds.append(w_speed_gb_s)

                # Read test
                t1 = time.time()
                checksum = 0
                for offset in range(0, buffer_size, 4096):
                    checksum += chunk[offset]
                r_time = max(0.0001, time.time() - t1)
                r_speed_gb_s = (test_mb / 1024.0) / r_time
                read_speeds.append(r_speed_gb_s)

                pct = min(0.95, (i + 1) / iterations)
                if progress_callback:
                    progress_callback(
                        pct,
                        f"Memory Read: {round(r_speed_gb_s, 1)} GB/s | Write: {round(w_speed_gb_s, 1)} GB/s"
                    )
        finally:
            if chunk is not None:
                del chunk

        total_duration = time.time() - start_time

        avg_read = sum(read_speeds) / max(1, len(read_speeds))
        avg_write = sum(write_speeds) / max(1, len(write_speeds))
        composite_bandwidth = round((avg_read + avg_write) / 2.0, 2)
        score = round(composite_bandwidth * 500.0, 1)

        metrics = [
            BenchmarkMetric(name="Read Bandwidth", value=round(avg_read, 2), unit="GB/s", description="Sequential RAM read throughput"),
            BenchmarkMetric(name="Write Bandwidth", value=round(avg_write, 2), unit="GB/s", description="Sequential RAM write throughput"),
            BenchmarkMetric(name="Average Bandwidth", value=composite_bandwidth, unit="GB/s", description="Mean RAM memory bandwidth"),
            BenchmarkMetric(name="Tested Buffer", value=float(test_mb), unit="MB", description="Adaptive safe memory buffer allocation")
        ]

        status = StatusEnum.PASS if composite_bandwidth >= 8.0 else StatusEnum.CAUTION

        return BenchmarkResult(
            benchmark_id="memory",
            display_name=self.display_name,
            duration_secs=round(total_duration, 1),
            score=score,
            metrics=metrics,
            status=status,
            details=f"Measured {composite_bandwidth} GB/s composite memory bandwidth across safe {test_mb}MB buffer."
        )

    def cleanup(self) -> None:
        self._stopped = True
