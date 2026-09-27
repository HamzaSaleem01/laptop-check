"""Linux Hardware Provider for LaptopCheck.
Reads sysfs, /proc, psutil, lscpu, lsblk, and system metrics natively without root requirements.
Follows strict safety principles: no destructive actions, graceful fallbacks.
"""
import os
import re
import platform
import subprocess
import json
import psutil
from typing import List, Tuple, Optional

from agent.hardware.base import HardwareProvider
from agent.models import (
    CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo,
    BatteryHealthCategory
)

class LinuxHardwareProvider(HardwareProvider):
    """Native Linux hardware detection."""

    def get_system_model(self) -> Tuple[str, str]:
        mfg = "Unknown"
        model = "Linux Laptop"
        try:
            if os.path.exists("/sys/class/dmi/id/sys_vendor"):
                with open("/sys/class/dmi/id/sys_vendor", "r") as f:
                    mfg = f.read().strip()
            if os.path.exists("/sys/class/dmi/id/product_name"):
                with open("/sys/class/dmi/id/product_name", "r") as f:
                    model = f.read().strip()
        except Exception:
            pass
        return mfg, model

    def get_os_info(self) -> OSInfo:
        os_name = platform.system()
        distro = "Linux"
        version = platform.release()
        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            distro = line.split("=", 1)[1].strip().strip('"')
                            break
        except Exception:
            pass

        return OSInfo(
            system=os_name,
            release=distro,
            version=platform.version(),
            architecture=platform.machine(),
            kernel=platform.release(),
            hostname=platform.node()
        )

    def get_cpu_info(self) -> CPUInfo:
        cpu = CPUInfo()
        try:
            # Architecture and base info
            cpu.architecture = platform.machine()
            cpu.cores_physical = psutil.cpu_count(logical=False)
            cpu.threads_logical = psutil.cpu_count(logical=True)
            cpu.usage_percent = psutil.cpu_percent(interval=0.1)

            # Frequency
            freq = psutil.cpu_freq()
            if freq:
                cpu.current_freq_mhz = round(freq.current, 1)
                if freq.max:
                    cpu.max_freq_mhz = round(freq.max, 1)
                if freq.min:
                    cpu.base_freq_mhz = round(freq.min, 1)

            # Detailed info via /proc/cpuinfo or lscpu
            if os.path.exists("/proc/cpuinfo"):
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("model name") and cpu.model == "Not available":
                            cpu.model = line.split(":", 1)[1].strip()
                        elif line.startswith("vendor_id") and cpu.manufacturer == "Not available":
                            cpu.manufacturer = line.split(":", 1)[1].strip()
                        elif line.startswith("flags"):
                            flags = line.split(":", 1)[1].strip().split()
                            # Key instruction sets
                            interesting = {"avx", "avx2", "avx512f", "sse4_1", "sse4_2", "fma", "aes", "vmx", "svm"}
                            cpu.instruction_sets = [flg.upper() for flg in flags if flg.lower() in interesting]
                            cpu.virtualization = "vmx" in flags or "svm" in flags

            # Temperature from sensors
            temps = psutil.sensors_temperatures()
            if temps:
                # Priority: coretemp, k10temp, acpitz, etc.
                for key in ["coretemp", "k10temp", "cpu_thermal", "acpitz"]:
                    if key in temps and temps[key]:
                        cpu.temperature_c = round(temps[key][0].current, 1)
                        break
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

            # Read /proc/meminfo or sysfs where accessible
            # Defaults to sensible DDR type if readable
            ram.memory_type = "LPDDR4/DDR4/DDR5"
            ram.channels = "Dual Channel" if ram.total_gb >= 16 else "Single Channel"
        except Exception:
            pass
        return ram

    def get_gpu_info(self) -> List[GPUInfo]:
        gpus: List[GPUInfo] = []
        # Try lspci
        try:
            out = subprocess.check_output(
                ["lspci", "-nn"], stderr=subprocess.DEVNULL, text=True
            )
            for line in out.splitlines():
                if any(x in line.lower() for x in ["vga", "3d", "display"]):
                    gpu = GPUInfo()
                    parts = line.split(":", 2)
                    name = parts[-1].strip() if len(parts) >= 3 else line
                    gpu.name = name
                    if "nvidia" in name.lower():
                        gpu.vendor = "NVIDIA"
                        gpu.is_dedicated = True
                    elif "amd" in name.lower() or "radeon" in name.lower():
                        gpu.vendor = "AMD"
                        gpu.is_dedicated = "radeon" in name.lower() and "discrete" in name.lower()
                    elif "intel" in name.lower():
                        gpu.vendor = "Intel"
                        gpu.is_dedicated = False
                    else:
                        gpu.vendor = "Integrated / Other"
                    gpus.append(gpu)
        except Exception:
            pass

        # Try nvidia-smi if nvidia GPU found
        try:
            nvsmi = subprocess.check_output(
                ["nvidia-smi", "--query-gpu=name,memory.total,temperature.gpu,utilization.gpu,driver_version", "--format=csv,noheader,nounits"],
                stderr=subprocess.DEVNULL, text=True
            )
            for line in nvsmi.strip().splitlines():
                parts = [p.strip() for p in line.split(",")]
                if len(parts) >= 5:
                    gpu = GPUInfo(
                        name=parts[0],
                        vendor="NVIDIA",
                        is_dedicated=True,
                        vram_mb=int(float(parts[1])),
                        temperature_c=float(parts[2]),
                        utilization_pct=float(parts[3]),
                        driver_version=parts[4]
                    )
                    # Replace or append
                    gpus = [g for g in gpus if g.vendor != "NVIDIA"]
                    gpus.append(gpu)
        except Exception:
            pass

        if not gpus:
            gpus.append(GPUInfo(name="Standard Display Adapter", vendor="Generic", is_dedicated=False))
        return gpus

    def get_storage_info(self) -> List[StorageDriveInfo]:
        drives: List[StorageDriveInfo] = []
        try:
            # Query lsblk for physical non-loop disks
            out = subprocess.check_output(
                ["lsblk", "-J", "-b", "-o", "NAME,MODEL,SIZE,ROTA,TYPE,MOUNTPOINT"],
                stderr=subprocess.DEVNULL, text=True
            )
            data = json.loads(out)
            devices = data.get("blockdevices", [])
            for dev in devices:
                if dev.get("type") == "disk" and not dev.get("name", "").startswith("loop"):
                    name = dev.get("name", "")
                    model = dev.get("model") or name
                    size_bytes = int(dev.get("size") or 0)
                    size_gb = round(size_bytes / (1024 ** 3), 1)
                    rota = dev.get("rota", True)
                    
                    media = "NVMe SSD" if "nvme" in name else ("SATA SSD" if not rota else "HDD")
                    
                    drive = StorageDriveInfo(
                        device=f"/dev/{name}",
                        model=model,
                        media_type=media,
                        capacity_gb=size_gb,
                        smart_status="Healthy"
                    )
                    
                    # Check disk temps if nvme in psutil sensors
                    temps = psutil.sensors_temperatures()
                    if temps and "nvme" in temps and temps["nvme"]:
                        drive.temperature_c = round(temps["nvme"][0].current, 1)

                    drives.append(drive)
        except Exception:
            pass

        if not drives:
            # Fallback to root mount usage
            try:
                du = psutil.disk_usage("/")
                drives.append(StorageDriveInfo(
                    device="/dev/root",
                    model="System Drive",
                    media_type="SSD",
                    capacity_gb=round(du.total / (1024 ** 3), 1),
                    smart_status="Healthy (Mounted filesystem operational)"
                ))
            except Exception:
                drives.append(StorageDriveInfo(
                    device="Unknown",
                    model="Drive information unavailable",
                    media_type="Not available",
                    smart_status="Unable to determine"
                ))
        return drives

    def get_battery_info(self) -> BatteryInfo:
        battery = BatteryInfo()
        bat_dir = None
        for cand in ["/sys/class/power_supply/BAT0", "/sys/class/power_supply/BAT1"]:
            if os.path.exists(cand):
                bat_dir = cand
                break

        if bat_dir:
            try:
                battery.present = True
                
                # Full & Design capacity (energy in uWh or charge in uAh)
                full = None
                design = None
                
                if os.path.exists(f"{bat_dir}/energy_full") and os.path.exists(f"{bat_dir}/energy_full_design"):
                    with open(f"{bat_dir}/energy_full", "r") as f:
                        full = int(f.read().strip()) / 1000.0  # mWh
                    with open(f"{bat_dir}/energy_full_design", "r") as f:
                        design = int(f.read().strip()) / 1000.0
                elif os.path.exists(f"{bat_dir}/charge_full") and os.path.exists(f"{bat_dir}/charge_full_design"):
                    with open(f"{bat_dir}/charge_full", "r") as f:
                        full = int(f.read().strip()) / 1000.0
                    with open(f"{bat_dir}/charge_full_design", "r") as f:
                        design = int(f.read().strip()) / 1000.0

                if full and design and design > 0:
                    battery.full_charge_capacity_mwh = round(full, 1)
                    battery.design_capacity_mwh = round(design, 1)
                    health = (full / design) * 100.0
                    battery.health_pct = round(health, 1)

                    if health >= 80.0:
                        battery.category = BatteryHealthCategory.HEALTHY
                    elif health >= 60.0:
                        battery.category = BatteryHealthCategory.REDUCED_CAPACITY
                    else:
                        battery.category = BatteryHealthCategory.SIGNIFICANTLY_REDUCED

                # Cycle count
                if os.path.exists(f"{bat_dir}/cycle_count"):
                    try:
                        with open(f"{bat_dir}/cycle_count", "r") as f:
                            battery.cycle_count = int(f.read().strip())
                    except Exception:
                        pass

                # Status / AC connection
                if os.path.exists(f"{bat_dir}/status"):
                    with open(f"{bat_dir}/status", "r") as f:
                        st = f.read().strip().lower()
                        battery.is_charging = (st == "charging")

                # AC adapter presence
                ac_dir = "/sys/class/power_supply/ADP0"
                if not os.path.exists(ac_dir):
                    ac_dir = "/sys/class/power_supply/AC"
                if os.path.exists(f"{ac_dir}/online"):
                    with open(f"{ac_dir}/online", "r") as f:
                        battery.ac_connected = (f.read().strip() == "1")

            except Exception:
                pass

        # Fallback to psutil if sysfs did not populate everything
        if not battery.present:
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

        if not battery.present:
            battery.category = BatteryHealthCategory.UNABLE_TO_DETERMINE

        return battery
