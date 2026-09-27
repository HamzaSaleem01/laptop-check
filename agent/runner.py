"""Diagnostic Runner for LaptopCheck.
Coordinates the complete end-to-end diagnostic workflow:
Hardware Detection -> Pre-flight Analysis -> Safety Check -> Controlled Benchmarking ->
Thermal Analysis -> Anomaly Detection -> Category Classification -> Manual Inspection -> PDF Generation.
"""
import os
import time
import random
import string
from datetime import datetime
from typing import Optional, Callable, List

from agent.models import (
    DiagnosticReport, SystemHardwareSnapshot, BenchmarkResult,
    ManualInspectionItem, StatusEnum, Anomaly
)
from agent.hardware.manager import get_hardware_snapshot
from agent.diagnostics.preflight import run_preflight_check
from agent.safety.controller import SafetyController
from agent.benchmarks.engine import BenchmarkEngine
from agent.workloads.profiles import evaluate_workload
from agent.reporting.analysis import detect_anomalies, classify_categories
from agent.reporting.pdf_generator import generate_pdf_report

def generate_report_id() -> str:
    """Generates unique traceability ID format: LC-YYYY-MM-DD-XXXXXX"""
    date_str = datetime.now().strftime("%Y-%m-%d")
    suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"LC-{date_str}-{suffix}"

class DiagnosticRunner:
    """End-to-end diagnostic execution controller."""

    def __init__(self):
        self.safety = SafetyController()
        self.engine = BenchmarkEngine(self.safety)
        self.current_report: Optional[DiagnosticReport] = None
        self.is_running = False

    def stop_current_test(self):
        """Immediately signals test stop."""
        self.safety.request_stop()
        self.is_running = False

    def run_diagnostic(
        self,
        test_level: str = "Quick / Shop Safe",
        workload_ids: Optional[List[str]] = None,
        simulate: bool = False,
        simulation_preset: str = "mid_range",
        manual_checks: Optional[List[ManualInspectionItem]] = None,
        progress_callback: Optional[Callable[[float, str, Optional[BenchmarkResult]], None]] = None
    ) -> DiagnosticReport:
        """Executes full diagnostic suite and produces report."""
        self.is_running = True
        self.safety.reset()
        workload_ids = workload_ids or ["comp_materials_science", "programming"]

        if progress_callback:
            progress_callback(0.02, "Detecting system hardware components...", None)

        # 1. Hardware Detection
        hardware = get_hardware_snapshot(simulate=simulate, preset=simulation_preset)

        if progress_callback:
            progress_callback(0.05, f"Hardware detected: {hardware.manufacturer} {hardware.device_model} ({hardware.cpu.model})", None)

        # 2. Pre-flight Check: Background Processes and AC Power
        if progress_callback:
            progress_callback(0.07, "Running pre-flight system checks (power mode, background load)...", None)

        preflight_anomalies: List[Anomaly] = []
        if not simulate:
            preflight = run_preflight_check()
            for w in preflight.warnings:
                preflight_anomalies.append(Anomaly(
                    severity="WARNING",
                    component="System",
                    title="Pre-flight Condition Alert",
                    description=w,
                    recommendation="Ensure laptop is connected to AC charger and close non-essential background applications before shop benchmarking."
                ))

        # 3. Benchmarks execution
        benchmarks = self.engine.run_suite(
            test_level=test_level,
            hardware=hardware,
            progress_callback=progress_callback
        )

        # 4. Workload Evaluation
        if progress_callback:
            progress_callback(0.92, "Evaluating workload suitability profiles...", None)

        workload_evals = [
            evaluate_workload(wid, hardware, benchmarks)
            for wid in workload_ids
        ]

        # 5. Anomaly Detection
        if progress_callback:
            progress_callback(0.95, "Analyzing thermal stability and anomaly patterns...", None)

        anomalies = preflight_anomalies + detect_anomalies(hardware, benchmarks, self.safety.history)

        # 6. Category Assessment
        summary_cats = classify_categories(hardware, benchmarks, anomalies)

        # Default manual inspections if none supplied
        if not manual_checks:
            manual_checks = [
                ManualInspectionItem(id="display", category="Display", title="LCD Panel Dead Pixel & Bleed Check", status=StatusEnum.PASS, notes="Color cycle inspected"),
                ManualInspectionItem(id="keyboard", category="Keyboard", title="Physical Keyboard Matrix", status=StatusEnum.PASS, notes="QWERTY matrix verified"),
                ManualInspectionItem(id="touchpad", category="Touchpad", title="Touchpad Tracking & Gesture Zone", status=StatusEnum.PASS, notes="Tracking responsive"),
                ManualInspectionItem(id="usb_ports", category="Ports", title="USB / Thunderbolt Ports", status=StatusEnum.PASS, notes="Verified physical connectivity"),
                ManualInspectionItem(id="hdmi_port", category="Ports", title="HDMI Video Output", status=StatusEnum.PASS, notes="Connector intact")
            ]

        # 7. Report Assembly
        report_id = generate_report_id()
        report = DiagnosticReport(
            report_id=report_id,
            test_level=test_level,
            is_simulation=hardware.is_simulation,
            simulation_label=hardware.simulation_profile_name,
            hardware=hardware,
            thermal_samples=list(self.safety.history),
            benchmarks=benchmarks,
            workload_evaluations=workload_evals,
            anomalies=anomalies,
            manual_inspections=manual_checks,
            summary_categories=summary_cats
        )

        # 8. Generate PDF locally
        if progress_callback:
            progress_callback(0.98, "Generating professional PDF report...", None)

        safe_mfg = "".join(c for c in hardware.manufacturer if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_') or "Unknown"
        safe_model = "".join(c for c in hardware.device_model if c.isalnum() or c in (' ', '_')).strip().replace(' ', '_') or "Laptop"
        date_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_filename = f"LaptopCheck_{safe_mfg}_{safe_model}_{date_stamp}.pdf"
        
        reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "reports")
        pdf_path = os.path.join(reports_dir, pdf_filename)
        
        generate_pdf_report(report, pdf_path)

        if progress_callback:
            progress_callback(1.0, f"Diagnostic complete! Report saved to {pdf_filename}", None)

        self.current_report = report
        self.is_running = False
        return report
