"""Data models for LaptopCheck.
Strictly typed, serializable, with safe fallback representations.
"""
from enum import Enum
from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

class StatusEnum(str, Enum):
    PASS = "PASS"
    CAUTION = "CAUTION"
    FAIL = "FAIL"
    NOT_AVAILABLE = "NOT AVAILABLE"
    NOT_TESTED = "NOT TESTED"
    SKIPPED = "SKIPPED"

class SafetyLevel(str, Enum):
    NORMAL = "NORMAL"
    WARNING = "WARNING"
    REDUCE_LOAD = "REDUCE LOAD"
    PAUSE = "PAUSE"
    STOP = "STOP"

class BatteryHealthCategory(str, Enum):
    HEALTHY = "Healthy"
    REDUCED_CAPACITY = "Reduced Capacity"
    SIGNIFICANTLY_REDUCED = "Significantly Reduced"
    UNABLE_TO_DETERMINE = "Unable to Determine"

class PriorityLevel(str, Enum):
    VERY_HIGH = "Very High"
    HIGH = "High"
    MEDIUM = "Medium"
    LOWER = "Lower Priority"

class ProvenanceStatus(str, Enum):
    MEASURED = "measured"
    REPORTED = "reported"
    INFERRED = "inferred"
    USER_CONFIRMED = "user_confirmed"
    UNAVAILABLE = "unavailable"
    PERMISSION_DENIED = "permission_denied"
    UNSUPPORTED = "unsupported"
    CONFLICT = "conflict"
    SIMULATED = "simulated"

class ProvenanceConfidence(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNAVAILABLE = "unavailable"
    SIMULATED = "simulated"

class FieldProvenance(BaseModel):
    key: str
    value: Any = None
    unit: str = ""
    source: str = ""                # e.g., "linux:/proc/cpuinfo", "linux:/sys/class/power_supply/BAT0", "windows:Win32_Processor"
    method: str = ""                # e.g., "os_topology", "acpi_sysfs", "smbios_firmware", "psutil"
    confidence: ProvenanceConfidence = ProvenanceConfidence.HIGH
    status: ProvenanceStatus = ProvenanceStatus.REPORTED
    observed_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    limitations: List[str] = Field(default_factory=list)

class CPUInfo(BaseModel):
    model: str = "Not available"
    manufacturer: str = "Not available"
    architecture: str = "Not available"
    cores_physical: Optional[int] = None
    threads_logical: Optional[int] = None
    p_cores: Optional[int] = None
    e_cores: Optional[int] = None
    stepping: Optional[str] = None
    base_freq_mhz: Optional[float] = None
    max_freq_mhz: Optional[float] = None
    current_freq_mhz: Optional[float] = None
    cache_l1d_kb: Optional[int] = None
    cache_l1i_kb: Optional[int] = None
    cache_l2_kb: Optional[int] = None
    cache_l3_kb: Optional[int] = None
    instruction_sets: List[str] = Field(default_factory=list)
    virtualization: bool = False
    usage_percent: Optional[float] = None
    temperature_c: Optional[float] = None
    tdp_w: Optional[float] = None
    governor: Optional[str] = None

class RAMInfo(BaseModel):
    total_gb: float = 0.0
    available_gb: float = 0.0
    used_gb: float = 0.0
    memory_type: str = "Not available"  # DDR4, DDR5, LPDDR5, etc.
    speed_mhz: Optional[int] = None
    channels: str = "Not available"    # Dual, Single, Quad
    modules_count: Optional[int] = None
    is_soldered: Optional[bool] = None
    slots_total: Optional[int] = None
    slots_used: Optional[int] = None
    upgradeable: Optional[str] = None
    bandwidth_gb_s: Optional[float] = None

class GPUInfo(BaseModel):
    name: str = "Not available"
    vendor: str = "Not available"
    is_dedicated: bool = False
    vram_mb: Optional[int] = None
    shared_memory_mb: Optional[int] = None
    driver_version: str = "Not available"
    compute_apis: List[str] = Field(default_factory=list)  # CUDA, ROCm, Vulkan, OpenCL
    temperature_c: Optional[float] = None
    utilization_pct: Optional[float] = None

class StorageDriveInfo(BaseModel):
    device: str = "Not available"
    model: str = "Not available"
    media_type: str = "Not available" # NVMe, SATA SSD, HDD
    transport: Optional[str] = None    # nvme, sata, usb
    capacity_gb: float = 0.0
    smart_status: str = "Unable to determine"
    health_pct: Optional[float] = None
    smart_wear_pct: Optional[float] = None
    temperature_c: Optional[float] = None
    power_on_hours: Optional[int] = None
    read_speed_mb_s: Optional[float] = None
    write_speed_mb_s: Optional[float] = None
    smart_limitations: List[str] = Field(default_factory=list)

class BatteryInfo(BaseModel):
    present: bool = False
    design_capacity_mwh: Optional[float] = None
    full_charge_capacity_mwh: Optional[float] = None
    current_capacity_mwh: Optional[float] = None
    health_pct: Optional[float] = None
    wear_pct: Optional[float] = None
    cycle_count: Optional[int] = None
    power_w: Optional[float] = None
    voltage_v: Optional[float] = None
    category: BatteryHealthCategory = BatteryHealthCategory.UNABLE_TO_DETERMINE
    is_charging: Optional[bool] = None
    ac_connected: Optional[bool] = None
    temperature_c: Optional[float] = None
    source_label: Optional[str] = None

class OSInfo(BaseModel):
    system: str = "Not available"  # Linux, Windows
    release: str = "Not available"
    version: str = "Not available"
    architecture: str = "Not available"
    kernel: Optional[str] = None
    hostname: str = "Not available"
    serial_number: Optional[str] = None
    bios_version: Optional[str] = None
    bios_date: Optional[str] = None

class SystemHardwareSnapshot(BaseModel):
    schema_version: str = "2.0.0"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    device_model: str = "Generic / Custom Laptop"
    manufacturer: str = "Unknown"
    is_simulation: bool = False
    simulation_profile_name: Optional[str] = None
    is_redacted: bool = False
    redacted_fields: List[str] = Field(default_factory=list)
    os: OSInfo = Field(default_factory=OSInfo)
    cpu: CPUInfo = Field(default_factory=CPUInfo)
    ram: RAMInfo = Field(default_factory=RAMInfo)
    gpus: List[GPUInfo] = Field(default_factory=list)
    storage: List[StorageDriveInfo] = Field(default_factory=list)
    battery: BatteryInfo = Field(default_factory=BatteryInfo)
    provenance: Dict[str, FieldProvenance] = Field(default_factory=dict)

    def add_provenance(
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
        """Helper to append or update a field provenance record."""
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

    def get_redacted_snapshot(self) -> "SystemHardwareSnapshot":
        """Returns a sanitized snapshot with sensitive machine/network IDs redacted by default."""
        snap_copy = self.model_copy(deep=True)
        redacted_list = []

        if snap_copy.os.hostname and snap_copy.os.hostname != "Not available":
            snap_copy.os.hostname = "[REDACTED_HOSTNAME]"
            redacted_list.append("os.hostname")
        if snap_copy.os.serial_number:
            snap_copy.os.serial_number = "[REDACTED_SERIAL]"
            redacted_list.append("os.serial_number")

        # Redact any serial numbers in storage devices
        for drive in snap_copy.storage:
            if drive.model and any(kw in drive.model.lower() for kw in ["serial", "s/n", "uuid"]):
                drive.model = "[REDACTED_DRIVE_MODEL]"
                redacted_list.append(f"storage.{drive.device}.model")

        # Redact corresponding provenance keys
        for key in list(snap_copy.provenance.keys()):
            if any(sensitive in key for sensitive in ["serial", "hostname", "uuid", "machine_id"]):
                prov = snap_copy.provenance[key]
                prov.value = "[REDACTED]"
                redacted_list.append(key)

        snap_copy.is_redacted = True
        snap_copy.redacted_fields = list(set(redacted_list))
        return snap_copy

class ThermalSample(BaseModel):
    timestamp: float
    elapsed_secs: float
    cpu_temp_c: Optional[float] = None
    gpu_temp_c: Optional[float] = None
    battery_temp_c: Optional[float] = None
    cpu_freq_mhz: Optional[float] = None
    cpu_usage_pct: Optional[float] = None
    gpu_usage_pct: Optional[float] = None
    safety_level: SafetyLevel = SafetyLevel.NORMAL

class BenchmarkMetric(BaseModel):
    name: str
    value: float
    unit: str
    description: str

class BenchmarkResult(BaseModel):
    benchmark_id: str
    display_name: str
    duration_secs: float
    score: float
    metrics: List[BenchmarkMetric] = Field(default_factory=list)
    initial_performance: Optional[float] = None
    sustained_performance: Optional[float] = None
    degradation_pct: Optional[float] = None
    status: StatusEnum = StatusEnum.PASS
    details: str = ""

class Anomaly(BaseModel):
    severity: str = "WARNING"  # INFO, WARNING, CRITICAL
    component: str             # CPU, Thermals, Battery, Storage, Memory, System
    title: str
    description: str
    recommendation: str

class RequirementCriterion(BaseModel):
    key: str
    label: str
    priority: PriorityLevel
    required_value: Any
    actual_value: Any
    unit: str = ""
    status: StatusEnum
    notes: str = ""

class WorkloadMatchResult(BaseModel):
    profile_id: str
    profile_name: str
    overall_status: StatusEnum
    suitability_summary: str
    criteria: List[RequirementCriterion] = Field(default_factory=list)

class ManualInspectionItem(BaseModel):
    id: str
    category: str  # Display, Keyboard, Touchpad, Ports, Audio
    title: str
    status: StatusEnum = StatusEnum.NOT_TESTED
    notes: str = ""

class DiagnosticReport(BaseModel):
    report_id: str
    app_version: str = "1.0.0"
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    test_level: str = "Quick / Shop Safe"
    is_simulation: bool = False
    simulation_label: Optional[str] = None
    hardware: SystemHardwareSnapshot
    thermal_samples: List[ThermalSample] = Field(default_factory=list)
    benchmarks: List[BenchmarkResult] = Field(default_factory=list)
    workload_evaluations: List[WorkloadMatchResult] = Field(default_factory=list)
    anomalies: List[Anomaly] = Field(default_factory=list)
    manual_inspections: List[ManualInspectionItem] = Field(default_factory=list)
    
    # Executive category scores
    summary_categories: Dict[str, StatusEnum] = Field(default_factory=dict)
    executive_summary: str = ""
