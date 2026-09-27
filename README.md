# LaptopCheck — Laptop Diagnostic & Workload Suitability Analyzer

**LaptopCheck** is a professional, shop-safe laptop diagnostic, benchmark, thermal stability, and computational workload suitability analyzer built for Windows and Linux.

---

## 1. Feature Support Matrix

| Category | Status | Details |
|---|---|---|
| **Linux Native Hardware** | **SUPPORTED** | Tested natively on physical `LENOVO 82TS`. Reads `/sys/class/dmi`, `/proc/cpuinfo`, `psutil`, `lsblk`, `sysfs` power supplies, battery energy, cycle counts, NVMe composite thermals, and core temperatures. |
| **Windows Provider** | **PARTIALLY SUPPORTED** | Complete WMI/CIM/PowerShell/psutil abstraction implemented in `agent/hardware/windows_provider.py`. Safe fallbacks to `Not available`. Cannot be physically executed on host Linux environment without a Windows kernel. |
| **Simulation Mode** | **SUPPORTED** | 6 realistic presets: Low-end Budget, Mid-range ThinkPad, Workstation Precision 7780, Thermally Limited SlimBlade, Battery Degraded Latitude, and Storage Warning Compaq. Prominently labeled `SIMULATION MODE`. |
| **Safety Guardian** | **SUPPORTED** | `SafetyController` enforces continuous monitoring across `NORMAL`, `WARNING`, `REDUCE LOAD`, `PAUSE`, `STOP`. Conservative platform thresholds: CPU Emergency: 94°C, GPU Emergency: 89°C, Battery Emergency: 48°C. Immediate user `STOP TEST`. |
| **CPU Benchmark** | **SUPPORTED** | Multi-threaded workload tracking initial burst vs sustained throughput to measure observed degradation percentage from thermal/power throttling. |
| **RAM Benchmark** | **SUPPORTED** | Adaptive buffer sizing (safely restricted to ≤ 20% available RAM, never exhausting low-RAM systems) measuring read/write bandwidth in GB/s. |
| **Non-Destructive Storage** | **SUPPORTED** | Controlled temporary sequential write/read with guaranteed immediate file deletion. Never touches raw partitions or disk formatting. |
| **GPU Benchmark** | **SUPPORTED** | Dedicated NVIDIA compute execution when present; honest `NOT AVAILABLE` fallback on integrated graphics without faking scores. |
| **Scientific BLAS & FFT** | **SUPPORTED** | Double-precision dense matrix multiplication (GEMM) & 2D FFT numerical workloads. |
| **Quantum ESPRESSO Plugin** | **SUPPORTED** | Safe `pw.x` binary presence detection. Gracefully reports `QE Not Installed` when absent without breaking diagnostic suite. |
| **Workload Profiles** | **SUPPORTED** | Special emphasis on **Computational Materials Science / Physics** (evaluating DFT, Quantum ESPRESSO, ASE, VESTA, NumPy/SciPy/BLAS, physical cores, RAM bandwidth, degradation %, Linux OS). Profiles for Software Development, AI/ML, and Productivity. |
| **Pre-flight Checks** | **SUPPORTED** | Measures baseline idle CPU and RAM usage. Detects AC power connection vs battery and displays warning if disconnected. Inspects top background processes non-invasively. |
| **Manual Inspections** | **SUPPORTED** | Fullscreen dead-pixel color cycler (Black, White, Red, Green, Blue, Gray), interactive keyboard matrix tester, touchpad tracking canvas, and physical ports checklist. Embedded into PDF report. |
| **PDF Reporting** | **SUPPORTED** | Multi-page PDF report with unique traceability ID (`LC-YYYY-MM-DD-XXXXXX`), executive summary, component status matrix, embedded matplotlib thermal curve charts, and manual inspection findings. |
| **Offline Execution** | **SUPPORTED** | Completely self-contained. Performs hardware detection, benchmarks, analysis, and PDF generation with zero internet connectivity. |
| **Standalone Packaging** | **SUPPORTED** | Standalone Linux executable built with PyInstaller at `dist/LaptopCheck/LaptopCheck`. Runs out of the box without requiring Python installed. |

---

## 2. Quick Start

### A. Run the Standalone Linux Binary (No Python Required)
```bash
# Terminal CLI mode
./dist/LaptopCheck/LaptopCheck --cli

# Web UI mode (launches web server on port 8000)
./dist/LaptopCheck/LaptopCheck
```

### B. Run from Source with Virtual Environment
```bash
# 1. Start Local Web Server (serves React frontend and FastAPI REST API)
./venv/bin/python run.py

# Open http://localhost:8000 in your browser.

# 2. Run Terminal CLI Diagnostic (Real Hardware)
./venv/bin/python run.py --cli --workload comp_materials_science

# 3. Run Simulation Diagnostic
./venv/bin/python run.py --cli --simulate --preset high_performance

# 4. Run Automated Test Suite (25 Tests)
PYTHONPATH=. ./venv/bin/pytest -v tests/
```

---

## 3. Test Levels

- **Level 1 — Quick / Shop Safe (Default)**:
  - Target: < 3 minutes
  - Tests: Hardware inspection, burst CPU, RAM integrity, non-destructive temporary SSD benchmark (50MB), GPU compute inspection, battery health, thermal monitoring.
- **Level 2 — Standard**:
  - Target: 10–15 minutes
  - Adds: Sustained CPU multi-threading, RAM bandwidth, deep storage benchmarks, throttling curves.
- **Level 3 — Extended**:
  - Target: 30+ minutes
  - Adds: Prolonged thermal stress to evaluate cooling assembly, thermal paste degradation, and long-term stability.

---

## 4. Conservative Safety Thresholds

To protect customer and shop hardware from heat damage, LaptopCheck enforces conservative thresholds:
- **CPU Warning**: 80.0°C | **Reduce Load**: 88.0°C | **Emergency Cutoff**: 94.0°C
- **GPU Warning**: 78.0°C | **Reduce Load**: 84.0°C | **Emergency Cutoff**: 89.0°C
- **Battery Warning**: 40.0°C | **Emergency Cutoff**: 48.0°C
- **Sustained Degradation Warning**: > 20% drop between burst and sustained phases flags throttling.

---

## 5. Build Commands

### Build Linux Standalone Binary:
```bash
bash deployment/package_linux.sh
```
*Output: `dist/LaptopCheck/LaptopCheck`*

### Build Windows Standalone Binary:
```cmd
deployment\package_windows.bat
```
*Output: `dist\LaptopCheck\LaptopCheck.exe`*

---

## 6. Known Limitations

1. **Windows Hardware Execution**: The Windows provider (`agent/hardware/windows_provider.py`) is fully implemented with WMI/CIM/PowerShell abstractions, but physical execution was performed on Linux. On non-Windows platforms, it safely reports unprobed metrics as `Not available`.
2. **Playwright Browser Subagent**: During automated browser recording, the Playwright subagent encountered an external network driver timeout (`could not download driver from azureedge.net: 404`). The Web UI itself runs cleanly on `http://127.0.0.1:8000` and has been verified via the backend static mount and Vite build.
