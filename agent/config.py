"""Centralized configuration for LaptopCheck.
Externalizes all thresholds, limits, durations, and defaults.
Enforces conservative, shop-safe thermal boundaries to protect customer and shop hardware.
"""
from pydantic import BaseModel, Field

class SafetyThresholds(BaseModel):
    """Conservative thermal and system load thresholds."""
    # CPU temperature thresholds in Celsius (conservative for laptop cooling pipes)
    cpu_temp_warning: float = 80.0
    cpu_temp_reduce_load: float = 88.0
    cpu_temp_emergency_stop: float = 94.0
    
    # GPU temperature thresholds in Celsius
    gpu_temp_warning: float = 78.0
    gpu_temp_reduce_load: float = 84.0
    gpu_temp_emergency_stop: float = 89.0
    
    # Battery temperature thresholds (Li-poly safe operational limits)
    battery_temp_warning: float = 40.0
    battery_temp_emergency_stop: float = 48.0

    # System load thresholds
    idle_cpu_warning_pct: float = 30.0
    idle_ram_warning_pct: float = 80.0
    
    # Degradation threshold: sustained performance drop > 20% flags throttling
    degradation_warning_pct: float = 20.0


class TestLevelDurations(BaseModel):
    # Quick / Shop Safe: <= 5 minutes target
    level1_cpu_short_secs: int = 15
    level1_memory_secs: int = 10
    level1_storage_mb: int = 50
    level1_scientific_secs: int = 15
    level1_gpu_secs: int = 5
    
    # Standard: 10-20 minutes target (compressed for snappy agent mode when needed)
    level2_cpu_sustained_secs: int = 60
    level2_memory_secs: int = 30
    level2_storage_mb: int = 250
    level2_scientific_secs: int = 45
    level2_gpu_secs: int = 15
    
    # Extended: deep stability test
    level3_cpu_sustained_secs: int = 180
    level3_memory_secs: int = 60
    level3_storage_mb: int = 500
    level3_scientific_secs: int = 90
    level3_gpu_secs: int = 30


class SystemConfig(BaseModel):
    app_name: str = "LaptopCheck"
    version: str = "1.0.0"
    safety: SafetyThresholds = Field(default_factory=SafetyThresholds)
    durations: TestLevelDurations = Field(default_factory=TestLevelDurations)
    storage_temp_dir: str = "/tmp/laptopcheck_tests"
    enable_simulation_by_default: bool = False


# Global default configuration instance
CONFIG = SystemConfig()
