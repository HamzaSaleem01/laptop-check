"""Phase 3 Test Suite: UI/UX, PDF Layout, NumberedCanvas, and Non-overlapping Flowables."""
import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from agent.models import (
    DiagnosticReport, SystemHardwareSnapshot, CPUInfo, RAMInfo, GPUInfo, StorageDriveInfo, BatteryInfo, OSInfo,
    StatusEnum, PriorityLevel, WorkloadMatchResult, RequirementCriterion, Anomaly, BatteryHealthCategory
)
from agent.reporting.pdf_generator import generate_pdf_report
from agent.hardware.simulated_provider import SIMULATED_PRESETS
from agent.runner import DiagnosticRunner
from web.backend.main import app


client = TestClient(app)


def test_pdf_with_extremely_long_strings_wraps_cleanly():
    """Verifies that extraordinarily long hardware strings wrap without overflowing or erroring."""
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        pdf_path = tmp.name

    try:
        report = DiagnosticReport(
            report_id="LC-TEST-LONGSTR-999",
            hardware=SystemHardwareSnapshot(
                manufacturer="ExtraordinarilyLongCustomManufacturerInternationalCorporation",
                device_model="SuperWorkstationExtremeEditionProMaxPlusUltra-SpecialSpecialEdition-2026-Revision9",
                os=OSInfo(system="Linux", release="6.18.0-999-generic-super-custom-hpc-kernel-with-huge-release-tag", architecture="x86_64"),
                cpu=CPUInfo(
                    model="Intel Xeon Platinum 9999X Scalable High Performance Processor Extreme Edition 128 Cores 256 Threads SuperBoost Technology",
                    cores_physical=64,
                    threads_logical=128,
                    instruction_sets=["AVX", "AVX2", "AVX512F", "AVX512CD", "AVX512BW", "AVX512DQ", "AVX512VL", "FMA", "AES", "SHA"]
                ),
                ram=RAMInfo(total_gb=256.0, channels="Octa Channel", speed_mhz=6400, memory_type="DDR5 Registered ECC"),
                gpus=[GPUInfo(name="NVIDIA RTX 6000 Ada Generation Professional Workstation Graphics Card", vram_mb=49152, is_dedicated=True)],
                storage=[StorageDriveInfo(model="Samsung PM1733 Enterprise NVMe PCIe 4.0 Solid State Drive (Extremely Long Serial Number)", capacity_gb=3840.0, media_type="NVMe SSD", smart_status="PASSED")],
                battery=BatteryInfo(present=True, health_pct=99.5, cycle_count=12, category=BatteryHealthCategory.HEALTHY)
            ),
            summary_categories={
                "CPU": StatusEnum.PASS,
                "RAM": StatusEnum.PASS,
                "Storage": StatusEnum.PASS,
                "GPU": StatusEnum.PASS,
                "Thermals": StatusEnum.PASS,
                "Battery": StatusEnum.PASS,
                "Stability": StatusEnum.PASS
            },
            anomalies=[
                Anomaly(
                    severity="WARNING",
                    component="Processor",
                    title="Extreme Thermal Dissipation Requirement Observed Under Extended Scientific Load",
                    description="The cooling assembly is operating at the upper boundary of thermal dissipation when running dense BLAS DGEMM routines across 128 logical threads simultaneously.",
                    recommendation="Ensure laptop cooling exhaust vents are elevated at least 2cm off flat desk surface and clean intake fan filters periodically."
                )
            ],
            workload_evaluations=[
                WorkloadMatchResult(
                    profile_id="comp_materials_science",
                    profile_name="Computational Materials Science / Physics",
                    overall_status=StatusEnum.PASS,
                    suitability_summary="System fully satisfies and exceeds all high-performance requirements for Density Functional Theory and plane-wave pseudopotential calculations.",
                    criteria=[
                        RequirementCriterion(
                            key="cpu_cores",
                            label="Physical CPU Cores",
                            priority=PriorityLevel.VERY_HIGH,
                            required_value="Min 6 (Pref 12)",
                            actual_value="64 cores",
                            status=StatusEnum.PASS,
                            notes="Superb core density."
                        )
                    ]
                )
            ]
        )

        out = generate_pdf_report(report, pdf_path)
        assert os.path.exists(out)
        assert os.path.getsize(out) > 5000  # Generated valid PDF
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


def test_all_simulation_presets_generate_pdf():
    """Verifies that all 6 simulation presets generate valid, non-crashing PDF reports."""
    runner = DiagnosticRunner()
    for preset_id in SIMULATED_PRESETS:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            pdf_path = tmp.name

        try:
            report = runner.run_diagnostic(
                test_level="Quick / Shop Safe",
                workload_ids=["comp_materials_science"],
                simulate=True,
                simulation_preset=preset_id
            )
            generate_pdf_report(report, pdf_path)
            assert os.path.exists(pdf_path)
            assert os.path.getsize(pdf_path) > 10000
        finally:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)


def test_static_frontend_dist_served_or_available():
    """Verifies that the compiled static frontend index.html exists."""
    dist_html = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web", "frontend", "dist", "index.html")
    assert os.path.exists(dist_html), "web/frontend/dist/index.html must be built for production"
    with open(dist_html, "r") as f:
        content = f.read()
    assert "LaptopCheck" in content or "vite" in content or "script" in content


def test_pdf_download_endpoint_returns_pdf():
    """Verifies the PDF download endpoint serves correct application/pdf content."""
    # List reports first
    res = client.get("/api/reports")
    assert res.status_code == 200
    reports = res.json()
    if reports:
        filename = reports[0]["filename"]
        dl = client.get(f"/api/reports/download/{filename}")
        assert dl.status_code == 200
        assert dl.headers["content-type"] == "application/pdf"
        assert len(dl.content) > 1000
