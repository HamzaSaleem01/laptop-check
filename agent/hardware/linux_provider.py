"""Linux Hardware Provider for LaptopCheck.
Reads sysfs, /proc, psutil, lscpu, lsblk, and system metrics natively without root requirements.
Tracks strict field-level provenance (source, method, status, confidence, and limitations).
Follows strict safety principles: no destructive actions, graceful fallbacks, no fabricated values.
"""
import os
import re
import platform
import subprocess
import json
import psutil
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime

from agent.hardware.base import HardwareProvider
from agent.models import (
    CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo,
    BatteryHealthCategory, FieldProvenance, ProvenanceStatus, ProvenanceConfidence
)

class LinuxHardwareProvider(HardwareProvider):
    """Native Linux hardware detection with field-level provenance tracking."""

    def __init__(self):
        self.provenance: Dict[str, FieldProvenance] = {}

    def get_provenance_records(self) -> Dict[str, FieldProvenance]:
        return self.provenance

    def _record_prov(
        self,
        key: str,
        value: Any,
        source: str,
        method: str,
        status: ProvenanceStatus = ProvenanceStatus.REPORTED,
        confidence: ProvenanceConfidence = ProvenanceConfidence.HIGH,
        unit: str = "",
        limitations: Optional[List[str]] = None
    ):
        self.provenance[key] = FieldProvenance(
            key=key,
            value=value,
            unit=unit,
            source=source,
            method=method,
            status=status,
            confidence=confidence,
            limitations=limitations or []
        )

    def get_system_model(self) -> Tuple[str, str]:
        mfg = "Unknown"
        model = "Linux Laptop"
        try:
            if os.path.exists("/sys/class/dmi/id/sys_vendor"):
                with open("/sys/class/dmi/id/sys_vendor", "r") as f:
                    val = f.read().strip()
                    if val:
                        mfg = val
                        self._record_prov(
                            "system.manufacturer", mfg,
                            source="linux:/sys/class/dmi/id/sys_vendor",
                            method="dmi_sysfs",
                            status=ProvenanceStatus.REPORTED,
                            confidence=ProvenanceConfidence.HIGH
                        )
            if os.path.exists("/sys/class/dmi/id/product_name"):
                with open("/sys/class/dmi/id/product_name", "r") as f:
                    val = f.read().strip()
                    if val:
                        model = val
                        self._record_prov(
                            "system.model", model,
                            source="linux:/sys/class/dmi/id/product_name",
                            method="dmi_sysfs",
                            status=ProvenanceStatus.REPORTED,
                            confidence=ProvenanceConfidence.HIGH
                        )
        except Exception as e:
            self._record_prov(
                "system.model", model,
                source="linux:/sys/class/dmi/id",
                method="dmi_sysfs",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.UNAVAILABLE,
                limitations=[f"Could not read DMI tables: {e}"]
            )
        return mfg, model

    def get_os_info(self) -> OSInfo:
        os_name = platform.system()
        distro = "Linux"
        kernel_rel = platform.release()
        hostname = platform.node()
        serial = None
        bios_ver = None
        bios_date = None

        try:
            if os.path.exists("/etc/os-release"):
                with open("/etc/os-release", "r") as f:
                    for line in f:
                        if line.startswith("PRETTY_NAME="):
                            distro = line.split("=", 1)[1].strip().strip('"')
                            break
        except Exception:
            pass

        try:
            if os.path.exists("/sys/class/dmi/id/product_serial"):
                with open("/sys/class/dmi/id/product_serial", "r") as f:
                    s = f.read().strip()
                    if s and s.lower() not in ["none", "n/a", "unknown"]:
                        serial = s
                        self._record_prov(
                            "system.serial_number", serial,
                            source="linux:/sys/class/dmi/id/product_serial",
                            method="dmi_sysfs",
                            status=ProvenanceStatus.REPORTED,
                            confidence=ProvenanceConfidence.HIGH,
                            limitations=["Subject to automatic redaction in public reports"]
                        )
            if os.path.exists("/sys/class/dmi/id/bios_version"):
                with open("/sys/class/dmi/id/bios_version", "r") as f:
                    bios_ver = f.read().strip()
            if os.path.exists("/sys/class/dmi/id/bios_date"):
                with open("/sys/class/dmi/id/bios_date", "r") as f:
                    bios_date = f.read().strip()
        except Exception:
            pass

        self._record_prov(
            "os.kernel", kernel_rel,
            source="linux:uname",
            method="kernel_release",
            status=ProvenanceStatus.REPORTED,
            confidence=ProvenanceConfidence.HIGH
        )
        self._record_prov(
            "os.hostname", hostname,
            source="linux:platform.node",
            method="hostname_query",
            status=ProvenanceStatus.REPORTED,
            confidence=ProvenanceConfidence.HIGH,
            limitations=["Redacted by default in exported reports"]
        )

        return OSInfo(
            system=os_name,
            release=distro,
            version=platform.version(),
            architecture=platform.machine(),
            kernel=kernel_rel,
            hostname=hostname,
            serial_number=serial,
            bios_version=bios_ver,
            bios_date=bios_date
        )

    def get_cpu_info(self) -> CPUInfo:
        cpu = CPUInfo()
        cpu.architecture = platform.machine()
        cpu.cores_physical = psutil.cpu_count(logical=False)
        cpu.threads_logical = psutil.cpu_count(logical=True)
        cpu.usage_percent = psutil.cpu_percent(interval=0.05)

        # Frequencies
        freq = psutil.cpu_freq()
        if freq:
            cpu.current_freq_mhz = round(freq.current, 1)
            if freq.max:
                cpu.max_freq_mhz = round(freq.max, 1)
            if freq.min:
                cpu.base_freq_mhz = round(freq.min, 1)

        # Detailed lscpu output parsing
        try:
            out = subprocess.check_output(["lscpu"], stderr=subprocess.DEVNULL, text=True)
            for line in out.splitlines():
                if ":" not in line:
                    continue
                k, v = [x.strip() for x in line.split(":", 1)]
                kl = k.lower()
                if "model name" in kl and cpu.model == "Not available":
                    cpu.model = v
                elif "vendor id" in kl and cpu.manufacturer == "Not available":
                    cpu.manufacturer = "Intel" if "intel" in v.lower() else ("AMD" if "amd" in v.lower() else v)
                elif "stepping" in kl:
                    cpu.stepping = v
                elif "l1d cache" in kl:
                    m = re.search(r"(\d+)\s*(k|m|g)?i?b", v, re.I)
                    if m:
                        val = int(m.group(1))
                        unit = (m.group(2) or "k").lower()
                        cpu.cache_l1d_kb = val if unit == "k" else (val * 1024 if unit == "m" else val)
                elif "l1i cache" in kl:
                    m = re.search(r"(\d+)\s*(k|m|g)?i?b", v, re.I)
                    if m:
                        val = int(m.group(1))
                        unit = (m.group(2) or "k").lower()
                        cpu.cache_l1i_kb = val if unit == "k" else (val * 1024 if unit == "m" else val)
                elif "l2 cache" in kl:
                    m = re.search(r"([\d\.]+)\s*(k|m|g)?i?b", v, re.I)
                    if m:
                        val = float(m.group(1))
                        unit = (m.group(2) or "m").lower()
                        cpu.cache_l2_kb = int(val * 1024 if unit == "m" else (val if unit == "k" else val))
                elif "l3 cache" in kl:
                    m = re.search(r"([\d\.]+)\s*(k|m|g)?i?b", v, re.I)
                    if m:
                        val = float(m.group(1))
                        unit = (m.group(2) or "m").lower()
                        cpu.cache_l3_kb = int(val * 1024 if unit == "m" else (val if unit == "k" else val))
                elif "flags" in kl:
                    flags = v.split()
                    interesting = {"avx", "avx2", "avx512f", "sse4_1", "sse4_2", "fma", "aes", "vmx", "svm", "sha_ni"}
                    cpu.instruction_sets = [flg.upper() for flg in flags if flg.lower() in interesting]
                    cpu.virtualization = "vmx" in flags or "svm" in flags
        except Exception:
            pass

        # Try to parse /proc/cpuinfo if model still missing
        if cpu.model == "Not available" and os.path.exists("/proc/cpuinfo"):
            try:
                with open("/proc/cpuinfo", "r") as f:
                    for line in f:
                        if line.startswith("model name") and cpu.model == "Not available":
                            cpu.model = line.split(":", 1)[1].strip()
                        elif line.startswith("vendor_id") and cpu.manufacturer == "Not available":
                            cpu.manufacturer = line.split(":", 1)[1].strip()
            except Exception:
                pass

        # Detect Hybrid Architecture (P-cores / E-cores)
        try:
            lscpu_e = subprocess.check_output(["lscpu", "-e=CPU,CORE,MAXMHZ"], stderr=subprocess.DEVNULL, text=True)
            lines = [l.strip() for l in lscpu_e.splitlines() if l.strip() and not l.startswith("CPU")]
            core_max_freqs = {}
            for l in lines:
                parts = l.split()
                if len(parts) >= 3:
                    cpu_idx, core_id, max_mhz = parts[0], parts[1], parts[2]
                    try:
                        core_max_freqs.setdefault(core_id, float(max_mhz))
                    except ValueError:
                        pass
            
            # If multiple distinct max freqs exist across physical cores, we have a hybrid topology!
            if len(set(core_max_freqs.values())) > 1:
                highest_freq = max(core_max_freqs.values())
                p_core_count = sum(1 for f in core_max_freqs.values() if f >= highest_freq - 100)
                e_core_count = len(core_max_freqs) - p_core_count
                cpu.p_cores = p_core_count
                cpu.e_cores = e_core_count
                self._record_prov(
                    "cpu.topology.hybrid",
                    f"{p_core_count}P + {e_core_count}E",
                    source="linux:lscpu -e",
                    method="frequency_topology_analysis",
                    status=ProvenanceStatus.MEASURED,
                    confidence=ProvenanceConfidence.HIGH,
                    limitations=[]
                )
        except Exception:
            pass

        # CPU Temperature: prioritize labeled coretemp / k10temp Package sensor
        cpu_temp_found = False
        temps = psutil.sensors_temperatures()
        if temps:
            # 1. Try coretemp (Intel)
            if "coretemp" in temps and temps["coretemp"]:
                for s in temps["coretemp"]:
                    if any(target in s.label.lower() for target in ["package id", "core 0", "temp1"]):
                        cpu.temperature_c = round(s.current, 1)
                        cpu_temp_found = True
                        self._record_prov(
                            "cpu.temperature_c", cpu.temperature_c,
                            source=f"linux:hwmon:coretemp ({s.label})",
                            method="sysfs_hwmon",
                            status=ProvenanceStatus.MEASURED,
                            confidence=ProvenanceConfidence.HIGH,
                            unit="celsius"
                        )
                        break
            # 2. Try k10temp (AMD)
            if not cpu_temp_found and "k10temp" in temps and temps["k10temp"]:
                for s in temps["k10temp"]:
                    if any(target in s.label.lower() for target in ["tdie", "tctl", "temp1"]):
                        cpu.temperature_c = round(s.current, 1)
                        cpu_temp_found = True
                        self._record_prov(
                            "cpu.temperature_c", cpu.temperature_c,
                            source=f"linux:hwmon:k10temp ({s.label})",
                            method="sysfs_hwmon",
                            status=ProvenanceStatus.MEASURED,
                            confidence=ProvenanceConfidence.HIGH,
                            unit="celsius"
                        )
                        break
            # 3. Fallback to other labeled sensors
            if not cpu_temp_found:
                for key in ["cpu_thermal", "soc_thermal"]:
                    if key in temps and temps[key]:
                        s = temps[key][0]
                        cpu.temperature_c = round(s.current, 1)
                        cpu_temp_found = True
                        self._record_prov(
                            "cpu.temperature_c", cpu.temperature_c,
                            source=f"linux:hwmon:{key} ({s.label or 'unlabeled'})",
                            method="sysfs_hwmon",
                            status=ProvenanceStatus.MEASURED,
                            confidence=ProvenanceConfidence.MEDIUM,
                            unit="celsius",
                            limitations=["Unlabeled sensor; inferred as CPU package temperature"]
                        )
                        break

        if not cpu_temp_found:
            self._record_prov(
                "cpu.temperature_c", None,
                source="linux:/sys/class/hwmon",
                method="sysfs_hwmon",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.UNAVAILABLE,
                limitations=["No supported CPU thermal sensor detected in /sys/class/hwmon"]
            )

        # Record CPU provenance
        self._record_prov(
            "cpu.model", cpu.model,
            source="linux:lscpu /proc/cpuinfo",
            method="os_topology",
            status=ProvenanceStatus.REPORTED,
            confidence=ProvenanceConfidence.HIGH
        )
        self._record_prov(
            "cpu.logical_processors", cpu.threads_logical,
            source="linux:/sys/devices/system/cpu/online",
            method="os_topology",
            status=ProvenanceStatus.REPORTED,
            confidence=ProvenanceConfidence.HIGH,
            unit="count"
        )
        self._record_prov(
            "cpu.physical_cores", cpu.cores_physical,
            source="linux:/sys/devices/system/cpu/cpu*/topology/core_id",
            method="os_topology",
            status=ProvenanceStatus.REPORTED,
            confidence=ProvenanceConfidence.HIGH,
            unit="count"
        )

        return cpu

    def get_ram_info(self) -> RAMInfo:
        ram = RAMInfo()
        try:
            vm = psutil.virtual_memory()
            ram.total_gb = round(vm.total / (1024 ** 3), 2)
            ram.available_gb = round(vm.available / (1024 ** 3), 2)
            ram.used_gb = round(vm.used / (1024 ** 3), 2)

            self._record_prov(
                "memory.total_usable_gb", ram.total_gb,
                source="linux:/proc/meminfo:MemTotal",
                method="kernel_sysfs",
                status=ProvenanceStatus.MEASURED,
                confidence=ProvenanceConfidence.HIGH,
                unit="gigabytes",
                limitations=["Usable OS memory; physical memory may be higher due to iGPU/firmware reservation"]
            )

            # Memory Type, Speed, and Channels:
            # On Linux without root/dmidecode, physical SPD/DIMM channels cannot be asserted reliably.
            # We explicitly report them as unavailable rather than fabricating "Dual Channel" or DDR types!
            ram.memory_type = "Not available"
            ram.channels = "Not available"

            self._record_prov(
                "memory.type", "Not available",
                source="linux:dmidecode",
                method="smbios_spd",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.UNAVAILABLE,
                limitations=["Physical memory type (DDR4/DDR5/LPDDR) requires root privileges for dmidecode on Linux."]
            )
            self._record_prov(
                "memory.channels", "Not available",
                source="linux:dmidecode",
                method="smbios_spd",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.UNAVAILABLE,
                limitations=["Memory channel architecture (Single/Dual Channel) cannot be determined without elevated SMBIOS access."]
            )
        except Exception as e:
            self._record_prov(
                "memory.total_usable_gb", 0.0,
                source="linux:/proc/meminfo",
                method="kernel_sysfs",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.UNAVAILABLE,
                limitations=[f"Failed to read /proc/meminfo: {e}"]
            )

        return ram

    def get_gpu_info(self) -> List[GPUInfo]:
        gpus: List[GPUInfo] = []
        try:
            out = subprocess.check_output(["lspci", "-nn"], stderr=subprocess.DEVNULL, text=True)
            gpu_idx = 0
            for line in out.splitlines():
                if any(x in line.lower() for x in ["vga", "3d", "display"]):
                    gpu = GPUInfo()
                    parts = line.split(":", 2)
                    name = parts[-1].strip() if len(parts) >= 3 else line
                    gpu.name = name
                    nl = name.lower()

                    if "nvidia" in nl:
                        gpu.vendor = "NVIDIA"
                        gpu.is_dedicated = True
                        gpu.compute_apis = ["CUDA", "Vulkan", "OpenCL"]
                    elif "amd" in nl or "radeon" in nl:
                        gpu.vendor = "AMD"
                        gpu.is_dedicated = any(k in nl for k in ["discrete", "rx", "xt", "pro"])
                        gpu.compute_apis = ["ROCm (Driver-dependent)", "Vulkan", "OpenCL"]
                    elif "intel" in nl:
                        gpu.vendor = "Intel"
                        gpu.is_dedicated = "arc" in nl and not "graphics" in nl
                        gpu.compute_apis = ["OpenCL", "Vulkan", "VA-API"]
                    else:
                        gpu.vendor = "Integrated / Other"
                        gpu.compute_apis = ["OpenGL / Vulkan"]

                    self._record_prov(
                        f"gpu.{gpu_idx}.name", gpu.name,
                        source="linux:lspci -nn",
                        method="pci_device_enumeration",
                        status=ProvenanceStatus.REPORTED,
                        confidence=ProvenanceConfidence.HIGH
                    )
                    self._record_prov(
                        f"gpu.{gpu_idx}.is_dedicated", gpu.is_dedicated,
                        source="linux:lspci -nn",
                        method="pci_device_heuristic",
                        status=ProvenanceStatus.INFERRED,
                        confidence=ProvenanceConfidence.HIGH if gpu.vendor == "NVIDIA" else ProvenanceConfidence.MEDIUM,
                        limitations=["Inferred from PCI device name and vendor; unified architectures may share memory"]
                    )

                    gpus.append(gpu)
                    gpu_idx += 1
        except Exception:
            pass

        # Query nvidia-smi if NVIDIA discrete GPU exists
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
                        driver_version=parts[4],
                        compute_apis=["CUDA", "Vulkan", "OpenCL"]
                    )
                    self._record_prov(
                        "gpu.nvidia.vram_mb", gpu.vram_mb,
                        source="linux:nvidia-smi",
                        method="proprietary_driver_telemetry",
                        status=ProvenanceStatus.REPORTED,
                        confidence=ProvenanceConfidence.HIGH,
                        unit="megabytes"
                    )
                    gpus = [g for g in gpus if g.vendor != "NVIDIA"]
                    gpus.append(gpu)
        except Exception:
            pass

        if not gpus:
            gpus.append(GPUInfo(name="Standard Display Adapter", vendor="Generic", is_dedicated=False))
            self._record_prov(
                "gpu.0.name", "Standard Display Adapter",
                source="linux:fallback",
                method="generic_fallback",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.LOW
            )

        return gpus

    def get_storage_info(self) -> List[StorageDriveInfo]:
        drives: List[StorageDriveInfo] = []
        try:
            out = subprocess.check_output(
                ["lsblk", "-J", "-b", "-o", "NAME,MODEL,SIZE,ROTA,TYPE,TRAN,MOUNTPOINT"],
                stderr=subprocess.DEVNULL, text=True
            )
            data = json.loads(out)
            devices = data.get("blockdevices", [])
            drive_idx = 0
            for dev in devices:
                if dev.get("type") == "disk" and not dev.get("name", "").startswith("loop"):
                    name = dev.get("name", "")
                    model = dev.get("model") or name
                    size_bytes = int(dev.get("size") or 0)
                    size_gb = round(size_bytes / (1024 ** 3), 1)
                    rota = dev.get("rota", True)
                    tran = (dev.get("tran") or ("nvme" if "nvme" in name else "sata")).lower()

                    media = "NVMe SSD" if tran == "nvme" else ("SATA SSD" if not rota else "HDD")

                    # Check for SMART capability via smartctl
                    smart_status = "Unavailable (smartctl utility not installed)"
                    smart_prov_status = ProvenanceStatus.UNAVAILABLE
                    smart_limits = ["smartctl is not installed on this system; cannot inspect physical SMART wear without smartmontools"]

                    try:
                        which_smart = subprocess.check_output(["which", "smartctl"], stderr=subprocess.DEVNULL, text=True).strip()
                        if which_smart:
                            # Try querying device
                            try:
                                s_out = subprocess.check_output(
                                    ["smartctl", "-H", f"/dev/{name}"],
                                    stderr=subprocess.DEVNULL, text=True
                                )
                                if "PASSED" in s_out:
                                    smart_status = "PASSED (Health OK)"
                                    smart_prov_status = ProvenanceStatus.MEASURED
                                    smart_limits = []
                                elif "FAILED" in s_out:
                                    smart_status = "FAILED (Imminent failure predicted)"
                                    smart_prov_status = ProvenanceStatus.MEASURED
                                    smart_limits = []
                            except subprocess.CalledProcessError as e:
                                if e.returncode in [1, 2]:
                                    smart_status = "Permission Denied (Root required)"
                                    smart_prov_status = ProvenanceStatus.PERMISSION_DENIED
                                    smart_limits = ["Root privileges required to run smartctl on raw block device."]
                    except Exception:
                        pass

                    drive = StorageDriveInfo(
                        device=f"/dev/{name}",
                        model=model,
                        media_type=media,
                        transport=tran,
                        capacity_gb=size_gb,
                        smart_status=smart_status,
                        smart_limitations=smart_limits
                    )

                    # NVMe Drive Temperature from hwmon if available
                    temps = psutil.sensors_temperatures()
                    if temps and "nvme" in temps and temps["nvme"]:
                        drive.temperature_c = round(temps["nvme"][0].current, 1)
                        self._record_prov(
                            f"storage.{drive_idx}.temperature_c", drive.temperature_c,
                            source="linux:/sys/class/hwmon (nvme Composite)",
                            method="sysfs_hwmon",
                            status=ProvenanceStatus.MEASURED,
                            confidence=ProvenanceConfidence.HIGH,
                            unit="celsius"
                        )

                    self._record_prov(
                        f"storage.{drive_idx}.capacity_gb", size_gb,
                        source=f"linux:lsblk:/dev/{name}",
                        method="block_device_query",
                        status=ProvenanceStatus.REPORTED,
                        confidence=ProvenanceConfidence.HIGH,
                        unit="gigabytes"
                    )
                    self._record_prov(
                        f"storage.{drive_idx}.smart_status", smart_status,
                        source=f"linux:smartctl:/dev/{name}",
                        method="smart_query",
                        status=smart_prov_status,
                        confidence=ProvenanceConfidence.HIGH if smart_prov_status == ProvenanceStatus.MEASURED else ProvenanceConfidence.UNAVAILABLE,
                        limitations=smart_limits
                    )

                    drives.append(drive)
                    drive_idx += 1
        except Exception:
            pass

        if not drives:
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
                battery.source_label = os.path.basename(bat_dir)

                full = None
                design = None
                now = None

                # 1. Energy in uWh
                if os.path.exists(f"{bat_dir}/energy_full") and os.path.exists(f"{bat_dir}/energy_full_design"):
                    with open(f"{bat_dir}/energy_full", "r") as f:
                        full = int(f.read().strip()) / 1000.0  # mWh
                    with open(f"{bat_dir}/energy_full_design", "r") as f:
                        design = int(f.read().strip()) / 1000.0
                    if os.path.exists(f"{bat_dir}/energy_now"):
                        with open(f"{bat_dir}/energy_now", "r") as f:
                            now = int(f.read().strip()) / 1000.0

                # 2. Or Charge in uAh
                elif os.path.exists(f"{bat_dir}/charge_full") and os.path.exists(f"{bat_dir}/charge_full_design"):
                    with open(f"{bat_dir}/charge_full", "r") as f:
                        full = int(f.read().strip()) / 1000.0
                    with open(f"{bat_dir}/charge_full_design", "r") as f:
                        design = int(f.read().strip()) / 1000.0
                    if os.path.exists(f"{bat_dir}/charge_now"):
                        with open(f"{bat_dir}/charge_now", "r") as f:
                            now = int(f.read().strip()) / 1000.0

                if full and design and design > 0:
                    battery.full_charge_capacity_mwh = round(full, 1)
                    battery.design_capacity_mwh = round(design, 1)
                    health = min(100.0, (full / design) * 100.0)
                    battery.health_pct = round(health, 1)
                    battery.wear_pct = round(max(0.0, 100.0 - health), 1)

                    if health >= 80.0:
                        battery.category = BatteryHealthCategory.HEALTHY
                    elif health >= 60.0:
                        battery.category = BatteryHealthCategory.REDUCED_CAPACITY
                    else:
                        battery.category = BatteryHealthCategory.SIGNIFICANTLY_REDUCED

                    self._record_prov(
                        "battery.health_pct", battery.health_pct,
                        source=f"linux:{bat_dir}/energy_full,energy_full_design",
                        method="acpi_capacity_ratio",
                        status=ProvenanceStatus.MEASURED,
                        confidence=ProvenanceConfidence.HIGH,
                        unit="percent",
                        limitations=["Capacity estimate is not a remaining-life guarantee; aging cells may lose voltage under peak load"]
                    )
                    self._record_prov(
                        "battery.design_capacity_mwh", battery.design_capacity_mwh,
                        source=f"linux:{bat_dir}/energy_full_design",
                        method="acpi_sysfs",
                        status=ProvenanceStatus.REPORTED,
                        confidence=ProvenanceConfidence.HIGH,
                        unit="mWh"
                    )

                if now is not None:
                    battery.current_capacity_mwh = round(now, 1)

                # Cycle count
                if os.path.exists(f"{bat_dir}/cycle_count"):
                    try:
                        with open(f"{bat_dir}/cycle_count", "r") as f:
                            c = int(f.read().strip())
                            battery.cycle_count = c
                            self._record_prov(
                                "battery.cycle_count", c,
                                source=f"linux:{bat_dir}/cycle_count",
                                method="acpi_sysfs",
                                status=ProvenanceStatus.REPORTED,
                                confidence=ProvenanceConfidence.HIGH,
                                unit="cycles"
                            )
                    except Exception:
                        pass

                # Power draw (power_now in uW)
                if os.path.exists(f"{bat_dir}/power_now"):
                    try:
                        with open(f"{bat_dir}/power_now", "r") as f:
                            p_uw = int(f.read().strip())
                            battery.power_w = round(p_uw / 1000000.0, 2)
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

        # Fallback to psutil (e.g. desktop UPS or virtual battery)
        if not battery.present:
            try:
                ps_bat = psutil.sensors_battery()
                if ps_bat:
                    battery.present = True
                    battery.ac_connected = ps_bat.power_plugged
                    battery.is_charging = ps_bat.power_plugged and ps_bat.percent < 99.0
                    # NOTE: ps_bat.percent is current state of charge, NOT health!
                    battery.category = BatteryHealthCategory.UNABLE_TO_DETERMINE
                    self._record_prov(
                        "battery.health_pct", None,
                        source="linux:psutil.sensors_battery",
                        method="os_snapshot",
                        status=ProvenanceStatus.UNAVAILABLE,
                        confidence=ProvenanceConfidence.UNAVAILABLE,
                        limitations=["psutil exposes instantaneous charge level (%), not battery wear or design capacity"]
                    )
            except Exception:
                pass

        if not battery.present:
            battery.category = BatteryHealthCategory.UNABLE_TO_DETERMINE
            self._record_prov(
                "battery.present", False,
                source="linux:/sys/class/power_supply",
                method="acpi_sysfs",
                status=ProvenanceStatus.REPORTED,
                confidence=ProvenanceConfidence.HIGH,
                limitations=["No physical battery found (desktop/server/VM system)"]
            )

        return battery
