"""Pre-flight Diagnostic Inspector for LaptopCheck.
Assesses system readiness before benchmarks begin:
- Background CPU and RAM activity
- AC Power vs Battery operational status
- High-consumption background processes (observational only, never terminates processes)
"""
import psutil
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class BackgroundProcessInfo(BaseModel):
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float

class PreflightCheckResult(BaseModel):
    is_ac_connected: Optional[bool] = None
    idle_cpu_percent: float
    idle_ram_percent: float
    warnings: List[str] = Field(default_factory=list)
    top_processes: List[BackgroundProcessInfo] = Field(default_factory=list)

def run_preflight_check() -> PreflightCheckResult:
    """Performs non-invasive pre-flight inspection."""
    warnings: List[str] = []

    # 1. Measure baseline idle CPU utilization over 0.5s interval
    cpu_pct = psutil.cpu_percent(interval=0.5)
    vm = psutil.virtual_memory()
    ram_pct = vm.percent

    if cpu_pct > 30.0:
        warnings.append(
            f"Elevated baseline background CPU usage ({cpu_pct}%). Benchmark accuracy may be affected by active background processes."
        )

    if ram_pct > 80.0:
        warnings.append(
            f"High system memory utilization ({ram_pct}%). Benchmarks will dynamically restrict buffer sizes to preserve system responsiveness."
        )

    # 2. Check AC power connection status
    is_ac = None
    try:
        bat = psutil.sensors_battery()
        if bat is not None:
            is_ac = bat.power_plugged
            if not is_ac:
                warnings.append(
                    "Laptop is currently running on battery power. For representative peak performance results and to prevent OEM power-budget throttling, connect the laptop to AC power."
                )
    except Exception:
        pass

    # 3. Observational inspection of top background processes
    top_procs: List[BackgroundProcessInfo] = []
    try:
        procs = []
        for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                info = p.info
                if info['cpu_percent'] and info['cpu_percent'] > 5.0:
                    procs.append(info)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        # Sort by CPU usage
        procs.sort(key=lambda x: x.get('cpu_percent', 0.0), reverse=True)
        top_procs = [
            BackgroundProcessInfo(
                pid=p['pid'],
                name=p['name'] or "Unknown",
                cpu_percent=round(p.get('cpu_percent', 0.0), 1),
                memory_percent=round(p.get('memory_percent', 0.0), 1)
            )
            for p in procs[:5]
        ]
    except Exception:
        pass

    return PreflightCheckResult(
        is_ac_connected=is_ac,
        idle_cpu_percent=round(cpu_pct, 1),
        idle_ram_percent=round(ram_pct, 1),
        warnings=warnings,
        top_processes=top_procs
    )
