"""Benchmark Engine for LaptopCheck.
Coordinates CPU, Memory, Storage, GPU, Scientific, and QE benchmarks.
Supports both real execution and high-fidelity simulated runs.
"""
import time
from typing import List, Callable, Optional, Dict, Any
import psutil

from agent.models import (
    BenchmarkResult, BenchmarkMetric, StatusEnum, SafetyLevel,
    SystemHardwareSnapshot
)
from agent.safety.controller import SafetyController
from agent.benchmarks.cpu import CPUBenchmark
from agent.benchmarks.memory import MemoryBenchmark
from agent.benchmarks.storage import StorageBenchmark
from agent.benchmarks.gpu import GPUBenchmark
from agent.benchmarks.scientific import ScientificBenchmark
from agent.benchmarks.qe_plugin import QuantumEspressoPlugin
from agent.config import CONFIG

class BenchmarkEngine:
    """Orchestrator for benchmark suite execution."""

    def __init__(self, safety: SafetyController):
        self.safety = safety
        self.cpu_bench = CPUBenchmark()
        self.mem_bench = MemoryBenchmark()
        self.storage_bench = StorageBenchmark()
        self.gpu_bench = GPUBenchmark()
        self.sci_bench = ScientificBenchmark()
        self.qe_plugin = QuantumEspressoPlugin()

    def run_suite(
        self,
        test_level: str,
        hardware: SystemHardwareSnapshot,
        progress_callback: Optional[Callable[[float, str, Optional[BenchmarkResult]], None]] = None,
        sample_callback: Optional[Callable[[float], None]] = None
    ) -> List[BenchmarkResult]:
        """Runs the benchmark suite matching the requested test level."""
        results: List[BenchmarkResult] = []

        if hardware.is_simulation:
            return self._run_simulated_suite(
                test_level, hardware, progress_callback, sample_callback
            )

        # Durations based on test level
        durations = CONFIG.durations
        if "quick" in test_level.lower():
            cpu_dur = durations.level1_cpu_short_secs
            mem_dur = durations.level1_memory_secs
            sci_dur = durations.level1_scientific_secs
            gpu_dur = durations.level1_gpu_secs
        elif "extended" in test_level.lower():
            cpu_dur = durations.level3_cpu_sustained_secs
            mem_dur = durations.level3_memory_secs
            sci_dur = durations.level3_scientific_secs
            gpu_dur = durations.level3_gpu_secs
        else:  # Standard
            cpu_dur = durations.level2_cpu_sustained_secs
            mem_dur = durations.level2_memory_secs
            sci_dur = durations.level2_scientific_secs
            gpu_dur = durations.level2_gpu_secs

        benchmarks_to_run = [
            ("cpu", self.cpu_bench, cpu_dur, "Benchmarking CPU Multi-Core Performance..."),
            ("memory", self.mem_bench, mem_dur, "Benchmarking RAM Memory Bandwidth..."),
            ("storage", self.storage_bench, 10, "Benchmarking Safe Storage Read/Write..."),
            ("gpu", self.gpu_bench, gpu_dur, "Inspecting GPU Compute Capabilities..."),
            ("scientific", self.sci_bench, sci_dur, "Benchmarking Scientific BLAS & FFT..."),
            ("qe", self.qe_plugin, 0, "Inspecting Quantum ESPRESSO Plugin...")
        ]

        total_steps = len(benchmarks_to_run)
        suite_start = time.time()
        for idx, (b_id, bench, dur, desc) in enumerate(benchmarks_to_run):
            if self.safety.is_stopped():
                break

            base_pct = idx / total_steps
            step_weight = 1.0 / total_steps

            if progress_callback:
                progress_callback(base_pct, desc, None)

            def sub_progress(sub_pct: float, sub_msg: str):
                overall_pct = base_pct + (sub_pct * step_weight)
                # Sample thermals
                cur_temp = None
                temps = psutil.sensors_temperatures()
                if temps:
                    for k in ["coretemp", "k10temp", "cpu_thermal", "acpitz"]:
                        if k in temps and temps[k]:
                            cur_temp = temps[k][0].current
                            break
                freq = psutil.cpu_freq().current if psutil.cpu_freq() else None
                sample = self.safety.evaluate(
                    cpu_temp=cur_temp,
                    cpu_freq=freq,
                    cpu_usage=psutil.cpu_percent(),
                    elapsed_secs=round(time.time() - suite_start, 1)
                )
                if progress_callback:
                    progress_callback(overall_pct, sub_msg, None)

            res = bench.run(dur, self.safety, progress_callback=sub_progress)
            results.append(res)
            
            if progress_callback:
                progress_callback(base_pct + step_weight, f"Completed {bench.display_name}", res)

        return results

    def _run_simulated_suite(
        self,
        test_level: str,
        hardware: SystemHardwareSnapshot,
        progress_callback: Optional[Callable[[float, str, Optional[BenchmarkResult]], None]] = None,
        sample_callback: Optional[Callable[[float], None]] = None
    ) -> List[BenchmarkResult]:
        """Generates realistic simulated benchmark data reflecting simulated profile."""
        profile = hardware.simulation_profile_name or ""
        is_low = "low-end" in profile.lower()
        is_hot = "thermally limited" in profile.lower()
        is_high = "workstation" in profile.lower() or "high-performance" in profile.lower()
        is_storage_warn = "storage-warning" in profile.lower()

        # Step count simulation
        steps = [
            ("cpu", "CPU Multi-Core & Sustained Performance", 4),
            ("memory", "RAM Memory Bandwidth & Integrity", 3),
            ("storage", "Storage Sequential Read/Write", 3),
            ("gpu", "GPU Compute & Graphics Acceleration", 2),
            ("scientific", "Scientific Computing & Numerical BLAS", 4),
            ("qe_plugin", "Quantum ESPRESSO (pw.x) Plugin", 1)
        ]

        total_steps = len(steps)
        results: List[BenchmarkResult] = []

        start_time = time.time()
        for idx, (b_id, name, duration) in enumerate(steps):
            if self.safety.is_stopped():
                break

            base_pct = idx / total_steps
            step_weight = 1.0 / total_steps

            for sec in range(duration):
                if self.safety.is_stopped():
                    break
                time.sleep(0.4)
                elapsed = time.time() - start_time
                sub_pct = (sec + 1) / duration
                overall_pct = base_pct + (sub_pct * step_weight)

                # Simulated thermal sample
                base_cpu_temp = 50.0
                if is_hot:
                    base_cpu_temp = 72.0 + (sec * 4.5)  # Reaches ~90C
                elif is_high:
                    base_cpu_temp = 56.0 + (sec * 1.5)
                elif is_low:
                    base_cpu_temp = 42.0 + (sec * 1.0)
                
                self.safety.evaluate(
                    cpu_temp=base_cpu_temp,
                    gpu_temp=base_cpu_temp - 5.0,
                    battery_temp=33.0,
                    cpu_freq=3800.0 if not is_hot else max(1600.0, 3200.0 - (sec * 300)),
                    cpu_usage=85.0 + (sec * 2),
                    elapsed_secs=elapsed
                )

                if progress_callback:
                    progress_callback(
                        overall_pct,
                        f"[SIMULATION] {name}: {int(sub_pct * 100)}%",
                        None
                    )

            # Generate synthetic results matching profile
            if b_id == "cpu":
                init_p = 14500.0 if is_high else (2200.0 if is_low else 8500.0)
                sust_p = init_p * (0.68 if is_hot else (0.95 if is_high else 0.91))
                deg_pct = round(((init_p - sust_p) / init_p) * 100.0, 1)
                st = StatusEnum.CAUTION if deg_pct >= 20.0 else StatusEnum.PASS
                results.append(BenchmarkResult(
                    benchmark_id="cpu",
                    display_name=name,
                    duration_secs=float(duration),
                    score=round(sust_p / 1500.0, 1),
                    initial_performance=round(init_p / 1000.0, 1),
                    sustained_performance=round(sust_p / 1000.0, 1),
                    degradation_pct=deg_pct,
                    status=st,
                    details=f"Simulated {name}. Degradation: {deg_pct}%.",
                    metrics=[
                        BenchmarkMetric(name="Initial Performance", value=round(init_p / 1000.0, 1), unit="k ops/sec", description="Initial burst"),
                        BenchmarkMetric(name="Sustained Performance", value=round(sust_p / 1000.0, 1), unit="k ops/sec", description="Sustained multi-thread"),
                        BenchmarkMetric(name="Observed Degradation", value=deg_pct, unit="%", description="Sustained load reduction")
                    ]
                ))
            elif b_id == "memory":
                bw = 58.2 if is_high else (9.6 if is_low else 24.5)
                st = StatusEnum.PASS if bw >= 12.0 else StatusEnum.CAUTION
                results.append(BenchmarkResult(
                    benchmark_id="memory",
                    display_name=name,
                    duration_secs=float(duration),
                    score=round(bw * 500.0, 1),
                    status=st,
                    details=f"Simulated Memory Bandwidth: {bw} GB/s.",
                    metrics=[
                        BenchmarkMetric(name="Average Bandwidth", value=bw, unit="GB/s", description="Mean RAM throughput")
                    ]
                ))
            elif b_id == "storage":
                w_spd = 5200.0 if is_high else (85.0 if is_storage_warn else (95.0 if is_low else 1800.0))
                r_spd = 6800.0 if is_high else (210.0 if is_storage_warn else (180.0 if is_low else 2800.0))
                st = StatusEnum.CAUTION if is_storage_warn else StatusEnum.PASS
                results.append(BenchmarkResult(
                    benchmark_id="storage",
                    display_name=name,
                    duration_secs=float(duration),
                    score=round(((w_spd + r_spd) / 2.0) * 2.0, 1),
                    status=st,
                    details=f"Simulated Storage: Read {r_spd} MB/s, Write {w_spd} MB/s.",
                    metrics=[
                        BenchmarkMetric(name="Sequential Read", value=r_spd, unit="MB/s", description="Read throughput"),
                        BenchmarkMetric(name="Sequential Write", value=w_spd, unit="MB/s", description="Write throughput")
                    ]
                ))
            elif b_id == "gpu":
                if is_high:
                    results.append(BenchmarkResult(
                        benchmark_id="gpu",
                        display_name=name,
                        duration_secs=float(duration),
                        score=14200.0,
                        status=StatusEnum.PASS,
                        details="Simulated NVIDIA RTX 4000 Ada Generation dedicated GPU compute verification.",
                        metrics=[
                            BenchmarkMetric(name="GPU Compute Score", value=14200.0, unit="pts", description="Workstation GPU compute throughput")
                        ]
                    ))
                elif is_hot:
                    results.append(BenchmarkResult(
                        benchmark_id="gpu",
                        display_name=name,
                        duration_secs=float(duration),
                        score=6100.0,
                        status=StatusEnum.PASS,
                        details="Simulated NVIDIA RTX 3060 Laptop GPU compute test.",
                        metrics=[
                            BenchmarkMetric(name="GPU Compute Score", value=6100.0, unit="pts", description="Dedicated GPU compute throughput")
                        ]
                    ))
                else:
                    results.append(BenchmarkResult(
                        benchmark_id="gpu",
                        display_name=name,
                        duration_secs=0.0,
                        score=0.0,
                        status=StatusEnum.NOT_AVAILABLE,
                        details="GPU benchmark unavailable on this system: Dedicated GPU compute or CUDA acceleration not detected. Integrated graphics verified for display output.",
                        metrics=[
                            BenchmarkMetric(name="GPU Compute Support", value=0.0, unit="status", description="Dedicated compute not present")
                        ]
                    ))
            elif b_id == "scientific":
                gflops = 142.0 if is_high else (12.0 if is_low else 64.0)
                st = StatusEnum.PASS if gflops >= 20.0 else StatusEnum.CAUTION
                results.append(BenchmarkResult(
                    benchmark_id="scientific",
                    display_name=name,
                    duration_secs=float(duration),
                    score=round(gflops * 150.0, 1),
                    status=st,
                    details=f"Simulated BLAS GEMM: {gflops} GFLOPS.",
                    metrics=[
                        BenchmarkMetric(name="BLAS GEMM Throughput", value=gflops, unit="GFLOPS", description="Matrix double-precision throughput")
                    ]
                ))
            elif b_id == "qe_plugin":
                results.append(BenchmarkResult(
                    benchmark_id="qe_plugin",
                    display_name=name,
                    duration_secs=0.0,
                    score=0.0,
                    status=StatusEnum.NOT_AVAILABLE,
                    details="QE Not Installed on simulated machine (optional plugin).",
                    metrics=[
                        BenchmarkMetric(name="Plugin Status", value=0.0, unit="status", description="pw.x binary not present")
                    ]
                ))

        return results
