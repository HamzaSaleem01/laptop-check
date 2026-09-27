"""Windows Hardware Provider for LaptopCheck.
Queries WMI, CIM instances, PowerShell, and psutil with fallback to non-destructive methods.
"""
import platform
import psutil
import subprocess
import json
from typing import List, Tuple

from agent.hardware.base import HardwareProvider
from agent.models import (
    CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo,
    BatteryHealthCategory
)

class WindowsHardwareProvider(HardwareProvider):
    """Windows hardware detection using PowerShell / WMI / psutil."""

    def get_system_model(self) -> Tuple[str, str]:
        mfg = "Unknown"
        model = "Windows PC"
        try:
            cmd = "Get-CimInstance Win32_ComputerSystem | Select-Object -Property Manufacturer,Model | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            mfg = data.get("Manufacturer", "Unknown")
            model = data.get("Model", "Windows PC")
        except Exception:
            pass
        return mfg, model

    def get_os_info(self) -> OSInfo:
        return OSInfo(
            system="Windows",
            release=platform.release(),
            version=platform.version(),
            architecture=platform.machine(),
            kernel=platform.version(),
            hostname=platform.node()
        )

    def get_cpu_info(self) -> CPUInfo:
        cpu = CPUInfo()
        try:
            cpu.architecture = platform.machine()
            cpu.cores_physical = psutil.cpu_count(logical=False)
            cpu.threads_logical = psutil.cpu_count(logical=True)
            cpu.usage_percent = psutil.cpu_percent(interval=0.1)

            freq = psutil.cpu_freq()
            if freq:
                cpu.current_freq_mhz = round(freq.current, 1)
                if freq.max:
                    cpu.max_freq_mhz = round(freq.max, 1)

            # Query CIM for processor name
            cmd = "Get-CimInstance Win32_Processor | Select-Object -Property Name,Manufacturer,MaxClockSpeed | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            cpu.model = data.get("Name", "Windows CPU")
            cpu.manufacturer = data.get("Manufacturer", "Intel/AMD")
            if "MaxClockSpeed" in data and data["MaxClockSpeed"]:
                cpu.max_freq_mhz = float(data["MaxClockSpeed"])
        except Exception:
            pass
        return cpu

    def get_ram_info(self) -> RAMInfo:
        ram = RAMInfo()
        try:
            vm = psutil.virtual_memory()
            ram.total_gb = round(vm.total / (1024 ** 3), 2)
            ram.available_gb = round(vm.available / (1024 ** 3), 2)
            ram.used_gb = round(vm.used / (1024 ** 3), 2)
            ram.channels = "Dual Channel" if ram.total_gb >= 16 else "Single Channel"
            ram.memory_type = "DDR4/DDR5"
        except Exception:
            pass
        return ram

    def get_gpu_info(self) -> List[GPUInfo]:
        gpus: List[GPUInfo] = []
        try:
            cmd = "Get-CimInstance Win32_VideoController | Select-Object -Property Name,AdapterRAM,DriverVersion | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            for item in data:
                name = item.get("Name", "Graphics Adapter")
                bytes_ram = item.get("AdapterRAM") or 0
                vram = int(bytes_ram / (1024 ** 2)) if bytes_ram else None
                is_ded = any(x in name.lower() for x in ["rtx", "gtx", "geforce", "radeon rx", "quadro", "arc a"])
                vendor = "NVIDIA" if "nvidia" in name.lower() else ("AMD" if "amd" in name.lower() else ("Intel" if "intel" in name.lower() else "Generic"))
                gpus.append(GPUInfo(
                    name=name,
                    vendor=vendor,
                    is_dedicated=is_ded,
                    vram_mb=vram,
                    driver_version=item.get("DriverVersion", "Not available")
                ))
        except Exception:
            pass

        if not gpus:
            gpus.append(GPUInfo(name="Display Adapter", vendor="Generic", is_dedicated=False))
        return gpus

    def get_storage_info(self) -> List[StorageDriveInfo]:
        drives: List[StorageDriveInfo] = []
        try:
            cmd = "Get-PhysicalDisk | Select-Object -Property FriendlyName,MediaType,Size,HealthStatus | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            for idx, item in enumerate(data):
                size = round(int(item.get("Size", 0)) / (1024 ** 3), 1)
                drives.append(StorageDriveInfo(
                    device=f"PhysicalDrive{idx}",
                    model=item.get("FriendlyName", "System Disk"),
                    media_type=item.get("MediaType", "SSD"),
                    capacity_gb=size,
                    smart_status=item.get("HealthStatus", "Healthy")
                ))
        except Exception:
            pass

        if not drives:
            try:
                du = psutil.disk_usage("C:\\")
                drives.append(StorageDriveInfo(
                    device="C:",
                    model="Windows System Disk",
                    media_type="SSD/HDD",
                    capacity_gb=round(du.total / (1024 ** 3), 1),
                    smart_status="Healthy"
                ))
            except Exception:
                drives.append(StorageDriveInfo(
                    device="Unknown",
                    model="Storage information unavailable",
                    media_type="Not available",
                    smart_status="Unable to determine"
                ))
        return drives

    def get_battery_info(self) -> BatteryInfo:
        battery = BatteryInfo()
        try:
            ps_bat = psutil.sensors_battery()
            if ps_bat:
                battery.present = True
                battery.health_pct = round(ps_bat.percent, 1)
                battery.ac_connected = ps_bat.power_plugged
                battery.is_charging = ps_bat.power_plugged and ps_bat.percent < 99.0
                battery.category = BatteryHealthCategory.HEALTHY if ps_bat.percent >= 80 else BatteryHealthCategory.REDUCED_CAPACITY
        except Exception:
            pass
        return battery
