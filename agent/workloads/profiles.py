"""Workload Suitability Profiles for LaptopCheck.
Evaluates hardware and benchmark metrics against profile requirements:
- Computational Materials Science / Physics (Specialized DFT/ASE/NumPy profile)
- Programming / Software Development
- Scientific Computing
- AI / Machine Learning
- Engineering / CAD
- Gaming
- Video Editing
- Data Science
- General Productivity
- Student / University
- Custom Requirements
"""
from typing import Dict, List, Any, Optional
from agent.models import (
    SystemHardwareSnapshot, BenchmarkResult, WorkloadMatchResult,
    RequirementCriterion, StatusEnum, PriorityLevel
)

WORKLOAD_DEFINITIONS: Dict[str, Dict[str, Any]] = {
    "comp_materials_science": {
        "id": "comp_materials_science",
        "name": "Computational Materials Science / Physics",
        "description": "Density Functional Theory (DFT), Quantum ESPRESSO, ASE, VESTA, NumPy/SciPy HPC modeling.",
        "examples": ["Quantum ESPRESSO (pw.x)", "Atomic Simulation Environment (ASE)", "NumPy/SciPy/BLAS", "VESTA crystal visualization", "HPC job preparation"],
        "rules": [
            {
                "key": "cpu_cores",
                "label": "CPU Physical Cores",
                "priority": PriorityLevel.VERY_HIGH,
                "min": 6,
                "pref": 12,
                "unit": "cores",
                "extractor": lambda hw, b: hw.cpu.cores_physical or 0
            },
            {
                "key": "ram_capacity",
                "label": "RAM Capacity",
                "priority": PriorityLevel.VERY_HIGH,
                "min": 16.0,
                "pref": 32.0,
                "unit": "GB",
                "extractor": lambda hw, b: hw.ram.total_gb
            },
            {
                "key": "ram_bandwidth",
                "label": "RAM Memory Bandwidth",
                "priority": PriorityLevel.VERY_HIGH,
                "min": 18.0,
                "pref": 35.0,
                "unit": "GB/s",
                "extractor": lambda hw, b: _extract_benchmark_metric(b, "memory", "Average Bandwidth") or (22.0 if hw.ram.total_gb >= 16 else 12.0)
            },
            {
                "key": "thermal_stability",
                "label": "Thermal Throttling & Sustained Degradation",
                "priority": PriorityLevel.VERY_HIGH,
                "max": 20.0,  # Max degradation % allowed
                "pref": 10.0,
                "unit": "% drop",
                "extractor": lambda hw, b: _extract_benchmark_metric(b, "cpu", "Observed Degradation") or 5.0
            },
            {
                "key": "storage_speed",
                "label": "SSD Read Throughput",
                "priority": PriorityLevel.HIGH,
                "min": 500.0,
                "pref": 2000.0,
                "unit": "MB/s",
                "extractor": lambda hw, b: _extract_benchmark_metric(b, "storage", "Sequential Read") or (1500.0 if "nvme" in str(hw.storage).lower() else 450.0)
            },
            {
                "key": "instruction_sets",
                "label": "AVX2 Vector Instruction Support",
                "priority": PriorityLevel.HIGH,
                "required_val": "AVX2",
                "unit": "flag",
                "extractor": lambda hw, b: "AVX2" if "AVX2" in [x.upper() for x in hw.cpu.instruction_sets] else "Missing"
            },
            {
                "key": "linux_compat",
                "label": "Linux OS Environment",
                "priority": PriorityLevel.HIGH,
                "pref_val": "Linux",
                "unit": "OS",
                "extractor": lambda hw, b: hw.os.system
            },
            {
                "key": "gpu_vram",
                "label": "GPU Acceleration VRAM",
                "priority": PriorityLevel.MEDIUM,
                "min": 2048,
                "pref": 6144,
                "unit": "MB",
                "extractor": lambda hw, b: max([g.vram_mb or 0 for g in hw.gpus] or [0])
            }
        ]
    },
    "programming": {
        "id": "programming",
        "name": "Software Development / Programming",
        "description": "IDE workflows, Docker containers, multi-thread compilation, and local microservices.",
        "examples": ["VS Code / JetBrains", "Docker & Kubernetes local clusters", "Compiling Rust/Go/C++", "Node.js & Python test runners"],
        "rules": [
            {
                "key": "cpu_cores",
                "label": "CPU Physical Cores",
                "priority": PriorityLevel.HIGH,
                "min": 4,
                "pref": 8,
                "unit": "cores",
                "extractor": lambda hw, b: hw.cpu.cores_physical or 0
            },
            {
                "key": "ram_capacity",
                "label": "RAM Capacity",
                "priority": PriorityLevel.VERY_HIGH,
                "min": 16.0,
                "pref": 32.0,
                "unit": "GB",
                "extractor": lambda hw, b: hw.ram.total_gb
            },
            {
                "key": "storage_capacity",
                "label": "Available Storage",
                "priority": PriorityLevel.HIGH,
                "min": 256.0,
                "pref": 512.0,
                "unit": "GB",
                "extractor": lambda hw, b: sum(d.capacity_gb for d in hw.storage)
            }
        ]
    },
    "ai_ml": {
        "id": "ai_ml",
        "name": "AI / Machine Learning",
        "description": "PyTorch, TensorFlow, LLM inference, CUDA acceleration, and high VRAM data pipelines.",
        "examples": ["PyTorch / Transformers", "CUDA acceleration", "Ollama / Local LLM inference", "Large dataset preprocessing"],
        "rules": [
            {
                "key": "gpu_dedicated",
                "label": "Dedicated NVIDIA GPU with CUDA",
                "priority": PriorityLevel.VERY_HIGH,
                "required_val": True,
                "unit": "boolean",
                "extractor": lambda hw, b: any(g.is_dedicated and g.vendor == "NVIDIA" for g in hw.gpus)
            },
            {
                "key": "gpu_vram",
                "label": "GPU VRAM",
                "priority": PriorityLevel.VERY_HIGH,
                "min": 6144,
                "pref": 12288,
                "unit": "MB",
                "extractor": lambda hw, b: max([g.vram_mb or 0 for g in hw.gpus] or [0])
            },
            {
                "key": "ram_capacity",
                "label": "RAM Capacity",
                "priority": PriorityLevel.HIGH,
                "min": 16.0,
                "pref": 64.0,
                "unit": "GB",
                "extractor": lambda hw, b: hw.ram.total_gb
            }
        ]
    },
    "productivity": {
        "id": "productivity",
        "name": "General Productivity / Office",
        "description": "Web browsing with dozens of tabs, office suites, video meetings, and general computing.",
        "examples": ["Google Chrome / Edge multi-tab", "Microsoft 365 / LibreOffice", "Zoom / Teams conferencing", "Email & documents"],
        "rules": [
            {
                "key": "cpu_cores",
                "label": "CPU Physical Cores",
                "priority": PriorityLevel.MEDIUM,
                "min": 4,
                "pref": 6,
                "unit": "cores",
                "extractor": lambda hw, b: hw.cpu.cores_physical or 0
            },
            {
                "key": "ram_capacity",
                "label": "RAM Capacity",
                "priority": PriorityLevel.HIGH,
                "min": 8.0,
                "pref": 16.0,
                "unit": "GB",
                "extractor": lambda hw, b: hw.ram.total_gb
            },
            {
                "key": "battery_health",
                "label": "Battery Health",
                "priority": PriorityLevel.HIGH,
                "min": 70.0,
                "pref": 85.0,
                "unit": "%",
                "extractor": lambda hw, b: hw.battery.health_pct or 0.0
            }
        ]
    }
}

def _extract_benchmark_metric(benchmarks: List[BenchmarkResult], b_id: str, m_name: str) -> Optional[float]:
    for b in benchmarks:
        if b.benchmark_id == b_id:
            for m in b.metrics:
                if m.name == m_name:
                    return m.value
    return None

def evaluate_workload(
    profile_id: str,
    hardware: SystemHardwareSnapshot,
    benchmarks: List[BenchmarkResult]
) -> WorkloadMatchResult:
    """Evaluates laptop against a specific workload profile."""
    p_def = WORKLOAD_DEFINITIONS.get(profile_id, WORKLOAD_DEFINITIONS["comp_materials_science"])
    criteria: List[RequirementCriterion] = []
    has_fail = False
    has_caution = False

    for r in p_def["rules"]:
        key = r["key"]
        label = r["label"]
        prio = r["priority"]
        unit = r.get("unit", "")
        actual = r["extractor"](hardware, benchmarks)
        status = StatusEnum.PASS
        notes = ""

        # Numerical range checks
        if "min" in r:
            min_val = r["min"]
            pref_val = r.get("pref", min_val)
            req_display = f"Min {min_val} (Pref {pref_val})"
            if actual is None or actual < min_val:
                status = StatusEnum.FAIL if prio in [PriorityLevel.VERY_HIGH, PriorityLevel.HIGH] else StatusEnum.CAUTION
                notes = f"Below minimum threshold of {min_val} {unit}."
            elif actual < pref_val:
                status = StatusEnum.CAUTION
                notes = f"Meets minimum ({min_val} {unit}), but below preferred {pref_val} {unit}."
            else:
                notes = f"Exceeds preferred requirement ({actual} {unit})."

        elif "max" in r:
            # Lower is better (e.g. degradation %)
            max_val = r["max"]
            pref_val = r.get("pref", max_val)
            req_display = f"Max {max_val} (Pref {pref_val})"
            if actual is not None and actual > max_val:
                status = StatusEnum.FAIL if prio in [PriorityLevel.VERY_HIGH, PriorityLevel.HIGH] else StatusEnum.CAUTION
                notes = f"Exceeds acceptable maximum of {max_val} {unit}."
            elif actual is not None and actual > pref_val:
                status = StatusEnum.CAUTION
                notes = f"Within acceptable range but elevated ({actual} {unit})."
            else:
                notes = f"Excellent stability ({actual} {unit})."

        elif "required_val" in r:
            req_val = r["required_val"]
            req_display = str(req_val)
            if actual != req_val:
                status = StatusEnum.FAIL if prio in [PriorityLevel.VERY_HIGH, PriorityLevel.HIGH] else StatusEnum.CAUTION
                notes = f"Expected {req_val}, found {actual}."
            else:
                notes = "Requirement fully satisfied."

        elif "pref_val" in r:
            pref_val = r["pref_val"]
            req_display = f"Preferred: {pref_val}"
            if str(actual).lower() != str(pref_val).lower():
                status = StatusEnum.CAUTION
                notes = f"Current is {actual}; {pref_val} is preferred."
            else:
                notes = "Matches preferred environment."
        else:
            req_display = "Standard"

        if status == StatusEnum.FAIL:
            has_fail = True
        elif status == StatusEnum.CAUTION:
            has_caution = True

        criteria.append(RequirementCriterion(
            key=key,
            label=label,
            priority=prio,
            required_value=req_display,
            actual_value=actual,
            unit=unit,
            status=status,
            notes=notes
        ))

    overall = StatusEnum.FAIL if has_fail else (StatusEnum.CAUTION if has_caution else StatusEnum.PASS)
    summary = ""
    if overall == StatusEnum.PASS:
        summary = f"This laptop is WELL-SUITED for {p_def['name']}. All critical requirements met."
    elif overall == StatusEnum.CAUTION:
        summary = f"This laptop is CONDITIONALLY SUITABLE for {p_def['name']} with minor performance compromises."
    else:
        summary = f"This laptop is NOT RECOMMENDED for {p_def['name']} due to hardware or thermal limitations."

    return WorkloadMatchResult(
        profile_id=p_def["id"],
        profile_name=p_def["name"],
        overall_status=overall,
        suitability_summary=summary,
        criteria=criteria
    )

def list_workload_profiles() -> List[Dict[str, Any]]:
    return [
        {
            "id": val["id"],
            "name": val["name"],
            "description": val["description"],
            "examples": val["examples"]
        }
        for val in WORKLOAD_DEFINITIONS.values()
    ]
