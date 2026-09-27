"""FastAPI REST API Server for LaptopCheck.
Exposes hardware inspection, test runner controls, live sensor streaming,
workload suitability profiles, and PDF report downloads.
"""
import os
import glob
import threading
import time
from datetime import datetime
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from agent import __version__
from agent.models import (
    SystemHardwareSnapshot, DiagnosticReport, ManualInspectionItem, StatusEnum
)
from agent.hardware.manager import get_hardware_snapshot, list_simulation_presets
from agent.workloads.profiles import list_workload_profiles
from agent.runner import DiagnosticRunner

app = FastAPI(
    title="LaptopCheck Diagnostic API",
    version=__version__,
    description="Laptop Diagnostic & Workload Suitability Analyzer REST API"
)

# Enable CORS for local web interface
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global test state
ACTIVE_RUNNER: Optional[DiagnosticRunner] = None
TEST_STATE = {
    "is_running": False,
    "progress": 0.0,
    "current_stage": "Idle",
    "elapsed_secs": 0.0,
    "safety_level": "NORMAL",
    "latest_report": None,
    "error": None
}
STATE_LOCK = threading.Lock()

class StartTestRequest(BaseModel):
    test_level: str = "Quick / Shop Safe"
    workload_ids: List[str] = ["comp_materials_science", "programming"]
    simulate: bool = False
    simulation_preset: str = "mid_range"
    manual_checks: Optional[List[ManualInspectionItem]] = None

@app.get("/api/health")
def get_health():
    return {
        "status": "healthy",
        "service": "LaptopCheck Diagnostic Engine",
        "version": __version__
    }

@app.get("/api/hardware", response_model=SystemHardwareSnapshot)
def get_hardware(simulate: bool = False, preset: str = "mid_range"):
    """Returns detected hardware inventory or simulated laptop profile."""
    return get_hardware_snapshot(simulate=simulate, preset=preset)

@app.get("/api/simulation/presets")
def get_simulation_presets():
    """Lists available simulated laptop machines."""
    return list_simulation_presets()

@app.get("/api/profiles")
def get_profiles():
    """Lists workload profiles (Computational Materials Science, etc.)."""
    return list_workload_profiles()

@app.get("/api/test-runs/active")
def get_active_test_status():
    """Polls real-time test progress and live sensor readings."""
    with STATE_LOCK:
        status = dict(TEST_STATE)
        if ACTIVE_RUNNER and ACTIVE_RUNNER.safety.history:
            recent_sample = ACTIVE_RUNNER.safety.history[-1]
            status["latest_sample"] = recent_sample.model_dump()
            status["samples_count"] = len(ACTIVE_RUNNER.safety.history)
            status["safety_level"] = ACTIVE_RUNNER.safety.get_current_level().value
        return status

def _run_test_worker(req: StartTestRequest):
    global ACTIVE_RUNNER
    runner = DiagnosticRunner()
    ACTIVE_RUNNER = runner
    start_t = time.time()

    def on_progress(pct: float, msg: str, bench_res):
        with STATE_LOCK:
            TEST_STATE["progress"] = round(pct, 2)
            TEST_STATE["current_stage"] = msg
            TEST_STATE["elapsed_secs"] = round(time.time() - start_t, 1)

    try:
        report = runner.run_diagnostic(
            test_level=req.test_level,
            workload_ids=req.workload_ids,
            simulate=req.simulate,
            simulation_preset=req.simulation_preset,
            manual_checks=req.manual_checks,
            progress_callback=on_progress
        )
        with STATE_LOCK:
            TEST_STATE["latest_report"] = report.model_dump()
            TEST_STATE["is_running"] = False
            TEST_STATE["current_stage"] = "Diagnostic Finished"
            TEST_STATE["progress"] = 1.0
    except Exception as e:
        with STATE_LOCK:
            TEST_STATE["is_running"] = False
            TEST_STATE["error"] = str(e)
            TEST_STATE["current_stage"] = f"Error: {str(e)}"

@app.post("/api/test-runs")
def start_test(req: StartTestRequest, background_tasks: BackgroundTasks):
    """Starts a new diagnostic test run in the background."""
    with STATE_LOCK:
        if TEST_STATE["is_running"]:
            raise HTTPException(status_code=400, detail="A diagnostic test is already running.")
        TEST_STATE["is_running"] = True
        TEST_STATE["progress"] = 0.01
        TEST_STATE["current_stage"] = "Initializing diagnostic suite..."
        TEST_STATE["elapsed_secs"] = 0.0
        TEST_STATE["error"] = None

    background_tasks.add_task(_run_test_worker, req)
    return {"message": "Test initiated", "parameters": req.model_dump()}

@app.post("/api/test-runs/stop")
def stop_test():
    """Immediately stops active benchmark execution."""
    if ACTIVE_RUNNER:
        ACTIVE_RUNNER.stop_current_test()
    with STATE_LOCK:
        TEST_STATE["is_running"] = False
        TEST_STATE["current_stage"] = "Test stopped by user"
    return {"message": "Test aborted by user request."}

@app.get("/api/reports")
def list_reports():
    """Lists generated report PDFs."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")
    if not os.path.exists(reports_dir):
        return []
    files = glob.glob(os.path.join(reports_dir, "*.pdf"))
    res = []
    for f in sorted(files, key=os.path.getmtime, reverse=True):
        basename = os.path.basename(f)
        size_kb = round(os.path.getsize(f) / 1024, 1)
        mtime = datetime.fromtimestamp(os.path.getmtime(f)).strftime("%Y-%m-%d %H:%M:%S")
        res.append({
            "filename": basename,
            "size_kb": size_kb,
            "created_at": mtime
        })
    return res

@app.get("/api/reports/download/{filename}")
def download_pdf(filename: str):
    """Downloads a specific PDF report."""
    reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "reports")
    # Sanitize filename
    clean_name = os.path.basename(filename)
    filepath = os.path.join(reports_dir, clean_name)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Report PDF not found.")
    return FileResponse(filepath, media_type="application/pdf", filename=clean_name)

# Mount compiled frontend dist if available
dist_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(dist_dir):
    app.mount("/", StaticFiles(directory=dist_dir, html=True), name="static_frontend")
