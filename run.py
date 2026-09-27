#!/usr/bin/env python3
"""LaptopCheck - Laptop Diagnostic & Workload Suitability Analyzer.
Entry point for CLI diagnostics or local web application server.

Usage:
  python run.py                      # Starts the local Web Application on http://localhost:8000
  python run.py --cli                # Runs diagnostic in Terminal CLI mode and generates PDF
  python run.py --cli --simulate     # Runs simulation diagnostic in Terminal CLI mode
  python run.py --port 8080          # Custom port for web UI
"""
import sys
import os
import argparse
import webbrowser

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

def run_cli_diagnostic(args):
    from agent.runner import DiagnosticRunner
    print("=" * 65)
    print("  LaptopCheck - Hardware Diagnostic & Workload Analyzer")
    print("=" * 65)
    
    if args.simulate:
        print(f"[*] Running in SIMULATION MODE (Preset: {args.preset})")
    else:
        print("[*] Running in REAL HARDWARE MODE")

    runner = DiagnosticRunner()

    def on_progress(pct, msg, bench_res):
        bars = int(pct * 30)
        progress_bar = f"[{'#' * bars}{'.' * (30 - bars)}]"
        print(f"\r{progress_bar} {int(pct*100):3d}% | {msg[:35]:<35}", end="", flush=True)

    print("\nStarting diagnostic suite...")
    report = runner.run_diagnostic(
        test_level=args.test_level,
        workload_ids=[args.workload, "programming"],
        simulate=args.simulate,
        simulation_preset=args.preset,
        progress_callback=on_progress
    )
    print("\n" + "=" * 65)
    print(f"REPORT ID: {report.report_id}")
    print(f"MACHINE:   {report.hardware.manufacturer} {report.hardware.device_model}")
    print(f"OS:        {report.hardware.os.system} {report.hardware.os.release}")
    print(f"CPU:       {report.hardware.cpu.model} ({report.hardware.cpu.cores_physical}C/{report.hardware.cpu.threads_logical}T)")
    print(f"RAM:       {report.hardware.ram.total_gb} GB ({report.hardware.ram.channels})")
    print("=" * 65)
    print("EXECUTIVE COMPONENT MATRIX:")
    for cat, status in report.summary_categories.items():
        print(f"  {cat:<14}: {status.value}")
    print("-" * 65)
    print(f"WORKLOAD SUITABILITY: {report.workload_evaluations[0].profile_name}")
    print(f"  VERDICT: {report.workload_evaluations[0].overall_status.value}")
    print(f"  SUMMARY: {report.workload_evaluations[0].suitability_summary}")
    print("=" * 65)
    if report.anomalies:
        print("KEY OBSERVATIONS / ANOMALIES:")
        for a in report.anomalies:
            print(f"  [{a.severity}] {a.title}: {a.description}")
            print(f"         Recommendation: {a.recommendation}")
    else:
        print("  ✅ No significant hardware anomalies detected.")
    print("=" * 65)

def run_web_server(args):
    import uvicorn
    host = args.host
    port = args.port
    print("=" * 65)
    print(f"  LaptopCheck Web UI Server launching at http://{host}:{port}")
    print("=" * 65)
    
    if args.open_browser:
        try:
            webbrowser.open(f"http://localhost:{port}")
        except Exception:
            pass

    uvicorn.run("web.backend.main:app", host=host, port=port, reload=False)

def main():
    parser = argparse.ArgumentParser(description="LaptopCheck Diagnostic & Workload Analyzer")
    parser.add_argument("--cli", action="store_true", help="Run in Terminal CLI mode without web server")
    parser.add_argument("--simulate", action="store_true", help="Run with simulated hardware profile")
    parser.add_argument("--preset", default="mid_range", choices=["low_end", "mid_range", "high_performance", "thermally_limited", "battery_degraded", "storage_warning"], help="Simulation preset profile")
    parser.add_argument("--workload", default="comp_materials_science", help="Target workload profile ID")
    parser.add_argument("--test-level", default="Quick / Shop Safe", help="Test level: 'Quick / Shop Safe', 'Standard', 'Extended'")
    parser.add_argument("--host", default="0.0.0.0", help="Web server host")
    parser.add_argument("--port", type=int, default=8000, help="Web server port")
    parser.add_argument("--open-browser", action="store_true", help="Automatically open default browser")

    args = parser.parse_args()

    if args.cli:
        run_cli_diagnostic(args)
    else:
        run_web_server(args)

if __name__ == "__main__":
    main()
