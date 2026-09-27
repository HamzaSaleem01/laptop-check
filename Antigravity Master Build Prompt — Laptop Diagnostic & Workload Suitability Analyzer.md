# MASTER BUILD PROMPT
## Laptop Diagnostic & Workload Suitability Analyzer

You are the lead software architect, senior full-stack developer, systems programmer, QA engineer, and UI/UX engineer for this project.

Your task is to **design, implement, test, debug, and package a fully functional laptop diagnostic application**, not a mockup, static demo, proof of concept, or collection of placeholder screens.

The final application must be capable of being used in a real laptop shop to inspect a Windows or Linux laptop, detect its hardware, safely perform appropriate diagnostics and benchmarks, monitor thermals and stability, compare the results against a selected workload profile, and generate a professional PDF report.

Do not stop at planning. Build the working software.

---

# 1. PRODUCT NAME

Use a temporary working name:

**LaptopCheck**

The architecture must allow the name, logo, colors, domain, and branding to be changed later.

---

# 2. CORE PURPOSE

The application must answer:

> "Is this laptop suitable for the user's intended workload, and what is the actual condition/performance of the machine?"

It must combine:

1. Hardware detection
2. Hardware health inspection
3. Performance benchmarking
4. Thermal monitoring
5. Stability testing
6. Battery health analysis
7. Storage health/performance
8. GPU analysis
9. RAM analysis
10. Workload-specific testing
11. Requirement matching
12. Anomaly detection
13. Manual hardware inspection
14. Professional PDF report generation

The application must be designed for **real-world used-laptop inspection**, especially laptops being tested temporarily at a shop.

---

# 3. CRITICAL DESIGN PRINCIPLE

Do NOT blindly run maximum-load benchmarks on every computer.

The application must first:

```text
Detect hardware
        ↓
Assess hardware capability
        ↓
Determine safe test profile
        ↓
Run controlled tests
        ↓
Monitor temperature/performance continuously
        ↓
Reduce/stop workload if necessary
        ↓
Analyze results
        ↓
Compare against requirements
        ↓
Generate report
```

Safety and system integrity are more important than obtaining a benchmark score.

---

# 4. TARGET PLATFORMS

### V1

Fully support:

- Windows 10
- Windows 11
- Ubuntu/Debian-based Linux

Architecture should make future macOS support possible, but do not compromise V1 development by attempting full macOS support immediately.

The application must detect the operating system automatically.

---

# 5. APPLICATION ARCHITECTURE

Build the project as a modular system.

Recommended architecture:

```text
LaptopCheck/
│
├── web/
│   ├── frontend/
│   └── backend/
│
├── agent/
│   ├── hardware/
│   ├── monitoring/
│   ├── benchmarks/
│   ├── diagnostics/
│   ├── safety/
│   ├── workloads/
│   └── reporting/
│
├── profiles/
│
├── tests/
│
├── docs/
│
└── deployment/
```

Recommended technologies:

### Frontend
React + TypeScript

### Backend
Python + FastAPI

### Local diagnostic agent
Python initially.

Design the agent with clear interfaces so that low-level components can later be replaced with Rust or native implementations where necessary.

### Database
PostgreSQL for cloud functionality.

However, the diagnostic agent must work locally without requiring a database or internet connection.

### PDF
ReportLab or another reliable Python PDF library.

### Packaging
Use PyInstaller or an equivalent reliable packaging system for Windows.

For Linux provide an AppImage or similarly convenient executable/package where practical.

---

# 6. TWO-PART SYSTEM

The product must have:

## A. Web Application

Used for:

- choosing workload
- defining requirements
- downloading the diagnostic agent
- viewing uploaded reports
- comparing laptops
- managing profiles
- viewing historical tests

## B. Local Diagnostic Agent

This is the most important component.

The agent must:

- run locally
- collect hardware information
- run diagnostics
- run benchmarks
- monitor hardware
- enforce safety limits
- generate results
- generate a PDF locally
- work without internet

The core diagnostic process must NOT depend on cloud connectivity.

---

# 7. FIRST-RUN USER EXPERIENCE

When the application starts, show a very simple interface:

# LaptopCheck

### What do you want to check?

Buttons:

- Quick Laptop Inspection
- Full Diagnostic
- Custom Test
- Compare Previous Report
- Settings

For first-time users, make **Quick Laptop Inspection** the default.

---

# 8. WORKLOAD SELECTION

Before testing, provide:

### "What will you use this laptop for?"

Profiles:

- General Productivity
- Programming
- Computational Materials Science
- Scientific Computing
- AI / Machine Learning
- Engineering / CAD
- Gaming
- Video Editing
- Data Science
- Student / University
- Custom

Allow multiple profiles.

---

# 9. COMPUTATIONAL MATERIALS SCIENCE PROFILE

Create a detailed built-in profile for:

**Computational Materials Science / Physics**

Prioritize:

### Very High

- CPU multi-core performance
- sustained CPU performance
- RAM capacity
- RAM bandwidth
- thermal stability

### High

- SSD speed
- SSD health
- Linux compatibility
- CPU instruction-set support

### Medium

- GPU

### Lower priority

- display refresh rate
- gaming GPU performance

Include workload examples:

- Density Functional Theory
- Quantum ESPRESSO
- Python
- NumPy
- SciPy
- ASE
- data analysis
- VESTA
- scientific computing
- HPC preparation

Do not claim that a benchmark directly predicts real DFT performance unless the benchmark actually measures the relevant workload.

---

# 10. CUSTOM REQUIREMENTS

Allow the user to define:

```text
Minimum CPU cores
Minimum RAM
Minimum storage
Minimum GPU VRAM
Minimum CPU performance
Minimum RAM bandwidth
Minimum SSD performance
Maximum acceptable temperature
Minimum battery health
Required operating system
Required GPU
```

Each requirement must support:

- minimum
- preferred
- optional
- not required

---

# 11. HARDWARE DETECTION

Automatically detect as much as reliably available.

## CPU

Collect:

- manufacturer
- model
- architecture
- generation where identifiable
- cores
- performance cores
- efficiency cores
- threads
- base frequency
- maximum frequency
- current frequency
- cache
- instruction sets
- virtualization support
- CPU utilization
- temperature where available
- power information where available

## RAM

Collect:

- total capacity
- available capacity
- used capacity
- type
- speed
- modules
- channel configuration
- memory bandwidth where measurable

## GPU

Collect:

- manufacturer
- model
- integrated/dedicated
- VRAM
- driver
- utilization
- temperature
- power where available
- PCIe information where available

## Storage

Collect:

- manufacturer
- model
- capacity
- HDD/SATA SSD/NVMe
- interface
- temperature
- SMART health
- power-on hours
- wear/life information where available

## Battery

Collect:

- design capacity
- full charge capacity
- current charge
- cycle count
- battery health
- charging status
- temperature where available

## OS

Collect:

- OS
- version
- architecture
- kernel version on Linux
- major driver information

---

# 12. HARDWARE DETECTION FALLBACKS

Never make the entire application fail because one hardware property is unavailable.

Use:

```text
AVAILABLE
NOT AVAILABLE
NOT SUPPORTED
REQUIRES MANUAL CHECK
```

Do not invent values.

For example:

```text
CPU Temperature: Not available
```

is preferable to an incorrect value.

---

# 13. STORAGE SAFETY

Storage benchmarks must NEVER perform destructive testing by default.

Do not:

- erase drives
- format drives
- overwrite the entire disk
- modify partitions
- alter firmware

Use controlled temporary test files.

Make it clear when a test writes data.

Provide:

### Safe Storage Test

Small controlled read/write test.

### Extended Storage Test

Optional and explicitly confirmed by the user.

---

# 14. BENCHMARK ENGINE

Create a modular benchmark engine.

Architecture:

```text
BenchmarkEngine
│
├── CPUBenchmark
├── MemoryBenchmark
├── StorageBenchmark
├── GPUBenchmark
├── PythonBenchmark
├── ScientificBenchmark
└── QEBenchmark
```

Every benchmark must expose:

```text
prepare()
run()
monitor()
stop()
cleanup()
analyze()
```

---

# 15. THREE TEST LEVELS

## Level 1 — QUICK / SHOP SAFE

Target:

5 minutes or less.

Tests:

- hardware detection
- CPU short test
- RAM test
- SSD health
- small SSD benchmark
- GPU short test where relevant
- battery
- thermal monitoring

This should be the default.

---

## Level 2 — STANDARD

Target:

10–20 minutes.

Adds:

- sustained CPU
- RAM bandwidth
- GPU workload
- storage performance
- thermal stability
- throttling analysis

---

## Level 3 — EXTENDED

Target:

30–60+ minutes.

Adds:

- sustained CPU
- sustained GPU
- combined CPU/GPU
- prolonged thermal monitoring
- performance degradation analysis

Before starting Extended mode, display a clear warning and require user confirmation.

---

# 16. SAFETY CONTROLLER

Implement a dedicated SafetyController.

It must monitor:

- CPU temperature
- GPU temperature
- battery temperature
- CPU frequency
- GPU frequency
- utilization
- power where available
- test duration
- system responsiveness

The safety controller must support:

```text
NORMAL
WARNING
REDUCE LOAD
PAUSE
STOP
```

Example:

```text
Normal temperature
        ↓
Continue

Temperature approaching configured threshold
        ↓
Warning

Temperature continues rising
        ↓
Reduce workload

Temperature reaches emergency threshold
        ↓
Stop test
```

Do NOT invent unsafe universal temperature limits.

Use conservative platform-specific limits where reliable information exists, otherwise use configurable conservative defaults and clearly label them.

The test must always be stoppable by the user.

---

# 17. THERMAL ANALYSIS

Record time-series data:

```text
timestamp
CPU temperature
GPU temperature
CPU frequency
GPU frequency
CPU utilization
GPU utilization
power if available
```

Calculate:

- idle temperature
- peak temperature
- average temperature
- sustained temperature
- sustained frequency
- performance degradation
- possible thermal throttling

Do not diagnose physical faults with certainty.

Use wording such as:

> "Possible thermal limitation detected."

rather than:

> "Thermal paste is bad."

---

# 18. PERFORMANCE DEGRADATION

This is important.

Compare:

```text
Initial performance
vs
Sustained performance
```

Example:

```text
Short CPU performance: 100%
Sustained performance: 78%

Observed degradation: 22%
```

Investigate whether degradation correlates with:

- temperature
- frequency reduction
- power limitation
- thermal throttling

---

# 19. BATTERY ANALYSIS

Calculate:

```text
Battery Health =
Full Charge Capacity / Design Capacity × 100
```

Show:

- health percentage
- cycle count
- capacity loss
- charging status

Do not call a battery "bad" solely based on an arbitrary percentage. Use categories such as:

```text
Healthy
Reduced Capacity
Significantly Reduced
Unable to Determine
```

---

# 20. SSD HEALTH

Read SMART/NVMe health information where supported.

Show:

- health
- temperature
- power-on hours
- wear
- error indicators
- capacity
- performance

If SMART cannot be accessed:

```text
SMART: Unable to determine
```

Do not infer health from benchmark speed alone.

---

# 21. DISPLAY TEST

Add a manual display test.

Full-screen:

- black
- white
- red
- green
- blue
- gray

Instructions:

> Inspect the screen for dead pixels, stuck pixels, lines, flickering, uneven backlight, or visible damage.

The user should be able to record:

```text
Display:
PASS
PASS WITH OBSERVATION
FAIL
SKIPPED
```

---

# 22. KEYBOARD TEST

Create an interactive keyboard tester.

Display a keyboard layout appropriate to the detected keyboard where possible.

Track pressed keys.

Allow:

```text
PASS
FAILED KEYS
SKIPPED
```

Record failed keys manually if necessary.

---

# 23. TOUCHPAD TEST

Manual test interface for:

- cursor movement
- left click
- right click
- scrolling
- multitouch

Record result.

---

# 24. PORT TESTING

Automatically detect what is possible.

For physical ports that cannot be electronically verified, create a manual checklist:

```text
USB-A
USB-C
HDMI
DisplayPort
Ethernet
Audio jack
SD card
```

Allow:

```text
PASS
FAIL
NOT TESTED
```

---

# 25. NETWORK TEST

Check:

- Wi-Fi adapter
- Bluetooth
- Ethernet adapter
- negotiated link speed where available
- signal information where available

Do not require internet connectivity.

Internet speed testing should be optional.

---

# 26. BACKGROUND PROCESS ANALYSIS

Before benchmarks:

measure background CPU/RAM usage.

Warn if:

```text
High CPU background usage
High RAM usage
Windows update running
Antivirus scan running
Heavy background process detected
```

Do not terminate arbitrary user processes.

Show the user what may be affecting benchmark accuracy.

---

# 27. POWER MODE

Detect the current power profile.

Show:

```text
Battery
Balanced
Performance
High Performance
```

Do not silently modify the user's power settings.

Offer:

> "For more representative performance results, connect the laptop to AC power."

For shop testing, default to AC-powered testing where possible.

---

# 28. SCIENTIFIC BENCHMARK

Create controlled scientific workloads:

- matrix operations
- FFT
- NumPy
- SciPy
- BLAS
- memory-intensive calculations
- multithreaded numerical workload

Measure:

- execution time
- CPU utilization
- memory usage
- throughput

---

# 29. QUANTUM ESPRESSO BENCHMARK

Design an optional Quantum ESPRESSO benchmark plugin.

Do not assume Quantum ESPRESSO is installed.

Provide:

```text
QE Benchmark Available
QE Not Installed
QE Test Package Not Available
```

If the benchmark package is included, use a small standardized test case.

Measure:

- total runtime
- CPU utilization
- memory usage
- SCF iterations
- elapsed time

Do not run huge calculations on shop laptops.

The QE benchmark must be optional.

---

# 30. RESULT CLASSIFICATION

Every requirement should produce one of:

```text
PASS
CAUTION
FAIL
NOT AVAILABLE
NOT TESTED
```

Do not use a single arbitrary universal laptop score as the primary result.

Instead show category results:

```text
CPU
RAM
Storage
GPU
Thermals
Battery
Stability
Workload Compatibility
```

---

# 31. ANOMALY DETECTION

Detect potential anomalies such as:

- unusually high idle CPU usage
- unusually high idle temperature
- thermal throttling
- significant sustained-performance drop
- SSD health warnings
- battery degradation
- abnormal memory configuration
- GPU driver problems
- missing hardware information
- excessive background processes
- benchmark instability
- unexpected shutdown/restart during testing

Phrase findings carefully.

Example:

```text
Potential thermal limitation detected.

The CPU temperature increased substantially during
the sustained test and CPU frequency decreased.

Possible causes include thermal or power limitations.
Further physical inspection is recommended.
```

---

# 32. REPORT GENERATION

Generate a professional PDF locally.

Filename:

```text
LaptopCheck_<Manufacturer>_<Model>_<Date>.pdf
```

Include:

## Page 1

- Laptop model
- OS
- CPU
- RAM
- GPU
- Storage
- battery
- test date/time
- report ID

## Page 2+

Detailed results.

Include:

- tables
- graphs
- thermal curves
- performance curves
- battery information
- storage health
- benchmark results
- workload compatibility
- anomalies
- manual inspection results

---

# 33. EXECUTIVE SUMMARY

The first report page must contain an easy-to-understand summary.

Example:

```text
SYSTEM OVERVIEW

CPU                 PASS
RAM                 PASS
Storage             PASS
GPU                 PASS
Thermals             CAUTION
Battery              CAUTION
Stability            PASS

WORKLOAD PROFILE

Computational Materials Science

CPU                  PASS
RAM                  PASS
Storage              PASS
Sustained Performance CAUTION
```

Then list the important findings.

---

# 34. REPORT TRACEABILITY

Every result should record:

```text
test name
test version
software version
timestamp
duration
hardware detected
test configuration
result
```

This makes reports reproducible.

---

# 35. UNIQUE REPORT ID

Generate something like:

```text
LC-2026-09-27-A7F92K
```

Include it in the PDF.

---

# 36. LOCAL-FIRST PRIVACY

Default behavior:

- no account
- no cloud upload
- no personal files accessed
- no browser history
- no passwords
- no microphone
- no camera
- no document scanning

Only collect information required for diagnostics.

The report is generated locally.

Cloud upload must be optional.

---

# 37. CLOUD PLATFORM

Later support:

```text
User account
Saved reports
Report sharing
Laptop comparison
Workload profiles
Custom requirements
```

Use PostgreSQL.

Never make cloud connectivity a requirement for basic diagnostics.

---

# 38. USER INTERFACE

The interface must be extremely simple.

Design principle:

> A person standing in a laptop shop should understand what to click without technical knowledge.

Use:

- large buttons
- clear progress indicators
- simple language
- status icons
- PASS / CAUTION / FAIL
- expandable technical details

Avoid overwhelming users with raw sensor data by default.

Provide:

### Simple View

and

### Technical View

---

# 39. TEST PROGRESS

During testing show:

```text
LaptopCheck

Detecting hardware        ✓
Checking storage          ✓
Testing memory            ✓
Testing CPU               ●
Monitoring thermals       ●

Estimated time remaining: 02:31
```

Show temperature and major safety information live.

Always provide:

**STOP TEST**

---

# 40. ERROR HANDLING

Never crash the complete application because one test fails.

Example:

```text
GPU temperature unavailable
```

should not prevent:

- CPU testing
- RAM testing
- storage testing
- report generation

The report should say:

```text
GPU temperature: unavailable on this system
```

---

# 41. OFFLINE MODE

The diagnostic agent must continue functioning without internet.

The complete basic workflow must be:

```text
Download
↓
Run
↓
Detect
↓
Test
↓
Analyze
↓
Generate PDF
```

without internet.

---

# 42. SECURITY

The agent must:

- request only necessary permissions
- never execute downloaded arbitrary code
- never modify BIOS/firmware
- never modify partitions
- never disable antivirus
- never bypass OS security
- never collect credentials
- never upload files automatically

The software should be code-signed for production Windows distribution when the project reaches release stage.

---

# 43. ANTIVIRUS COMPATIBILITY

Assume the user may have antivirus software installed.

Do NOT instruct the application to disable antivirus.

Avoid unnecessary privileged operations.

If a benchmark requires elevated permissions, clearly explain why and provide a non-admin fallback where possible.

---

# 44. DATABASE DESIGN

Create schemas for:

```text
users
devices
hardware_snapshots
test_runs
benchmark_results
thermal_samples
battery_results
storage_results
workload_profiles
requirements
reports
```

Do not store sensitive personal data unnecessarily.

---

# 45. API DESIGN

Create clean REST endpoints such as:

```text
GET  /api/health
GET  /api/profiles
POST /api/test-runs
POST /api/results
GET  /api/reports/{id}
POST /api/reports
```

Use proper validation.

Generate OpenAPI documentation automatically through FastAPI.

---

# 46. CONFIGURATION

All configurable values must be externalized.

Examples:

```text
test durations
temperature thresholds
benchmark sizes
storage test sizes
workload requirements
report settings
```

Do not hard-code important values throughout the application.

---

# 47. TESTING REQUIREMENTS

Write automated tests.

At minimum:

### Unit tests

- hardware parsing
- requirement matching
- battery calculation
- benchmark result processing
- thermal analysis
- report generation

### Integration tests

- complete diagnostic run
- report generation
- API communication

### Safety tests

- temperature threshold behavior
- manual stop
- timeout
- benchmark failure
- unavailable sensors

---

# 48. SIMULATION MODE

This is mandatory for development.

Create:

**Demo / Simulation Mode**

It should simulate:

- CPU
- RAM
- GPU
- storage
- battery
- temperatures
- benchmark results

This allows the complete UI and report workflow to be tested without repeatedly running heavy benchmarks.

Provide several simulated machines:

```text
Low-end laptop
Mid-range laptop
High-performance laptop
Thermally limited laptop
Battery-degraded laptop
Storage-warning laptop
```

---

# 49. HARDWARE ABSTRACTION

Do not tightly couple UI code to Windows-specific commands.

Use interfaces:

```text
HardwareProvider
WindowsHardwareProvider
LinuxHardwareProvider
```

Similarly:

```text
TemperatureProvider
BatteryProvider
StorageHealthProvider
GPUProvider
```

This is essential for cross-platform support.

---

# 50. LOGGING

Create structured logs.

Never log:

- passwords
- personal files
- private document content
- browser history

Logs should help diagnose application failures.

Provide:

```text
Export Diagnostic Log
```

for troubleshooting.

---

# 51. PACKAGING

Produce:

### Windows

A simple executable:

```text
LaptopCheck.exe
```

or installer.

The user should not need to manually install Python.

### Linux

Provide a convenient executable/package.

Document installation clearly.

---

# 52. WEB DOWNLOAD FLOW

The website should eventually provide:

```text
Download for Windows
Download for Linux
```

Automatically select the correct version where possible.

---

# 53. VERSIONING

Use semantic versioning:

```text
0.1.0
0.2.0
1.0.0
```

The report must include the LaptopCheck version.

---

# 54. DEVELOPMENT WORKFLOW

Follow this order:

## Stage 1

Build project skeleton.

## Stage 2

Implement hardware detection.

## Stage 3

Implement local diagnostic engine.

## Stage 4

Implement safety controller.

## Stage 5

Implement benchmark engine.

## Stage 6

Implement workload profiles.

## Stage 7

Implement analysis engine.

## Stage 8

Implement PDF reporting.

## Stage 9

Implement web interface.

## Stage 10

Implement cloud/report management.

## Stage 11

Package Windows/Linux applications.

## Stage 12

Run complete QA.

Do not skip testing.

---

# 55. DEVELOPMENT RULE

Do not simply create placeholders such as:

```text
TODO
Coming soon
Mock result
Fake benchmark
Placeholder report
```

for core functionality.

If a feature cannot yet be implemented safely on a platform, implement a proper:

```text
NOT AVAILABLE
```

state with an explanation.

---

# 56. NO FAKE DATA

Never present simulated data as real hardware data.

Simulation mode must be visibly labelled:

```text
SIMULATION MODE
```

Real hardware mode must use actual system information.

---

# 57. PERFORMANCE

The application itself should have minimal overhead.

The diagnostic agent should not consume excessive RAM/CPU before testing.

Avoid unnecessary background services.

Do not keep continuous monitoring active when no test is running.

---

# 58. ACCESSIBILITY

Support:

- readable fonts
- keyboard navigation
- clear contrast
- clear status indicators
- no information conveyed only through color

---

# 59. REPORT DESIGN

The PDF must look professional enough to send to:

- a laptop buyer
- seller
- company
- technician
- researcher

Use:

- clean typography
- tables
- graphs
- clear sections
- timestamps
- software version
- report ID

---

# 60. FINAL USER WORKFLOW

The complete intended workflow is:

```text
OPEN WEBSITE
      ↓
SELECT "LAPTOP INSPECTION"
      ↓
DOWNLOAD AGENT
      ↓
RUN AGENT
      ↓
HARDWARE DETECTION
      ↓
SELECT WORKLOAD
      ↓
SELECT TEST LEVEL
      ↓
SAFETY CHECK
      ↓
START TEST
      ↓
MONITOR SYSTEM
      ↓
RUN APPROPRIATE TESTS
      ↓
ANALYZE RESULTS
      ↓
COMPARE REQUIREMENTS
      ↓
MANUAL INSPECTION
      ↓
FINAL RESULTS
      ↓
GENERATE PDF
      ↓
SAVE / SHARE REPORT
```

---

# 61. IMPORTANT: BUILD, DON'T JUST EXPLAIN

Do not respond to this specification with another theoretical roadmap.

Start implementing the project.

First:

1. Inspect the development environment.
2. Create the project structure.
3. Initialize the frontend.
4. Initialize the backend.
5. Initialize the local diagnostic agent.
6. Implement the first hardware detection modules.
7. Implement Simulation Mode.
8. Build the first working end-to-end workflow.
9. Run tests.
10. Fix errors.
11. Continue implementation module by module.

At every stage, keep the application runnable.

---

# 62. ACCEPTANCE CRITERIA

The project is considered functionally complete only when a user can:

### On Windows

```text
Run LaptopCheck
↓
Detect actual laptop hardware
↓
Select Computational Materials Science
↓
Run Quick Diagnostic
↓
Monitor temperatures
↓
Run CPU/RAM/storage/GPU tests where supported
↓
Analyze results
↓
See PASS/CAUTION/FAIL
↓
Generate a PDF
```

### On Linux

The equivalent workflow must work using the Linux hardware providers.

### Offline

The diagnostic workflow must work without internet.

### Failure handling

If one sensor or benchmark is unavailable, the rest of the diagnostic must continue.

### Safety

The user can always stop a running test.

### Report

The PDF must contain actual measured values and clearly distinguish unavailable values.

---

# 63. DEVELOPMENT PRIORITY

Prioritize:

1. Correctness
2. Safety
3. Reliability
4. Cross-platform architecture
5. Useful diagnostics
6. Good UX
7. Performance
8. Visual polish

Do not sacrifice safety or correctness for a flashy UI.

---

# 64. IMPORTANT ENGINEERING PRINCIPLE

When choosing between:

```text
Fast but unreliable
```

and

```text
Slightly slower but reliable
```

choose reliability.

When hardware information is unavailable:

```text
Say "Unavailable"
```

Do not guess.

When a benchmark could risk hardware:

```text
Do not run it automatically.
```

When a result is ambiguous:

```text
Report the uncertainty.
```

---

# 65. START NOW

Begin by creating the actual repository and implementing the first end-to-end vertical slice:

```text
Application startup
→ Hardware detection
→ Simulation mode
→ Workload selection
→ Quick diagnostic
→ Results dashboard
→ PDF generation
```

After that vertical slice works, expand the system module-by-module.

Do not wait for additional instructions unless you encounter a genuine technical blocker.

Keep the code clean, modular, documented, tested, and production-oriented.