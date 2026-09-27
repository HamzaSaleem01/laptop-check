"""Hardware Manager for LaptopCheck.
Detects platform and returns actual hardware snapshot or simulated profile.
"""
import platform
from typing import Dict, Any, List

from agent.hardware.base import HardwareProvider
from agent.hardware.linux_provider import LinuxHardwareProvider
from agent.hardware.windows_provider import WindowsHardwareProvider
from agent.hardware.simulated_provider import SimulatedHardwareProvider, SIMULATED_PRESETS
from agent.models import SystemHardwareSnapshot

def get_native_provider() -> HardwareProvider:
    """Returns the native hardware provider for the current operating system."""
    sys_name = platform.system().lower()
    if sys_name == "windows":
        return WindowsHardwareProvider()
    else:
        # Linux and default fallback
        return LinuxHardwareProvider()

def get_hardware_snapshot(simulate: bool = False, preset: str = "mid_range") -> SystemHardwareSnapshot:
    """Collects system hardware snapshot safely."""
    if simulate:
        provider = SimulatedHardwareProvider(preset_key=preset)
        return provider.get_full_snapshot()
    else:
        provider = get_native_provider()
        return provider.get_full_snapshot()

def list_simulation_presets() -> List[Dict[str, str]]:
    """Lists available simulation laptop profiles."""
    return [
        {"id": key, "label": val["label"], "description": f"{val['mfg']} {val['model']} - {val['cpu'].model}"}
        for key, val in SIMULATED_PRESETS.items()
    ]
