"""Hardware Provider Base Interfaces.
Defines clean contracts for OS-specific implementations.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from agent.models import (
    CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo, SystemHardwareSnapshot
)

class HardwareProvider(ABC):
    """Abstract interface for system hardware detection."""

    @abstractmethod
    def get_os_info(self) -> OSInfo:
        pass

    @abstractmethod
    def get_cpu_info(self) -> CPUInfo:
        pass

    @abstractmethod
    def get_ram_info(self) -> RAMInfo:
        pass

    @abstractmethod
    def get_gpu_info(self) -> List[GPUInfo]:
        pass

    @abstractmethod
    def get_storage_info(self) -> List[StorageDriveInfo]:
        pass

    @abstractmethod
    def get_battery_info(self) -> BatteryInfo:
        pass

    @abstractmethod
    def get_system_model(self) -> tuple[str, str]:
        """Returns (manufacturer, model_name)"""
        pass

    def get_provenance_records(self) -> dict:
        """Returns provenance dictionary for detected fields."""
        return {}

    def get_full_snapshot(self) -> SystemHardwareSnapshot:
        mfg, model = self.get_system_model()
        snapshot = SystemHardwareSnapshot(
            device_model=model,
            manufacturer=mfg,
            is_simulation=False,
            os=self.get_os_info(),
            cpu=self.get_cpu_info(),
            ram=self.get_ram_info(),
            gpus=self.get_gpu_info(),
            storage=self.get_storage_info(),
            battery=self.get_battery_info()
        )
        snapshot.provenance = self.get_provenance_records()
        return snapshot
