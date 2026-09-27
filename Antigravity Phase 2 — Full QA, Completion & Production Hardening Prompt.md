You have completed the initial LaptopCheck implementation.

DO NOT start a new project.

DO NOT rewrite the application from scratch.

Continue working on the existing LaptopCheck repository and bring it from the current V1 implementation to a genuinely usable, fully functional release candidate.

Your previous report claimed substantial implementation and testing, but the browser-based GUI verification was not completed because the Playwright environment failed. Therefore, your next task is to perform a rigorous audit of the existing implementation, identify missing/incomplete functionality, fix it, and verify the complete application as far as the environment allows.

# PRIMARY OBJECTIVE

Turn the existing project into a reliable real-world laptop inspection application that can be taken to a laptop shop and used to inspect a machine safely.

The complete workflow must be:

START APPLICATION
→ Detect operating system
→ Detect hardware
→ Select workload
→ Select test level
→ Safety assessment
→ Run diagnostic
→ Monitor thermals
→ Run appropriate benchmarks
→ Analyze results
→ Perform manual inspection
→ Generate PDF
→ Save/export report

Do not merely make the interface look complete.

Every button and workflow must perform its intended function.

---

# 1. FIRST: AUDIT THE EXISTING PROJECT

Before modifying anything:

Inspect the entire existing repository.

Check:

- frontend
- backend
- local diagnostic agent
- hardware providers
- benchmark engine
- safety controller
- workload profiles
- reporting
- API
- tests
- simulation mode
- packaging
- documentation

Create an internal checklist of:

1. Fully implemented
2. Partially implemented
3. Placeholder
4. Broken
5. Unsafe
6. Not tested
7. Platform-specific limitation

Do not assume that because a file exists, its functionality is complete.

Inspect the actual code.

---

# 2. VERIFY REAL HARDWARE MODE

The most important requirement is REAL HARDWARE testing.

Run the application on the actual Linux host.

Verify:

- CPU detection
- RAM detection
- GPU detection
- storage detection
- battery detection
- temperatures
- OS information
- disk health where supported

Compare detected values against trusted system commands such as:

Linux:

```bash
lscpu
lsblk
lspci
free -h
cat /sys/class/dmi/id/product_name
cat /sys/class/dmi/id/sys_vendor
sensors
```

and appropriate `/sys` interfaces.

Do not blindly trust the application's own output.

If there is a discrepancy, investigate and fix it.

---

# 3. VERIFY WINDOWS PROVIDER

Inspect the Windows provider carefully.

Do not claim full Windows support unless the implementation genuinely works.

Check:

- CPU
- RAM
- GPU
- storage
- battery
- OS
- temperature availability
- SMART availability

For properties that Windows cannot reliably expose:

show:

NOT AVAILABLE

rather than fake values.

If Windows-specific code has not been executed because the current environment is Linux, explicitly document that limitation.

---

# 4. TEST SIMULATION MODE

Verify every simulation preset.

Required presets:

- Low-end
- Mid-range
- High-performance
- Thermally limited
- Battery degraded
- Storage warning

For every preset verify that:

1. Hardware information changes appropriately.
2. Benchmark results are internally consistent.
3. Workload analysis responds to the hardware.
4. Anomalies appear when expected.
5. PDF report correctly identifies simulation mode.
6. Simulation data can NEVER accidentally appear as real hardware data.

Add automated tests for all of these.

---

# 5. FRONTEND FUNCTIONALITY AUDIT

Inspect every UI button.

Every button must have a real action.

Check:

- Start Diagnostic
- Stop Test
- Workload selector
- Test-level selector
- Hardware cards
- Thermal monitor
- Display test
- Keyboard test
- Touchpad test
- Port checklist
- Report viewer
- PDF download
- Simulation mode
- Settings
- Reset
- Error states

No dead buttons.

No fake progress bars.

No hardcoded benchmark values.

No placeholder results.

---

# 6. COMPLETE END-TO-END TEST

Run the actual application.

Start:

```bash
./venv/bin/python run.py
```

Then verify:

```text
http://localhost:8000
```

Test the full user workflow.

If browser automation is unavailable, do NOT pretend it succeeded.

Instead:

1. Test API endpoints with HTTP requests.
2. Test frontend build.
3. Test JavaScript/TypeScript compilation.
4. Test backend/frontend integration.
5. Use an available browser/manual method if possible.
6. Document exactly what could and could not be verified.

---

# 7. API VERIFICATION

Test every endpoint.

Verify:

- HTTP status
- response schema
- invalid input handling
- missing data handling
- test start
- test stop
- progress
- report generation
- report retrieval
- PDF download
- hardware snapshot

No endpoint should return fake success.

---

# 8. SAFETY CONTROLLER AUDIT

This is a critical area.

Inspect the existing thermal thresholds and safety logic.

The current implementation reportedly uses:

CPU 98°C
GPU 93°C
Battery 55°C

Do NOT automatically assume these are universally safe values.

Review the safety architecture and make the thresholds:

- configurable
- documented
- conservative
- platform-aware where possible

The system must always allow:

STOP TEST

The STOP TEST action must actually terminate the active workload.

Test:

1. Normal
2. Warning
3. Reduce Load
4. Pause
5. Emergency Stop
6. Manual Stop
7. Timeout
8. Benchmark crash
9. Sensor unavailable

The application must fail safely.

---

# 9. CPU BENCHMARK AUDIT

Verify that CPU benchmark results are based on actual measured work.

Check:

- execution time
- throughput
- CPU utilization
- frequency
- temperature
- sustained performance

The benchmark must not simply generate arbitrary scores.

Separate:

SHORT BURST PERFORMANCE

from:

SUSTAINED PERFORMANCE

Calculate degradation from measured results.

---

# 10. RAM BENCHMARK AUDIT

Verify:

- memory allocation
- actual read/write operation
- measured bandwidth
- cleanup
- memory safety

Do not allocate excessive memory.

The benchmark must adapt to available RAM.

For example, a machine with 4 GB RAM must NOT attempt to allocate almost all system memory.

Leave sufficient memory for the operating system.

---

# 11. STORAGE BENCHMARK AUDIT

This is especially important.

Confirm that the default storage benchmark:

- does not destroy data
- uses temporary files
- cleans up correctly
- does not fill the disk
- does not modify partitions
- does not format anything

The user must clearly see when a write test is occurring.

Add cleanup verification tests.

---

# 12. GPU BENCHMARK

Inspect the current GPU implementation.

If a real GPU benchmark exists, verify that it measures actual GPU work.

If GPU support is unavailable:

show:

GPU benchmark unavailable on this system.

Do not produce fake GPU scores.

The test must adapt to:

- integrated GPU
- dedicated GPU
- no GPU
- unknown GPU

---

# 13. THERMAL MONITORING

Verify real-time monitoring.

Record:

- timestamp
- CPU temperature
- GPU temperature
- CPU frequency
- GPU frequency
- utilization
- power where available

Verify that the PDF graph contains actual collected samples.

Do not create graphs from synthetic data in real mode.

---

# 14. THERMAL THROTTLING ANALYSIS

Do not declare "thermal throttling" solely because temperature is high.

Look for evidence such as:

- frequency reduction
- performance reduction
- thermal limit indicators where available

Use cautious wording:

"Potential thermal limitation detected."

rather than making a definitive hardware-fault diagnosis.

---

# 15. BATTERY AUDIT

Verify:

```text
health =
full_charge_capacity / design_capacity × 100
```

Verify units carefully.

Support:

- Wh
- mWh
- µWh

Do not accidentally divide incompatible units.

Show:

- design capacity
- full charge capacity
- health
- cycles
- charging state

If unavailable:

NOT AVAILABLE

---

# 16. SSD HEALTH

Verify SMART/NVMe data.

Support:

- SATA
- NVMe
- HDD where possible

Do not report "healthy" merely because a benchmark is fast.

Health should be based on actual SMART/NVMe information.

---

# 17. WORKLOAD PROFILES

Audit all profiles.

At minimum:

- Computational Materials Science
- Scientific Computing
- Programming
- AI/ML
- General Productivity

Make sure the profile actually changes:

- requirements
- test selection
- interpretation

It must not simply change the text shown on the screen.

---

# 18. COMPUTATIONAL MATERIALS PROFILE

Make this profile technically meaningful.

Evaluate:

CPU:

- cores
- threads
- sustained performance

RAM:

- capacity
- bandwidth

Storage:

- SSD type
- health
- performance

Thermals:

- sustained performance
- degradation

Software environment:

- Linux
- Python
- NumPy
- SciPy
- ASE
- Quantum ESPRESSO availability

GPU:

Treat as workload-dependent rather than universally required.

Do NOT claim that the tool can guarantee DFT performance from generic benchmarks.

---

# 19. QUANTUM ESPRESSO PLUGIN

Verify that:

- `pw.x` detection works
- version detection works if possible
- unavailable QE is handled correctly
- optional benchmark does not break the main diagnostic

Do not automatically execute large QE calculations.

Use only a small controlled benchmark.

Clearly identify:

QE benchmark not available

when QE is absent.

---

# 20. MANUAL INSPECTION

Verify:

### Display

- black
- white
- red
- green
- blue
- gray

Allow:

PASS
OBSERVATION
FAIL
SKIPPED

### Keyboard

Track actual key presses.

Allow failed keys to be recorded.

### Touchpad

Provide manual test.

### Ports

Provide manual checklist.

Make sure these results are included in the final PDF.

---

# 21. BACKGROUND PROCESS DETECTION

Before benchmarking:

measure:

- CPU utilization
- RAM usage

Detect unusually heavy background activity.

Show:

"Benchmark may be affected by background activity."

Do NOT terminate arbitrary processes.

---

# 22. POWER MODE

Detect current power mode.

If the laptop is running on battery:

display a warning:

"For representative performance results, connect the laptop to AC power."

Do not silently change power settings.

---

# 23. PDF AUDIT

Generate a report from a REAL diagnostic.

Open/inspect the generated PDF.

Verify:

- PDF is valid
- pages render
- tables are readable
- graphs render
- values are correct
- no placeholder text
- simulation watermark works
- report ID works
- timestamp works
- workload profile is correct
- manual inspection results appear

The PDF must never claim a test was performed if it was skipped.

---

# 24. REPORT LANGUAGE

Use careful technical language.

Examples:

GOOD:

"CPU frequency decreased during sustained testing."

GOOD:

"Potential thermal limitation detected."

GOOD:

"Battery capacity is approximately 82% of design capacity."

BAD:

"CPU is damaged."

BAD:

"Thermal paste is definitely bad."

BAD:

"This laptop will definitely run Quantum ESPRESSO well."

The software reports measurements and evidence; it should not invent diagnoses.

---

# 25. RESULT ENGINE

Use:

PASS
CAUTION
FAIL
NOT AVAILABLE
NOT TESTED

Avoid one universal "Laptop Score" as the main result.

The user should be able to see exactly why a category received its status.

For every CAUTION or FAIL, provide:

- measured value
- requirement
- reason
- relevant observation

---

# 26. PRIVACY AUDIT

Verify that the application does NOT:

- upload files automatically
- read personal documents
- read browser history
- collect passwords
- access camera
- access microphone
- collect unrelated personal information

Cloud upload must remain optional.

---

# 27. OFFLINE TEST

Disconnect/disable network access if practical.

Verify:

```text
Agent
→ hardware detection
→ diagnostics
→ benchmarks
→ analysis
→ PDF
```

still works.

The core diagnostic must not depend on internet connectivity.

---

# 28. ERROR INJECTION

Intentionally simulate:

- unavailable temperature sensor
- unavailable battery
- unavailable GPU
- SMART unavailable
- benchmark failure
- user cancellation
- timeout
- insufficient RAM
- insufficient disk space
- missing QE
- background process interference

The application must gracefully continue wherever possible.

---

# 29. RESOURCE SAFETY

Verify the diagnostic agent itself does not consume excessive resources.

Especially:

- RAM benchmark
- CPU benchmark
- disk benchmark

Tests must scale according to detected hardware.

Do not let a low-end laptop become unusable merely because LaptopCheck is testing it.

---

# 30. PERFORMANCE

The UI must remain responsive during testing.

Long-running tests must not block the web server.

Use asynchronous/background execution where appropriate.

The STOP TEST action must remain responsive.

---

# 31. SECURITY AUDIT

Inspect:

- subprocess execution
- shell commands
- file paths
- temporary files
- API input
- report paths
- uploaded data

Prevent command injection.

Do not execute arbitrary user-provided commands.

Do not trust filenames or paths supplied by the UI.

---

# 32. PACKAGING

After functionality is stable, prepare:

Windows:

LaptopCheck.exe / installer

Linux:

AppImage or equivalent portable package

The end user should NOT need Python installed.

Document the build commands.

---

# 33. DOCUMENTATION

Update README with:

- installation
- Windows usage
- Linux usage
- Quick Inspection
- Standard Diagnostic
- Extended Diagnostic
- workload profiles
- safety information
- offline mode
- PDF reports
- troubleshooting
- limitations

Include a clear distinction between:

SUPPORTED
PARTIALLY SUPPORTED
NOT AVAILABLE

---

# 34. FINAL TEST MATRIX

Create a test matrix:

| Area | Status | Evidence |
|---|---|---|
| Linux hardware | | |
| Windows provider | | |
| Simulation | | |
| CPU | | |
| RAM | | |
| Storage | | |
| GPU | | |
| Battery | | |
| Thermal | | |
| Safety | | |
| Workloads | | |
| QE | | |
| Display | | |
| Keyboard | | |
| Touchpad | | |
| Ports | | |
| API | | |
| Frontend | | |
| PDF | | |
| Offline | | |
| Packaging | | |

Do not mark something PASS unless it has actually been tested.

---

# 35. FINAL ACCEPTANCE TEST

Perform one complete REAL diagnostic on the current physical Linux machine.

Use:

Computational Materials Science

and:

Quick / Shop Safe

Then generate the actual PDF.

Inspect the PDF.

Then perform at least one Simulation Mode run.

Then run the complete automated test suite.

Then build the frontend.

Then verify the backend starts.

---

# 36. IMPORTANT

Do not simply report:

"Implemented."

Provide evidence.

For every major component report:

- what was tested
- command used
- result
- limitations

If something cannot be tested because the current environment is Linux, Windows hardware, browser automation, or another dependency is unavailable, explicitly say so.

Do NOT falsely claim cross-platform verification.

---

# 37. DO NOT STOP AFTER FINDING ISSUES

If you discover bugs:

1. Fix them.
2. Add a regression test.
3. Re-run the affected tests.
4. Re-run the full suite.

Continue until the application is in the best verified state possible.

Do not rewrite working modules unnecessarily.

---

# 38. FINAL DELIVERABLE

At the end provide:

1. Current implementation status
2. Features actually working
3. Features partially supported
4. Features unavailable
5. Tests executed
6. Test results
7. Remaining known limitations
8. Exact command to launch the application
9. Exact command to run tests
10. Exact command to build the production package
11. Location of generated PDF
12. Location of executable/package

Most importantly:

**Do not confuse "implemented" with "verified."**

Only call functionality verified when it has actually been tested.