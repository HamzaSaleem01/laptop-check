"""Safe Non-Destructive Storage Benchmark for LaptopCheck.
Strict safety rules:
- Uses ONLY temporary test files in standard scratch / user cache directories.
- NEVER modifies partitions, boot records, or disk formatting.
- Automatically cleans up and removes all test files immediately.
"""
import os
import time
import tempfile
from typing import Optional, Callable
from agent.benchmarks.base import BaseBenchmark
from agent.models import BenchmarkResult, BenchmarkMetric, StatusEnum
from agent.safety.controller import SafetyController

class StorageBenchmark(BaseBenchmark):
    """Measures safe disk read/write throughput using non-destructive temporary files."""

    def __init__(self):
        super().__init__("storage", "Storage Sequential Read/Write")
        self._test_filepath: Optional[str] = None

    def prepare(self) -> None:
        self._stopped = False
        # Create temp file in user temp directory
        temp_dir = tempfile.gettempdir()
        self._test_filepath = os.path.join(temp_dir, f"laptopcheck_safe_test_{int(time.time())}.tmp")

    def run(
        self,
        duration_secs: int,
        safety: SafetyController,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> BenchmarkResult:
        self._stopped = False
        start_time = time.time()
        
        # Test size: 50MB for Quick test, safe and rapid
        test_size_mb = 50
        block_size = 1024 * 1024  # 1 MB blocks
        total_blocks = test_size_mb
        random_block = os.urandom(block_size)

        write_speed_mb_s = 0.0
        read_speed_mb_s = 0.0

        try:
            if not self._test_filepath:
                self.prepare()

            # Sequential Write Phase
            if progress_callback:
                progress_callback(0.1, f"Safe Storage: Sequential Write ({test_size_mb} MB)...")

            t_write_start = time.time()
            with open(self._test_filepath, "wb") as f:
                for b_idx in range(total_blocks):
                    if safety.is_stopped() or self._stopped:
                        break
                    f.write(random_block)
                    if progress_callback and b_idx % 10 == 0:
                        pct = 0.1 + 0.4 * (b_idx / total_blocks)
                        progress_callback(pct, f"Writing test file {b_idx}/{total_blocks} MB...")
                f.flush()
                os.fsync(f.fileno())
            t_write_end = time.time()
            w_time = max(0.001, t_write_end - t_write_start)
            write_speed_mb_s = round(test_size_mb / w_time, 1)

            # Sequential Read Phase
            if not safety.is_stopped() and not self._stopped:
                if progress_callback:
                    progress_callback(0.55, f"Safe Storage: Sequential Read ({test_size_mb} MB)...")

                t_read_start = time.time()
                bytes_read = 0
                with open(self._test_filepath, "rb") as f:
                    while True:
                        if safety.is_stopped() or self._stopped:
                            break
                        chunk = f.read(block_size)
                        if not chunk:
                            break
                        bytes_read += len(chunk)
                        if progress_callback:
                            pct = 0.55 + 0.4 * (bytes_read / (test_size_mb * block_size))
                            progress_callback(pct, f"Reading test file {int(bytes_read / (1024*1024))} MB...")
                t_read_end = time.time()
                r_time = max(0.001, t_read_end - t_read_start)
                read_speed_mb_s = round((bytes_read / (1024 * 1024)) / r_time, 1)

        finally:
            self.cleanup()

        total_duration = time.time() - start_time
        avg_speed = round((write_speed_mb_s + read_speed_mb_s) / 2.0, 1)
        score = round(avg_speed * 2.0, 1)

        # Classification
        status = StatusEnum.PASS
        if avg_speed < 150.0:  # Below SATA SSD typical speeds
            status = StatusEnum.CAUTION

        metrics = [
            BenchmarkMetric(name="Sequential Write", value=write_speed_mb_s, unit="MB/s", description="Non-destructive temporary file write speed"),
            BenchmarkMetric(name="Sequential Read", value=read_speed_mb_s, unit="MB/s", description="Buffered temporary file read speed"),
            BenchmarkMetric(name="Average Speed", value=avg_speed, unit="MB/s", description="Mean sequential storage throughput"),
            BenchmarkMetric(name="Test File Size", value=float(test_size_mb), unit="MB", description="Controlled temporary write test payload")
        ]

        details = f"Non-destructive test wrote and read {test_size_mb}MB. Write: {write_speed_mb_s} MB/s, Read: {read_speed_mb_s} MB/s. Cleaned up successfully."

        return BenchmarkResult(
            benchmark_id="storage",
            display_name=self.display_name,
            duration_secs=round(total_duration, 1),
            score=score,
            metrics=metrics,
            status=status,
            details=details
        )

    def cleanup(self) -> None:
        self._stopped = True
        if self._test_filepath and os.path.exists(self._test_filepath):
            try:
                os.remove(self._test_filepath)
            except Exception:
                pass
            self._test_filepath = None
