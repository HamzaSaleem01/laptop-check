"""Windows Hardware Provider for LaptopCheck.
Queries WMI, CIM instances, PowerShell, and psutil with fallback to non-destructive methods.
Tracks field-level provenance with explicit status and limitations.
"""
import platform
import psutil
import subprocess
import json
from typing import List, Tuple, Dict, Any, Optional

from agent.hardware.base import HardwareProvider
from agent.models import (
    CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo,
    BatteryHealthCategory, FieldProvenance, ProvenanceStatus, ProvenanceConfidence
)

class WindowsHardwareProvider(HardwareProvider):
    """Windows hardware detection using PowerShell / CIM / psutil with provenance."""

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
        model = "Windows PC"
        try:
            cmd = "Get-CimInstance Win32_ComputerSystem | Select-Object -Property Manufacturer,Model | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            mfg = data.get("Manufacturer", "Unknown")
            model = data.get("Model", "Windows PC")
            self._record_prov(
                "system.manufacturer", mfg,
                source="windows:Win32_ComputerSystem",
                method="cim_wmi",
                status=ProvenanceStatus.REPORTED,
                confidence=ProvenanceConfidence.HIGH,
                limitations=["Reported by motherboard firmware SMBIOS"]
            )
            self._record_prov(
                "system.model", model,
                source="windows:Win32_ComputerSystem",
                method="cim_wmi",
                status=ProvenanceStatus.REPORTED,
                confidence=ProvenanceConfidence.HIGH,
                limitations=["Reported by motherboard firmware SMBIOS"]
            )
        except Exception as e:
            self._record_prov(
                "system.model", model,
                source="windows:Win32_ComputerSystem",
                method="cim_wmi",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.UNAVAILABLE,
                limitations=[f"PowerShell CIM query failed: {e}"]
            )
        return mfg, model

    def get_os_info(self) -> OSInfo:
        serial = None
        bios_ver = None
        try:
            cmd = "Get-CimInstance Win32_BIOS | Select-Object -Property SerialNumber,SMBIOSBIOSVersion | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            serial = data.get("SerialNumber")
            bios_ver = data.get("SMBIOSBIOSVersion")
            if serial:
                self._record_prov(
                    "system.serial_number", serial,
                    source="windows:Win32_BIOS",
                    method="cim_wmi",
                    status=ProvenanceStatus.REPORTED,
                    confidence=ProvenanceConfidence.HIGH,
                    limitations=["Subject to automatic redaction in public reports"]
                )
        except Exception:
            pass

        self._record_prov(
            "os.hostname", platform.node(),
            source="windows:platform.node",
            method="os_query",
            status=ProvenanceStatus.REPORTED,
            confidence=ProvenanceConfidence.HIGH,
            limitations=["Redacted by default in exported reports"]
        )

        return OSInfo(
            system="Windows",
            release=platform.release(),
            version=platform.version(),
            architecture=platform.machine(),
            kernel=platform.version(),
            hostname=platform.node(),
            serial_number=serial,
            bios_version=bios_ver
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

            # Query CIM for processor details
            cmd = "Get-CimInstance Win32_Processor | Select-Object -Property Name,Manufacturer,MaxClockSpeed,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            if isinstance(data, list) and len(data) > 0:
                data = data[0]
            cpu.model = data.get("Name", "Windows CPU")
            cpu.manufacturer = data.get("Manufacturer", "Intel/AMD")
            if "MaxClockSpeed" in data and data["MaxClockSpeed"]:
                cpu.max_freq_mhz = float(data["MaxClockSpeed"])

            self._record_prov(
                "cpu.model", cpu.model,
                source="windows:Win32_Processor",
                method="cim_wmi",
                status=ProvenanceStatus.REPORTED,
                confidence=ProvenanceConfidence.HIGH,
                limitations=["Reported by SMBIOS table"]
            )
            self._record_prov(
                "cpu.logical_processors", cpu.threads_logical,
                source="windows:Win32_Processor",
                method="cim_wmi",
                status=ProvenanceStatus.REPORTED,
                confidence=ProvenanceConfidence.HIGH,
                unit="count"
            )
            self._record_prov(
                "cpu.physical_cores", cpu.cores_physical,
                source="windows:Win32_Processor",
                method="cim_wmi",
                status=ProvenanceStatus.REPORTED,
                confidence=ProvenanceConfidence.HIGH,
                unit="count"
            )
        except Exception as e:
            self._record_prov(
                "cpu.model", cpu.model,
                source="windows:Win32_Processor",
                method="cim_wmi",
                status=ProvenanceStatus.UNAVAILABLE,
                confidence=ProvenanceConfidence.UNAVAILABLE,
                limitations=[f"CIM query failed: {e}"]
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
                source="windows:GlobalMemoryStatusEx",
                method="win32_api",
                status=ProvenanceStatus.MEASURED,
                confidence=ProvenanceConfidence.HIGH,
                unit="gigabytes"
            )

            # Query CIM for physical memory sticks (DIMM/channel details)
            try:
                cmd = "Get-CimInstance Win32_PhysicalMemory | Select-Object -Property Capacity,Speed,MemoryType,SMBIOSMemoryType,FormFactor | ConvertTo-Json"
                out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
                mem_data = json.loads(out)
                if isinstance(mem_data, dict):
                    mem_data = [mem_data]
                if mem_data:
                    ram.modules_count = len(mem_data)
                    ram.slots_used = len(mem_data)
                    first_speed = mem_data[0].get("Speed")
                    if first_speed:
                        ram.speed_mhz = int(first_speed)
                    
                    if len(mem_data) >= 2:
                        ram.channels = "Dual Channel"
                    elif len(mem_data) == 1:
                        ram.channels = "Single Channel"
                    
                    self._record_prov(
                        "memory.channels", ram.channels,
                        source="windows:Win32_PhysicalMemory",
                        method="smbios_cim",
                        status=ProvenanceStatus.REPORTED,
                        confidence=ProvenanceConfidence.HIGH
                    )
            except Exception:
                ram.channels = "Not available"
                ram.memory_type = "Not available"
                self._record_prov(
                    "memory.channels", "Not available",
                    source="windows:Win32_PhysicalMemory",
                    method="smbios_cim",
                    status=ProvenanceStatus.UNAVAILABLE,
                    confidence=ProvenanceConfidence.UNAVAILABLE,
                    limitations=["Physical memory module details unavailable via standard user permissions"]
                )
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
            for idx, item in enumerate(data):
                name = item.get("Name", "Graphics Adapter")
                bytes_ram = item.get("AdapterRAM") or 0
                vram = int(bytes_ram / (1024 ** 2)) if bytes_ram and bytes_ram > 0 else None
                is_ded = any(x in name.lower() for x in ["rtx", "gtx", "geforce", "radeon rx", "quadro", "arc a"])
                vendor = "NVIDIA" if "nvidia" in name.lower() else ("AMD" if "amd" in name.lower() else ("Intel" if "intel" in name.lower() else "Generic"))

                compute_apis = []
                if vendor == "NVIDIA":
                    compute_apis = ["CUDA", "DirectCompute", "Vulkan", "OpenCL"]
                elif vendor == "AMD":
                    compute_apis = ["DirectCompute", "Vulkan", "OpenCL"]
                else:
                    compute_apis = ["DirectCompute", "Vulkan", "OpenCL"]

                gpu = GPUInfo(
                    name=name,
                    vendor=vendor,
                    is_dedicated=is_ded,
                    vram_mb=vram,
                    driver_version=item.get("DriverVersion", "Not available"),
                    compute_apis=compute_apis
                )
                self._record_prov(
                    f"gpu.{idx}.name", name,
                    source="windows:Win32_VideoController",
                    method="cim_wmi",
                    status=ProvenanceStatus.REPORTED,
                    confidence=ProvenanceConfidence.HIGH
                )
                gpus.append(gpu)
        except Exception:
            pass

        if not gpus:
            gpus.append(GPUInfo(name="Display Adapter", vendor="Generic", is_dedicated=False))
        return gpus

    def get_storage_info(self) -> List[StorageDriveInfo]:
        drives: List[StorageDriveInfo] = []
        try:
            cmd = "Get-PhysicalDisk | Select-Object -Property FriendlyName,MediaType,BusType,Size,HealthStatus | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out)
            if isinstance(data, dict):
                data = [data]
            for idx, item in enumerate(data):
                size = round(int(item.get("Size", 0)) / (1024 ** 3), 1)
                bus_type = str(item.get("BusType", "")).lower()
                tran = "nvme" if "nvme" in bus_type else ("sata" if "sata" in bus_type else bus_type)
                media = item.get("MediaType", "SSD")
                if "nvme" in tran and media == "SSD":
                    media = "NVMe SSD"

                health_status = item.get("HealthStatus", "Healthy")
                smart_status = f"{health_status} (OS Storage Service)"

                drive = StorageDriveInfo(
                    device=f"PhysicalDrive{idx}",
                    model=item.get("FriendlyName", "System Disk"),
                    media_type=media,
                    transport=tran,
                    capacity_gb=size,
                    smart_status=smart_status
                )
                self._record_prov(
                    f"storage.{idx}.health_status", health_status,
                    source="windows:Get-PhysicalDisk",
                    method="storage_management_api",
                    status=ProvenanceStatus.REPORTED,
                    confidence=ProvenanceConfidence.HIGH,
                    limitations=["Windows Storage Service health status; raw vendor SMART attributes require vendor utility"]
                )
                drives.append(drive)
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
                    smart_status="Operational"
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
            # Query CIM for battery design and full charge capacity
            cmd = "Get-CimInstance -Namespace root/WMI -ClassName BatteryStaticData -ErrorAction SilentlyContinue | Select-Object -Property DesignedCapacity | ConvertTo-Json"
            out = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd], text=True, stderr=subprocess.DEVNULL)
            data = json.loads(out) if out.strip() else {}
            if isinstance(data, list) and data:
                data = data[0]
            design_cap = data.get("DesignedCapacity")

            cmd2 = "Get-CimInstance -Namespace root/WMI -ClassName BatteryFullChargedCapacity -ErrorAction SilentlyContinue | Select-Object -Property FullChargedCapacity | ConvertTo-Json"
            out2 = subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd2], text=True, stderr=subprocess.DEVNULL)
            data2 = json.loads(out2) if out2.strip() else {}
            if isinstance(data2, list) and data2:
                data2 = data2[0]
            full_cap = data2.get("FullChargedCapacity")

            if design_cap and full_cap and design_cap > 0:
                battery.present = True
                battery.design_capacity_mwh = float(design_cap)
                battery.full_charge_capacity_mwh = float(full_cap)
                health = min(100.0, (float(full_cap) / float(design_cap)) * 100.0)
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
                    source="windows:root/WMI:BatteryStaticData,BatteryFullChargedCapacity",
                    method="wmi_acpi_ratio",
                    status=ProvenanceStatus.MEASURED,
                    confidence=ProvenanceConfidence.HIGH,
                    unit="percent"
                )
        except Exception:
            pass

        # AC and charging state via psutil
        try:
            ps_bat = psutil.sensors_battery()
            if ps_bat:
                battery.present = True
                battery.ac_connected = ps_bat.power_plugged
                battery.is_charging = ps_bat.power_plugged and ps_bat.percent < 99.0
                if battery.health_pct is None:
                    # Do NOT use ps_bat.percent as health!
                    self._record_prov(
                        "battery.health_pct", None,
                        source="windows:psutil",
                        method="os_snapshot",
                        status=ProvenanceStatus.UNAVAILABLE,
                        confidence=ProvenanceConfidence.UNAVAILABLE,
                        limitations=["psutil exposes instantaneous charge level (%), not physical battery health/wear"]
                    )
        except Exception:
            pass

        if not battery.present:
            battery.category = BatteryHealthCategory.UNABLE_TO_DETERMINE
            self._record_prov(
                "battery.present", False,
                source="windows:CIM",
                method="wmi_query",
                status=ProvenanceStatus.REPORTED,
                confidence=ProvenanceConfidence.HIGH,
                limitations=["No physical battery found"]
            )

        return battery
