"""Base Benchmark Class.
Defines mandatory lifecycle hooks: prepare, run, monitor, stop, cleanup, analyze.
"""
from abc import ABC, abstractmethod
from typing import Optional, Callable
from agent.models import BenchmarkResult
from agent.safety.controller import SafetyController

class BaseBenchmark(ABC):
    """Abstract interface for all diagnostic benchmarks."""

    def __init__(self, name: str, display_name: str):
        self.name = name
        self.display_name = display_name
        self._stopped = False

    @abstractmethod
    def prepare(self) -> None:
        """Pre-test resource setup, temporary buffers, or warm-up."""
        pass

    @abstractmethod
    def run(
        self,
        duration_secs: int,
        safety: SafetyController,
        progress_callback: Optional[Callable[[float, str], None]] = None
    ) -> BenchmarkResult:
        """Executes the benchmark with progress reporting and safety monitoring."""
        pass

    def stop(self) -> None:
        """Signals benchmark loop to stop safely."""
        self._stopped = True

    @abstractmethod
    def cleanup(self) -> None:
        """Guaranteed cleanup of temporary files or memory buffers."""
        pass
