"""Simulation Hardware Provider for LaptopCheck.
Mandatory for testing and demonstrations without stressing real shop hardware.
Supports 6 distinct realistic machine profiles:
1. Low-end laptop
2. Mid-range laptop
3. High-performance workstation laptop
4. Thermally limited laptop (throttles heavily under load)
5. Battery-degraded laptop (low capacity, high cycle count)
6. Storage-warning laptop (SMART wear and error warnings)

All simulated snapshots are explicitly flagged with is_simulation=True and labeled clearly.
"""
from typing import List, Tuple, Dict, Any

from agent.hardware.base import HardwareProvider
from agent.models import (
    CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo,
    SystemHardwareSnapshot, BatteryHealthCategory
)

SIMULATED_PRESETS: Dict[str, Dict[str, Any]] = {
    "low_end": {
        "label": "Low-End Budget Laptop",
        "mfg": "BudgetTech",
        "model": "EcoBook 14 (Dual-Core Celeron)",
        "cpu": CPUInfo(
            model="Intel Celeron N4020 @ 1.10GHz",
            manufacturer="Intel",
            architecture="x86_64",
            cores_physical=2,
            threads_logical=2,
            base_freq_mhz=1100.0,
            max_freq_mhz=2800.0,
            current_freq_mhz=2100.0,
            instruction_sets=["SSE4_2"],
            virtualization=True,
            usage_percent=12.5,
            temperature_c=42.0
        ),
        "ram": RAMInfo(
            total_gb=4.0,
            available_gb=1.6,
            used_gb=2.4,
            memory_type="LPDDR4",
            speed_mhz=2400,
            channels="Single Channel",
            modules_count=1,
            bandwidth_gb_s=9.6
        ),
        "gpus": [
            GPUInfo(name="Intel UHD Graphics 600", vendor="Intel", is_dedicated=False, vram_mb=512)
        ],
        "storage": [
            StorageDriveInfo(
                device="/dev/mmcblk0",
                model="SanDisk 64GB eMMC",
                media_type="eMMC / Flash",
                capacity_gb=58.2,
                smart_status="Operational",
                health_pct=92.0,
                read_speed_mb_s=180.0,
                write_speed_mb_s=95.0
            )
        ],
        "battery": BatteryInfo(
            present=True,
            design_capacity_mwh=35000.0,
            full_charge_capacity_mwh=31500.0,
            health_pct=90.0,
            cycle_count=120,
            category=BatteryHealthCategory.HEALTHY,
            is_charging=False,
            ac_connected=True,
            temperature_c=29.0
        ),
        "os": OSInfo(
            system="Linux",
            release="Ubuntu 22.04 LTS",
            version="5.15.0-generic",
            architecture="x86_64",
            hostname="budget-ecobook"
        ),
        "thermal_behavior": "normal"
    },
    "mid_range": {
        "label": "Mid-Range Productivity Laptop",
        "mfg": "Lenovo",
        "model": "ThinkPad E14 Gen 4",
        "cpu": CPUInfo(
            model="12th Gen Intel Core i5-1240P",
            manufacturer="Intel",
            architecture="x86_64",
            cores_physical=12,
            threads_logical=16,
            base_freq_mhz=1700.0,
            max_freq_mhz=4400.0,
            current_freq_mhz=2800.0,
            instruction_sets=["AVX", "AVX2", "FMA", "AES", "VMX"],
            virtualization=True,
            usage_percent=8.0,
            temperature_c=48.0
        ),
        "ram": RAMInfo(
            total_gb=16.0,
            available_gb=11.2,
            used_gb=4.8,
            memory_type="DDR4",
            speed_mhz=3200,
            channels="Dual Channel",
            modules_count=2,
            bandwidth_gb_s=24.5
        ),
        "gpus": [
            GPUInfo(name="Intel Iris Xe Graphics", vendor="Intel", is_dedicated=False, vram_mb=2048)
        ],
        "storage": [
            StorageDriveInfo(
                device="/dev/nvme0n1",
                model="Samsung PM991a 512GB NVMe",
                media_type="NVMe SSD",
                capacity_gb=476.9,
                smart_status="Healthy",
                health_pct=98.0,
                read_speed_mb_s=2800.0,
                write_speed_mb_s=1800.0
            )
        ],
        "battery": BatteryInfo(
            present=True,
            design_capacity_mwh=57000.0,
            full_charge_capacity_mwh=52400.0,
            health_pct=91.9,
            cycle_count=185,
            category=BatteryHealthCategory.HEALTHY,
            is_charging=False,
            ac_connected=True,
            temperature_c=31.5
        ),
        "os": OSInfo(
            system="Linux",
            release="Ubuntu 24.04 LTS",
            version="6.8.0-generic",
            architecture="x86_64",
            hostname="thinkpad-e14"
        ),
        "thermal_behavior": "normal"
    },
    "high_performance": {
        "label": "High-Performance Workstation Laptop",
        "mfg": "Dell",
        "model": "Precision 7780 Mobile Workstation",
        "cpu": CPUInfo(
            model="Intel Core i9-13950HX (24 cores, 32 threads)",
            manufacturer="Intel",
            architecture="x86_64",
            cores_physical=24,
            threads_logical=32,
            base_freq_mhz=2200.0,
            max_freq_mhz=5500.0,
            current_freq_mhz=3800.0,
            instruction_sets=["AVX", "AVX2", "FMA", "AES", "VMX", "AVX-VNNI"],
            virtualization=True,
            usage_percent=4.0,
            temperature_c=52.0
        ),
        "ram": RAMInfo(
            total_gb=64.0,
            available_gb=56.0,
            used_gb=8.0,
            memory_type="DDR5",
            speed_mhz=5600,
            channels="Quad Channel (2x 32GB Dual)",
            modules_count=2,
            bandwidth_gb_s=58.2
        ),
        "gpus": [
            GPUInfo(name="Intel UHD Graphics", vendor="Intel", is_dedicated=False, vram_mb=1024),
            GPUInfo(name="NVIDIA RTX 4000 Ada Generation Laptop GPU", vendor="NVIDIA", is_dedicated=True, vram_mb=12288, driver_version="550.78", temperature_c=46.0)
        ],
        "storage": [
            StorageDriveInfo(
                device="/dev/nvme0n1",
                model="Kioxia 2TB Gen4 PCIe NVMe SSD",
                media_type="NVMe SSD",
                capacity_gb=1907.7,
                smart_status="Healthy",
                health_pct=99.0,
                read_speed_mb_s=6800.0,
                write_speed_mb_s=5200.0
            )
        ],
        "battery": BatteryInfo(
            present=True,
            design_capacity_mwh=93000.0,
            full_charge_capacity_mwh=89500.0,
            health_pct=96.2,
            cycle_count=64,
            category=BatteryHealthCategory.HEALTHY,
            is_charging=False,
            ac_connected=True,
            temperature_c=33.0
        ),
        "os": OSInfo(
            system="Linux",
            release="Debian GNU/Linux 12 (bookworm)",
            version="6.1.0-21-amd64",
            architecture="x86_64",
            hostname="precision-rig"
        ),
        "thermal_behavior": "excellent"
    },
    "thermally_limited": {
        "label": "Thermally Limited / Throttling Laptop",
        "mfg": "UltraThin Corp",
        "model": "SlimBlade Pro 15",
        "cpu": CPUInfo(
            model="Intel Core i7-11800H @ 2.30GHz",
            manufacturer="Intel",
            architecture="x86_64",
            cores_physical=8,
            threads_logical=16,
            base_freq_mhz=2300.0,
            max_freq_mhz=4600.0,
            current_freq_mhz=2100.0,
            instruction_sets=["AVX", "AVX2", "FMA", "AES"],
            virtualization=True,
            usage_percent=14.0,
            temperature_c=68.0  # High idle temperature!
        ),
        "ram": RAMInfo(
            total_gb=16.0,
            available_gb=10.5,
            used_gb=5.5,
            memory_type="DDR4",
            speed_mhz=3200,
            channels="Dual Channel",
            modules_count=2,
            bandwidth_gb_s=22.0
        ),
        "gpus": [
            GPUInfo(name="NVIDIA GeForce RTX 3060 Laptop GPU", vendor="NVIDIA", is_dedicated=True, vram_mb=6144, temperature_c=62.0)
        ],
        "storage": [
            StorageDriveInfo(
                device="/dev/nvme0n1",
                model="SK Hynix 1TB NVMe",
                media_type="NVMe SSD",
                capacity_gb=953.8,
                smart_status="Healthy",
                health_pct=94.0,
                read_speed_mb_s=3100.0,
                write_speed_mb_s=2200.0
            )
        ],
        "battery": BatteryInfo(
            present=True,
            design_capacity_mwh=70000.0,
            full_charge_capacity_mwh=58000.0,
            health_pct=82.8,
            cycle_count=310,
            category=BatteryHealthCategory.HEALTHY,
            is_charging=False,
            ac_connected=True,
            temperature_c=41.0
        ),
        "os": OSInfo(
            system="Windows",
            release="Windows 11 Home",
            version="10.0.22631",
            architecture="x86_64",
            hostname="slimblade-hot"
        ),
        "thermal_behavior": "throttling"
    },
    "battery_degraded": {
        "label": "Battery-Degraded Used Laptop",
        "mfg": "Latitude Refurb",
        "model": "Latitude 5490 (Used Shop Stock)",
        "cpu": CPUInfo(
            model="Intel Core i5-8350U @ 1.70GHz",
            manufacturer="Intel",
            architecture="x86_64",
            cores_physical=4,
            threads_logical=8,
            base_freq_mhz=1700.0,
            max_freq_mhz=3600.0,
            current_freq_mhz=2200.0,
            instruction_sets=["AVX", "AVX2", "FMA", "AES"],
            virtualization=True,
            usage_percent=9.0,
            temperature_c=46.0
        ),
        "ram": RAMInfo(
            total_gb=8.0,
            available_gb=4.2,
            used_gb=3.8,
            memory_type="DDR4",
            speed_mhz=2400,
            channels="Single Channel",
            modules_count=1,
            bandwidth_gb_s=14.0
        ),
        "gpus": [
            GPUInfo(name="Intel UHD Graphics 620", vendor="Intel", is_dedicated=False, vram_mb=1024)
        ],
        "storage": [
            StorageDriveInfo(
                device="/dev/sda",
                model="Micron 256GB 2.5 SATA SSD",
                media_type="SATA SSD",
                capacity_gb=238.4,
                smart_status="Healthy",
                health_pct=88.0,
                read_speed_mb_s=520.0,
                write_speed_mb_s=440.0
            )
        ],
        "battery": BatteryInfo(
            present=True,
            design_capacity_mwh=68000.0,
            full_charge_capacity_mwh=34500.0,  # 50.7% health!
            health_pct=50.7,
            cycle_count=842,
            category=BatteryHealthCategory.SIGNIFICANTLY_REDUCED,
            is_charging=False,
            ac_connected=False,
            temperature_c=34.0
        ),
        "os": OSInfo(
            system="Windows",
            release="Windows 10 Pro",
            version="10.0.19045",
            architecture="x86_64",
            hostname="latitude-used"
        ),
        "thermal_behavior": "normal"
    },
    "storage_warning": {
        "label": "Storage-Warning Laptop (SMART Wear / Bad Sectors)",
        "mfg": "Compaq Legacy",
        "model": "Notebook 15-da00",
        "cpu": CPUInfo(
            model="Intel Core i3-1005G1 @ 1.20GHz",
            manufacturer="Intel",
            architecture="x86_64",
            cores_physical=2,
            threads_logical=4,
            base_freq_mhz=1200.0,
            max_freq_mhz=3400.0,
            current_freq_mhz=1800.0,
            instruction_sets=["AVX", "AVX2", "FMA"],
            virtualization=True,
            usage_percent=15.0,
            temperature_c=49.0
        ),
        "ram": RAMInfo(
            total_gb=8.0,
            available_gb=4.0,
            used_gb=4.0,
            memory_type="DDR4",
            speed_mhz=2666,
            channels="Single Channel",
            modules_count=1,
            bandwidth_gb_s=12.5
        ),
        "gpus": [
            GPUInfo(name="Intel UHD Graphics", vendor="Intel", is_dedicated=False, vram_mb=1024)
        ],
        "storage": [
            StorageDriveInfo(
                device="/dev/sda",
                model="Kingston A400 240GB SSD",
                media_type="SATA SSD",
                capacity_gb=223.5,
                smart_status="WARNING: Reallocated Sectors / High Wear Count (148 sectors)",
                health_pct=58.0,
                read_speed_mb_s=210.0,
                write_speed_mb_s=85.0
            )
        ],
        "battery": BatteryInfo(
            present=True,
            design_capacity_mwh=41000.0,
            full_charge_capacity_mwh=32000.0,
            health_pct=78.0,
            cycle_count=420,
            category=BatteryHealthCategory.REDUCED_CAPACITY,
            is_charging=True,
            ac_connected=True,
            temperature_c=32.0
        ),
        "os": OSInfo(
            system="Linux",
            release="Debian GNU/Linux 11 (bullseye)",
            version="5.10.0-generic",
            architecture="x86_64",
            hostname="storage-warn-box"
        ),
        "thermal_behavior": "normal"
    }
}

class SimulatedHardwareProvider(HardwareProvider):
    """Provides high-fidelity simulated hardware snapshots for testing."""

    def __init__(self, preset_key: str = "mid_range"):
        if preset_key not in SIMULATED_PRESETS:
            preset_key = "mid_range"
        self.preset_key = preset_key
        self.preset = SIMULATED_PRESETS[preset_key]

    def get_system_model(self) -> Tuple[str, str]:
        return self.preset["mfg"], self.preset["model"]

    def get_os_info(self) -> OSInfo:
        return self.preset["os"]

    def get_cpu_info(self) -> CPUInfo:
        return self.preset["cpu"]

    def get_ram_info(self) -> RAMInfo:
        return self.preset["ram"]

    def get_gpu_info(self) -> List[GPUInfo]:
        return self.preset["gpus"]

    def get_storage_info(self) -> List[StorageDriveInfo]:
        return self.preset["storage"]

    def get_battery_info(self) -> BatteryInfo:
        return self.preset["battery"]

    def get_full_snapshot(self) -> SystemHardwareSnapshot:
        mfg, model = self.get_system_model()
        return SystemHardwareSnapshot(
            device_model=model,
            manufacturer=mfg,
            is_simulation=True,
            simulation_profile_name=self.preset["label"],
            os=self.get_os_info(),
            cpu=self.get_cpu_info(),
            ram=self.get_ram_info(),
            gpus=self.get_gpu_info(),
            storage=self.get_storage_info(),
            battery=self.get_battery_info()
        )
