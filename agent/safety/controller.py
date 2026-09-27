"""Safety Controller for LaptopCheck.
Monitors thermals, frequencies, utilization, and enforces safety boundaries.
Prevents damaging shop laptops under test.
"""
import time
import threading
from typing import Optional, Callable
from agent.config import CONFIG, SafetyThresholds
from agent.models import SafetyLevel, ThermalSample

class SafetyController:
    """Active safety guardian during diagnostic tests."""

    def __init__(self, thresholds: Optional[SafetyThresholds] = None):
        self.thresholds = thresholds or CONFIG.safety
        self._user_stop_requested = threading.Event()
        self._paused = threading.Event()
        self._current_level = SafetyLevel.NORMAL
        self.history: list[ThermalSample] = []
        self._lock = threading.Lock()

    def request_stop(self, reason: str = "User requested test stop"):
        """Instantly requests the benchmark engine to abort."""
        self._user_stop_requested.set()
        with self._lock:
            self._current_level = SafetyLevel.STOP

    def is_stopped(self) -> bool:
        return self._user_stop_requested.is_set()

    def set_pause(self, paused: bool):
        if paused:
            self._paused.set()
            with self._lock:
                self._current_level = SafetyLevel.PAUSE
        else:
            self._paused.clear()
            with self._lock:
                self._current_level = SafetyLevel.NORMAL

    def is_paused(self) -> bool:
        return self._paused.is_set()

    def get_current_level(self) -> SafetyLevel:
        with self._lock:
            return self._current_level

    def evaluate(self, cpu_temp: Optional[float], gpu_temp: Optional[float] = None,
                 battery_temp: Optional[float] = None, cpu_freq: Optional[float] = None,
                 cpu_usage: Optional[float] = None, elapsed_secs: float = 0.0) -> ThermalSample:
        """Evaluates sensor readings against safety limits and returns a sample."""
        level = SafetyLevel.NORMAL

        if self._user_stop_requested.is_set():
            level = SafetyLevel.STOP
        elif self._paused.is_set():
            level = SafetyLevel.PAUSE
        else:
            # Check Emergency Thresholds
            if cpu_temp and cpu_temp >= self.thresholds.cpu_temp_emergency_stop:
                level = SafetyLevel.STOP
                self._user_stop_requested.set()
            elif gpu_temp and gpu_temp >= self.thresholds.gpu_temp_emergency_stop:
                level = SafetyLevel.STOP
                self._user_stop_requested.set()
            elif battery_temp and battery_temp >= self.thresholds.battery_temp_emergency_stop:
                level = SafetyLevel.STOP
                self._user_stop_requested.set()
            # Check Reduce Load Thresholds
            elif cpu_temp and cpu_temp >= self.thresholds.cpu_temp_reduce_load:
                level = SafetyLevel.REDUCE_LOAD
            elif gpu_temp and gpu_temp >= self.thresholds.gpu_temp_reduce_load:
                level = SafetyLevel.REDUCE_LOAD
            # Check Warning Thresholds
            elif cpu_temp and cpu_temp >= self.thresholds.cpu_temp_warning:
                level = SafetyLevel.WARNING
            elif gpu_temp and gpu_temp >= self.thresholds.gpu_temp_warning:
                level = SafetyLevel.WARNING
            elif battery_temp and battery_temp >= self.thresholds.battery_temp_warning:
                level = SafetyLevel.WARNING

        with self._lock:
            self._current_level = level

        sample = ThermalSample(
            timestamp=time.time(),
            elapsed_secs=round(elapsed_secs, 1),
            cpu_temp_c=cpu_temp,
            gpu_temp_c=gpu_temp,
            battery_temp_c=battery_temp,
            cpu_freq_mhz=cpu_freq,
            cpu_usage_pct=cpu_usage,
            safety_level=level
        )

        with self._lock:
            self.history.append(sample)

        return sample

    def reset(self):
        """Resets safety controller state for a fresh test run."""
        self._user_stop_requested.clear()
        self._paused.clear()
        with self._lock:
            self._current_level = SafetyLevel.NORMAL
            self.history.clear()
