"""Unit tests for Workload Matching, Anomaly Detection, and Reporting."""
import os
import re
from agent.hardware.manager import get_hardware_snapshot
from agent.workloads.profiles import evaluate_workload, WORKLOAD_DEFINITIONS
from agent.reporting.analysis import detect_anomalies, classify_categories
from agent.reporting.pdf_generator import generate_pdf_report
from agent.models import (
    BenchmarkResult, BenchmarkMetric, StatusEnum, ThermalSample,
    DiagnosticReport
)
from agent.runner import generate_report_id

def test_report_id_format():
    rid = generate_report_id()
    assert re.match(r"^LC-\d{4}-\d{2}-\d{2}-[A-Z0-9]{6}$", rid)

def test_computational_materials_science_evaluation():
    high_perf_hw = get_hardware_snapshot(simulate=True, preset="high_performance")
    benchmarks = [
        BenchmarkResult(
            benchmark_id="cpu",
            display_name="CPU",
            duration_secs=5.0,
            score=9500.0,
            degradation_pct=4.5,
            metrics=[BenchmarkMetric(name="Observed Degradation", value=4.5, unit="%", description="")]
        ),
        BenchmarkResult(
            benchmark_id="memory",
            display_name="Memory",
            duration_secs=3.0,
            score=25000.0,
            metrics=[BenchmarkMetric(name="Average Bandwidth", value=58.2, unit="GB/s", description="")]
        )
    ]
    res = evaluate_workload("comp_materials_science", high_perf_hw, benchmarks)
    assert res.profile_id == "comp_materials_science"
    assert res.overall_status in [StatusEnum.PASS, StatusEnum.CAUTION]
    assert len(res.criteria) >= 6

def test_anomaly_detection_throttling():
    hw = get_hardware_snapshot(simulate=True, preset="thermally_limited")
    benchmarks = [
        BenchmarkResult(
            benchmark_id="cpu",
            display_name="CPU",
            duration_secs=10.0,
            score=3000.0,
            degradation_pct=32.0,  # Severe throttling
            metrics=[BenchmarkMetric(name="Observed Degradation", value=32.0, unit="%", description="")]
        )
    ]
    thermal_samples = [
        ThermalSample(timestamp=1.0, elapsed_secs=1.0, cpu_temp_c=94.0)
    ]
    anomalies = detect_anomalies(hw, benchmarks, thermal_samples)
    assert any("Thermal" in a.title or "Degradation" in a.title for a in anomalies)
    categories = classify_categories(hw, benchmarks, anomalies)
    assert categories["Thermals"] in [StatusEnum.CAUTION, StatusEnum.FAIL]

def test_pdf_generation(tmp_path):
    hw = get_hardware_snapshot(simulate=True, preset="mid_range")
    report = DiagnosticReport(
        report_id=generate_report_id(),
        test_level="Quick",
        is_simulation=True,
        hardware=hw,
        summary_categories={"CPU": StatusEnum.PASS, "Thermals": StatusEnum.PASS}
    )
    pdf_path = str(tmp_path / "test_report.pdf")
    out = generate_pdf_report(report, pdf_path)
    assert os.path.exists(out)
    assert os.path.getsize(out) > 2000
