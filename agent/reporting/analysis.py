"""Anomaly Detection & Executive Category Classification for LaptopCheck.
Identifies hardware bottlenecks, thermal throttling, battery wear, and produces professional findings.
"""
from typing import List, Dict, Tuple
from agent.models import (
    SystemHardwareSnapshot, BenchmarkResult, ThermalSample,
    Anomaly, StatusEnum, BatteryHealthCategory
)

def detect_anomalies(
    hardware: SystemHardwareSnapshot,
    benchmarks: List[BenchmarkResult],
    thermal_samples: List[ThermalSample]
) -> List[Anomaly]:
    """Analyzes system state and test history for anomalies."""
    anomalies: List[Anomaly] = []

    # 1. Idle / Baseline CPU utilization check
    if hardware.cpu.usage_percent and hardware.cpu.usage_percent > 35.0:
        anomalies.append(Anomaly(
            severity="WARNING",
            component="CPU",
            title="Elevated Baseline Background Activity",
            description=f"Idle CPU utilization was recorded at {hardware.cpu.usage_percent}%, suggesting background tasks, pending updates, or indexing.",
            recommendation="Inspect background processes or reboot before running critical computational workloads."
        ))

    # 2. Idle Temperature check
    if hardware.cpu.temperature_c and hardware.cpu.temperature_c > 65.0:
        anomalies.append(Anomaly(
            severity="WARNING",
            component="Thermals",
            title="Elevated Idle Temperature Observed",
            description=f"Baseline CPU temperature was {hardware.cpu.temperature_c}°C before heavy benchmark execution.",
            recommendation="Inspect cooling vents for dust accumulation and verify fan operation."
        ))

    # 3. Peak temperature & thermal throttling
    peak_temp = max([s.cpu_temp_c for s in thermal_samples if s.cpu_temp_c] or [hardware.cpu.temperature_c or 0.0])
    if peak_temp >= 90.0:
        anomalies.append(Anomaly(
            severity="WARNING",
            component="Thermals",
            title="Potential Thermal Limitation Detected",
            description=f"Peak CPU temperature reached {peak_temp}°C during load. System approached upper thermal boundaries.",
            recommendation="Consider laptop cooling elevation or thermal repasting if sustained heavy scientific workloads are planned."
        ))

    # 4. Sustained Performance Degradation Check
    for b in benchmarks:
        if b.benchmark_id == "cpu" and b.degradation_pct and b.degradation_pct >= 20.0:
            anomalies.append(Anomaly(
                severity="WARNING",
                component="CPU",
                title="Sustained Performance Degradation Observed",
                description=f"CPU multi-core throughput dropped by {b.degradation_pct}% between burst initial state and sustained test phase.",
                recommendation="Indicates thermal or OEM power budget throttling under prolonged multi-threaded load."
            ))

    # 5. Battery Degradation Check
    if hardware.battery.present:
        if hardware.battery.health_pct and hardware.battery.health_pct < 70.0:
            anomalies.append(Anomaly(
                severity="WARNING",
                component="Battery",
                title="Significantly Reduced Battery Capacity",
                description=f"Battery full charge capacity is at {hardware.battery.health_pct}% of original factory design ({hardware.battery.cycle_count or 'Unknown'} cycles recorded).",
                recommendation="Battery runtime off AC power will be substantially reduced. Replacement may be required."
            ))
        elif hardware.battery.cycle_count and hardware.battery.cycle_count > 500:
            anomalies.append(Anomaly(
                severity="INFO",
                component="Battery",
                title="High Battery Cycle Count",
                description=f"Battery has completed {hardware.battery.cycle_count} charge cycles.",
                recommendation="Normal wear for an experienced machine; monitor discharge rates during field use."
            ))

    # 6. Storage Health / SMART Warning Check
    for d in hardware.storage:
        if "warning" in d.smart_status.lower() or (d.health_pct and d.health_pct < 70.0):
            anomalies.append(Anomaly(
                severity="CRITICAL",
                component="Storage",
                title=f"Storage Drive Health Alert: {d.model}",
                description=f"Storage drive reported abnormal status: '{d.smart_status}'. Health rating: {d.health_pct or 'N/A'}%.",
                recommendation="Backup critical data immediately and schedule drive replacement."
            ))

    # 7. Memory Configuration Check
    if hardware.ram.channels == "Single Channel" and (hardware.cpu.cores_physical or 0) >= 6:
        anomalies.append(Anomaly(
            severity="INFO",
            component="Memory",
            title="Single-Channel RAM Memory Configuration",
            description="System is operating with single-channel memory on a modern multi-core processor, limiting peak memory bandwidth.",
            recommendation="Adding a matching secondary RAM module to enable dual-channel mode will noticeably boost memory-intensive and scientific workflows."
        ))

    return anomalies

def classify_categories(
    hardware: SystemHardwareSnapshot,
    benchmarks: List[BenchmarkResult],
    anomalies: List[Anomaly]
) -> Dict[str, StatusEnum]:
    """Generates the executive category status matrix."""
    categories: Dict[str, StatusEnum] = {
        "CPU": StatusEnum.PASS,
        "RAM": StatusEnum.PASS,
        "Storage": StatusEnum.PASS,
        "GPU": StatusEnum.PASS,
        "Thermals": StatusEnum.PASS,
        "Battery": StatusEnum.PASS,
        "Stability": StatusEnum.PASS
    }

    # Evaluate Thermals
    thermal_anoms = [a for a in anomalies if a.component == "Thermals"]
    if any(a.severity == "CRITICAL" for a in thermal_anoms):
        categories["Thermals"] = StatusEnum.FAIL
    elif any(a.severity == "WARNING" for a in thermal_anoms):
        categories["Thermals"] = StatusEnum.CAUTION

    # Evaluate Battery
    if not hardware.battery.present:
        categories["Battery"] = StatusEnum.NOT_AVAILABLE
    elif hardware.battery.health_pct and hardware.battery.health_pct < 60.0:
        categories["Battery"] = StatusEnum.CAUTION
    elif hardware.battery.category == BatteryHealthCategory.SIGNIFICANTLY_REDUCED:
        categories["Battery"] = StatusEnum.CAUTION

    # Evaluate Storage
    storage_anoms = [a for a in anomalies if a.component == "Storage"]
    if any(a.severity == "CRITICAL" for a in storage_anoms):
        categories["Storage"] = StatusEnum.FAIL
    elif any(a.severity == "WARNING" for a in storage_anoms):
        categories["Storage"] = StatusEnum.CAUTION

    # Evaluate CPU
    cpu_anoms = [a for a in anomalies if a.component == "CPU"]
    if any(a.severity == "CRITICAL" for a in cpu_anoms):
        categories["CPU"] = StatusEnum.FAIL
    elif any(a.severity == "WARNING" for a in cpu_anoms):
        categories["CPU"] = StatusEnum.CAUTION

    # Evaluate Memory
    if hardware.ram.total_gb < 8.0:
        categories["RAM"] = StatusEnum.CAUTION

    return categories
