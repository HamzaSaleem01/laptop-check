"""Scientific Computing / Materials Science Benchmark for LaptopCheck.
Executes controlled numerical workloads:
- Dense Matrix Multiplication (GEMM - BLAS/LAPACK)
- Fast Fourier Transforms (FFT - 2D/3D frequency grid)
- Linear equation solving (LU decomposition)
Relevant for Density Functional Theory (DFT), ASE, NumPy, and scientific simulations.
"""
import time
import numpy as np
from typing import Optional, Callable
from agent.benchmarks.base import BaseBenchmark
from agent.models import BenchmarkResult, BenchmarkMetric, StatusEnum
from agent.safety.controller import SafetyController

class ScientificBenchmark(BaseBenchmark):
    """Numerical scientific compute benchmark simulating DFT / physics algorithms."""

    def __init__(self):
        super().__init__("scientific", "Scientific Computing & Numerical BLAS")

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
        
        # Test sizes
        matrix_n = 1024  # 1024x1024 double precision matrix = 8 MB per matrix
        fft_dim = 1024

        gemm_times = []
        fft_times = []

        if progress_callback:
            progress_callback(0.05, "Scientific Benchmark: Initializing BLAS matrices...")

        iteration = 0
        while (time.time() - start_time) < duration_secs and not safety.is_stopped() and not self._stopped:
            iteration += 1
            
            # Phase 1: Matrix Multiplication (GEMM)
            # Floating point operations for N x N matrix multiply is 2 * N^3
            t0 = time.time()
            A = np.random.randn(matrix_n, matrix_n).astype(np.float64)
            B = np.random.randn(matrix_n, matrix_n).astype(np.float64)
            C = np.dot(A, B)
            t_gemm = max(0.0001, time.time() - t0)
            gemm_times.append(t_gemm)

            if safety.is_stopped() or self._stopped:
                break

            # Phase 2: 2D Fast Fourier Transform (FFT)
            t1 = time.time()
            grid = np.random.randn(fft_dim, fft_dim).astype(np.complex128)
            freq_grid = np.fft.fft2(grid)
            t_fft = max(0.0001, time.time() - t1)
            fft_times.append(t_fft)

            elapsed = time.time() - start_time
            pct = min(0.95, elapsed / max(1.0, duration_secs))
            
            # Calculate current GFLOPS: (2 * N^3) / (t_gemm * 10^9)
            gflops = (2.0 * (matrix_n ** 3)) / (t_gemm * 1e9)
            if progress_callback:
                progress_callback(
                    pct,
                    f"Scientific BLAS: GEMM {round(gflops, 1)} GFLOPS | FFT2 {round(t_fft*1000, 1)} ms"
                )

        total_duration = time.time() - start_time
        
        # Aggregate metrics
        avg_gemm = sum(gemm_times) / max(1, len(gemm_times))
        avg_fft_ms = (sum(fft_times) / max(1, len(fft_times))) * 1000.0
        peak_gflops = round((2.0 * (matrix_n ** 3)) / (min(gemm_times or [1.0]) * 1e9), 1)
        avg_gflops = round((2.0 * (matrix_n ** 3)) / (avg_gemm * 1e9), 1)

        # Scientific compute score
        score = round(avg_gflops * 150.0, 1)

        status = StatusEnum.PASS if avg_gflops >= 15.0 else StatusEnum.CAUTION

        metrics = [
            BenchmarkMetric(name="BLAS GEMM Throughput", value=avg_gflops, unit="GFLOPS", description="Double-precision dense matrix multiplication throughput"),
            BenchmarkMetric(name="Peak BLAS GEMM", value=peak_gflops, unit="GFLOPS", description="Burst maximum matrix multiplication throughput"),
            BenchmarkMetric(name="2D FFT Latency", value=round(avg_fft_ms, 2), unit="ms", description="1024x1024 2D complex Fourier transform time"),
            BenchmarkMetric(name="Matrix Dimension", value=float(matrix_n), unit="NxN", description="Double precision matrix size tested")
        ]

        details = f"Executed {iteration} scientific cycles. Average BLAS GEMM: {avg_gflops} GFLOPS, 2D FFT: {round(avg_fft_ms, 1)} ms."

        return BenchmarkResult(
            benchmark_id="scientific",
            display_name=self.display_name,
            duration_secs=round(total_duration, 1),
            score=score,
            metrics=metrics,
            status=status,
            details=details
        )

    def cleanup(self) -> None:
        self._stopped = True
