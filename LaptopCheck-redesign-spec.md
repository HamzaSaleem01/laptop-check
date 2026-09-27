# LaptopCheck: diagnostic engine and product redesign

## Executive summary

LaptopCheck should become a **local laptop examiner with a workload adviser**, with the website acting as its download, setup, report viewer, and reference-data home. A web page alone cannot inspect another computer's BIOS, CPU topology, NVMe SMART data, battery cycle count, or sensor readings. The current site acknowledges that limitation and offers Windows scripts, but its browser panel also shows exact-looking values without identifying their source or confidence. That makes it difficult to know which numbers are measured, reported by firmware, inferred, simulated, or unavailable.

The product should answer two separate questions:

1. **What hardware and condition does this particular laptop actually have?**
2. **Given the user's workload and constraints, what can this particular configuration reasonably do, and what are its limiting factors?**

It should never label a machine “good for DFT” based on a generic six-core/16-GB threshold. It should explain the evidence, trade-offs, uncertainty, and workload assumptions behind every conclusion.

## Review of the live site

Inspected `https://laptopcheck.vercel.app/` on 27 September 2026. The home page includes live-device and preset modes, an upload path for `laptop_specs.json`, Windows scanner downloads/instructions, Quick / Full / Extended test choices, four workload cards, a manual shop-check section, and a historical PDF report list.

### What is present

- Browser-side device page plus a separate Windows scanner route.
- A preset comparison mode with six example reference profiles.
- A basic CPU, GPU, RAM, storage, battery and OS summary; an expanded view adds CPU clocks/instruction flags, GPU driver/VRAM, memory speed and use, storage SMART/temperature, and battery capacity/cycles.
- Three benchmark-duration choices, thermal-guardian language, manual display/keyboard/touchpad/port checks, and downloadable PDF samples.
- Workload cards for computational materials science, software development, AI/ML, and office work.

### Product and trust problems visible on the page

- The page says browsers cannot read certain physical details, then presents exact-looking live values such as CPU temperature, memory type/channel, NVMe model, battery cycles, and health. Each field needs a source and a confidence state. Browser APIs cannot establish many of these facts. A Linux host page reporting “Intel Processor (12 Threads Detected)” with no model illustrates why an OS-level collector is necessary.
- “100% Genuine Specs” and “exact hardware in 3 seconds” overpromise. SMBIOS, firmware, drivers, sensor support, permissions, and OS APIs can return missing, stale, generic, or vendor-specific values. The software needs to say “reported by firmware,” “read from OS,” “inferred,” or “not available,” not imply certainty.
- The page suggests `irm https://laptopcheck.vercel.app/scan.ps1 | iex`. That downloads and immediately executes a remote script. This is a high-trust path for a tool meant to run on a shop laptop. Prefer a signed, versioned, inspectable download with a visible publisher/hash and a clear disclosure of every collected field. Never request administrator rights for ordinary read-only inventory.
- The workload cards show fixed labels such as “VERY HIGH” and “RECOMMENDED,” but do not show a per-machine calculation, evidence, threshold source, user-selected problem size, estimated runtime, memory requirement, or confidence. “AI/ML” is too broad to assess without model size, framework, precision, and VRAM.
- A CPU name, core count, and maximum clock do not establish sustained performance. Cooling, power limits, memory configuration, firmware mode, and observed throttling matter. A short burst score must not be presented as a sustained workload result.
- Core technical details requested by the user are incomplete or hidden: CPU architecture/microarchitecture, core topology and P/E-core counts, cache hierarchy, ISA flags, sustained clocks and power; DIMM/soldered status and upgrade paths; GPU architecture/compute support and dedicated/shared memory; display resolution/refresh/panel evidence; Wi-Fi/Ethernet link capabilities; and uncertainty/provenance per value.
- “RAM integrity” and “deep storage benchmarks” need precise definitions and safeguards. A normal OS process cannot prove all RAM is error-free; storage write tests can consume space/wear SSDs or damage existing data if poorly designed. Make test scope explicit, bounded, read-only by default, and opt-in when writes or extended load are involved.
- The PDF list contains sample reports with machine names. Sample artifacts must be clearly marked as examples, never mixed with a user's actual results.
- Manual checks are useful, but should report user-confirmed observations separately from automated measurements.

This review covers the visible UI and publicly exposed text; I did not run a benchmark or execute the downloaded scanner. Therefore test safety and report correctness remain unverified.

## Product principles

1. **Evidence before verdict.** Every fact carries its source, collection time, method, confidence, and limitations.
2. **Unknown stays unknown.** Never fill absent sensor or firmware fields with plausible numbers.
3. **Profile the actual laptop.** Compare measured capabilities and health to workload-specific requirements and user constraints, not a universal “good laptop” preset.
4. **Explain the result.** Say what a capability means, where it helps, where it does not, and what limits the workload.
5. **Separate suitability from condition.** A healthy laptop can be too small for a workload; a capable model can be degraded or throttling.
6. **Safe by default.** Inventory is read-only. Benchmarks have named duration, load, write volume, stop conditions, and explicit consent.
7. **Portable evidence.** Reports are self-contained, timestamped, reproducible, and usable offline.

## Proposed user journey

1. **Choose a goal:** inspect a used laptop; assess this laptop; compare two laptops; or estimate suitability for a planned workload.
2. **Choose workload(s):** select a detailed template (for example, Quantum ESPRESSO plane-wave DFT, ASE/Python, local LLM inference, gaming) and answer a few task questions. Let users set minimum RAM/VRAM, expected system/model size, budget, runtime tolerance, OS/toolchain, portability, and whether upgrades are acceptable.
3. **Collect a read-only inventory:** download and launch a signed Windows/Linux/macOS agent, or upload a previously exported report. Explain each permission and collected field before scanning. Show progress and unavailable fields.
4. **Review discovered hardware:** show source and confidence next to values; flag conflicts and ask the user to verify the model or upgradeability when firmware cannot establish it.
5. **Choose tests:** begin with non-invasive checks; show estimated duration, load, disk writes, and stop conditions. Allow the user to skip any test.
6. **Get a per-workload assessment:** overall fit plus separate compatibility, capacity, speed, sustained behavior, condition, and uncertainty. Explain likely bottlenecks and useful upgrades.
7. **Export/share locally:** generate a PDF and JSON report. Sharing to the website is optional and off by default.

## Architecture

### A. Local collector (source of hardware truth)

Build a small, versioned, signed native agent with OS-specific read-only adapters and a stable JSON output contract. A website cannot substitute for it.

- **Windows:** use documented CIM/WMI and Windows APIs for processor, memory, OS, battery and system data; use vendor-supported interfaces/tools where SMART and sensors require them. Treat SMBIOS fields as firmware-reported, not guaranteed truth. Do not pipe a remote script directly into an execution command.
- **Linux:** combine `/proc`, `/sys`, `lscpu`, `dmidecode` where permitted, `hwmon`/thermal interfaces, `upower`/ACPI, and `smartctl` where installed and authorized. Sensor channels are driver and platform dependent; preserve raw labels and do not guess that an unlabeled sensor is CPU temperature.
- **macOS (later phase):** use supported system APIs/commands and clearly mark limits where Apple does not expose battery, SMART, or thermal detail to third-party apps.
- **Cross-platform:** normalize units and identifiers; retain original raw values; use timeouts and bounded output; collect no serial number, username, hostname, or network identifiers unless the user explicitly opts in. Redact by default in the shareable report.

A field record should follow this pattern:

```json
{
  "key": "cpu.logical_processors",
  "value": 12,
  "unit": "count",
  "source": "linux:/sys/devices/system/cpu/online",
  "method": "os_topology",
  "confidence": "high",
  "observed_at": "2026-09-27T00:00:00Z",
  "limitations": []
}
```

Use explicit `status` values such as `measured`, `reported`, `inferred`, `user_confirmed`, `unavailable`, `permission_denied`, `unsupported`, and `conflict`. Never manufacture a value for an unavailable field.

### B. Inventory and health data model

Store hardware identity separately from live state and benchmark observations.

- **System:** manufacturer/model/product identifiers, BIOS/UEFI version/date, OS/build/kernel, architecture, firmware-reported identifiers with redaction controls.
- **CPU:** exact model string, vendor, family/model/stepping where available, ISA/bitness, microarchitecture mapping with database version, physical packages, physical/logical cores, topology by core type (P/E or equivalent), online/disabled cores, SMT, base/max advertised clocks, sampled per-core effective clocks under idle/load, L1/L2/L3 cache, supported instruction sets, power/thermal limits only when sourced.
- **Memory:** total usable and installed capacity; modules/slots; form factor; type/generation; rated/configured speed; channel mode when exposed; ranks/ECC; soldered/removable/slot population and upgradeability as verified, inferred, or unknown; available memory is a changing snapshot, not capacity.
- **GPU(s):** vendor/model, integrated/discrete status, architecture, driver/runtime, compute APIs and versions, dedicated VRAM vs shared memory, memory bandwidth only when known, active device, power/temperature/load when readable. Never call shared system RAM “VRAM.”
- **Storage:** model, capacity, bus/protocol, firmware, partition/free-space context, SMART/NVMe health attributes and self-test history when available, temperature, unsafe shutdowns/media errors/wear indicators, read/write benchmark results with test size and method. SMART pass is not a guarantee of future health.
- **Thermals/power:** sensor label and source, idle/load time series, fan RPM if readable, package power if readable, AC/battery state, thermal/power throttling flags, stop reasons. Identify sensor mapping limitations.
- **Battery:** design/full-charge capacity and wear estimate where available, cycle count where exposed, current charge, voltage/temperature if exposed, source and firmware limitations. Capacity estimate is not a remaining-life guarantee.
- **Display/input/network:** panel EDID identity, resolution, refresh, active display, HDR/color claims only when detectable; user-guided dead-pixel/backlight test; keyboard/touchpad/ports user checks; Wi-Fi/Ethernet adapter and negotiated link/capability only where supported. Do not silently run network speed tests.

### C. Safe test runner

The agent owns test execution and safety; the web UI only presents an approved plan and displays results.

- Default inventory and quick inspection are read-only. Benchmark tests are bounded, named, and independently cancellable.
- CPU quick test: short, reproducible single/multi-thread workload; record version, duration, power mode, starting temperature, score, effective clock, temperature, and throttling. Do not infer 30-minute performance from a burst.
- Sustained CPU test: explicit duration and load cap, temperature/power monitoring, pause/stop thresholds based on reported vendor/firmware limits and safe configurable policy. If trustworthy telemetry is unavailable, state that protection is limited and offer a conservative test.
- Memory: bandwidth/latency benchmark is distinct from a full memory integrity test. Full error-detection needs bootable/offline or privileged tools and should be a separate opt-in workflow.
- Storage: use bounded test files in a user-selected temporary location, check free space, cap total writes, clean up only the test's own files, and report exact bytes written. Health reads are separate from performance tests.
- GPU: query support and run only known bounded tests compatible with the detected API/device. Identify whether results include integrated GPU/shared memory. No automatic CUDA suitability claim based solely on NVIDIA brand.
- Stop immediately on user cancellation, critical reported temperature, OS thermal event, repeated errors, or configured safety limit. Log why a test stopped.
- Keep a dry-run plan preview and a “shop-safe quick check” lasting under a clearly estimated time, with longer tests opt-in.

### D. Workload assessment engine

A workload profile is a structured, versioned set of constraints and explanatory rules, not a star rating or vague tier. Profiles must be backed by official software documentation, published benchmark methods, or clearly labeled empirical data. Store source URLs, revision date, and confidence.

For each selected task, calculate and show independent dimensions:

- **Compatibility:** OS, instruction set, driver/runtime, software support, required accelerators.
- **Capacity:** RAM/VRAM/storage requirements based on the user's selected input size or model.
- **Performance:** observed benchmark evidence relevant to the task; use comparable results and record benchmark/version/settings.
- **Sustained behavior:** performance under longer load, throttling, power mode, and thermal evidence.
- **Condition:** battery, storage health flags, errors, and observed stability.
- **Confidence:** how much of the conclusion is measured, reported, inferred, stale, or missing.

Use hard gates for real incompatibilities (for example, required CUDA when CUDA is unavailable), explicit constraint checks for capacity, and measured performance ranges for speed. Avoid a single unexplained weighted score. If a summary score is offered, show its formula, weight controls, source data, and which missing measurements widen the range. Present outcomes such as `Meets stated needs`, `Likely workable with limits`, `Likely unsuitable for stated input`, or `Insufficient evidence`, each with evidence and caveats.

#### Computational materials / DFT profile

Ask for code and build (Quantum ESPRESSO version/build and CPU/GPU support), functional/pseudopotential approach where known, system size/atom count, cutoff, k-point grid, spin/SOC, expected number of bands, job duration, and whether jobs can run on a cluster. Explain that CPU threads do not translate linearly to DFT speed: MPI/OpenMP parallelization depends on k-points, bands, FFT work, libraries, and the input. Assess memory headroom and thermal sustain, not just core count. GPU value depends on the actual QE build and supported accelerator path. Estimate only where a validated model exists; otherwise provide a clearly labeled pilot-run recommendation and collect a short representative benchmark if the user has their own input.

#### Additional workload templates

- **Python / ASE / scientific computing:** clarify whether work is scripting, NumPy/SciPy BLAS, compilation, or large in-memory datasets; include RAM and BLAS threading.
- **Programming:** project size, compiler, IDEs, containers/VM count, parallel build, disk and memory footprint.
- **AI/ML:** model, framework/version, precision/quantization, VRAM requirement, context/batch size, CUDA/ROCm/Metal availability, and whether CPU inference is acceptable.
- **Gaming/graphics:** target games/apps, resolution, quality, frame-rate target, GPU/VRAM and display refresh, power mode.
- **Office/portable study:** app count, video calls, display use, battery condition and measured battery test context.
- **Custom workload:** let users enter constraints and minimums without requiring a predefined category.

### E. Website and privacy model

The site should guide downloads, explain scans, accept a local JSON report, visualize findings, manage workload profiles, and produce reports. It must not imply the site itself inspected inaccessible hardware. Local-first processing should be the default; if a server is used for accounts/reference data, do not upload inventory automatically. Provide a preview of exactly what leaves the device before optional upload. Avoid public report listings, serial numbers, hostnames, usernames, or precise network details in default PDFs. Publish the collector source or reproducible build metadata, signed releases, checksums, release notes, and a security/contact policy.

## Report design

1. **Decision summary:** laptop identity (redacted), tested date, selected workloads and assumptions, fit outcomes, major limits, and confidence.
2. **Evidence card:** source/method/status for critical fields; unavailable/conflicting fields called out.
3. **Hardware inventory:** CPU topology/cache/ISA, memory configuration and upgrade uncertainty, GPU/VRAM, storage, thermals, battery, display and network.
4. **Condition findings:** measured health values, errors, test coverage, stopped/skipped tests.
5. **Workload-by-workload explanation:** strengths, bottlenecks, expected use, unknowns, and practical upgrade/alternative suggestions.
6. **Test record:** exact benchmark versions/settings/durations, start/end state, temperature/power trace summaries, disk writes, safety stops.
7. **Limitations and sources:** profile revision, source links, and distinctions between measurement, vendor claim, inference, and user entry.

PDF generation must use flow-based layout, wrapped content, page-break rules, font embedding, and render-based visual review. Include sample PDFs in a separate examples area and label every sample prominently.

## Implementation plan

### Phase 0 — Correct the existing product's claims

- Change browser-detected values to “browser estimate” only when genuinely obtainable; mark temperatures, cycles, SMART, memory type/channels and exact models unavailable unless an agent supplied them.
- Remove “100% genuine” and “exact in 3 seconds” claims.
- Replace remote PowerShell pipe-and-execute instructions with signed, versioned download and inspectable source/hash; document what is collected and make scan local by default.
- Mark presets and PDF samples as synthetic examples; make live vs preset state visually unmistakable.
- Define a stable JSON schema with provenance and schema version before adding more scanner fields.

### Phase 1 — Reliable inventory

- Implement Windows and Linux collector adapters and a conformance test corpus from varied hardware (Intel hybrid, AMD, ARM where supported, integrated/discrete GPU, soldered RAM, SATA/NVMe, missing sensors).
- Build normalization, field provenance, redaction, and import/export.
- Validate against OS utilities and firmware screens; track field coverage and false claims by device family.

### Phase 2 — Bounded diagnostics

- Add cancellable quick tests and thermal/event logging; independently measure CPU, memory bandwidth, storage read and bounded write, GPU compatibility, battery/storage health.
- Make any full memory test, extended combined stress, or write-heavy test opt-in with time/wear disclosure.
- Validate test stop behavior and compare repeated results across power modes and temperatures.

### Phase 3 — Workload model

- Define versioned profile format, sources, hard constraints, capacity estimators, benchmark compatibility, and uncertainty propagation.
- Start with QE/DFT, Python/ASE, software development, AI/ML, gaming, productivity, and custom needs.
- Build explainable outcome cards that cite the exact measured fields and assumptions. Do not release “recommended” labels until profiles have device-level validation.

### Phase 4 — User experience and reporting

- Replace the dashboard-first landing page with the guided journey above.
- Provide an expert view for full details and a plain-language view for shop use.
- Add side-by-side laptop comparison by selected workload, offline JSON/PDF export, and report visual QA.
- Add accessibility, keyboard navigation, mobile layout, and clear language localization.

### Phase 5 — Release and maintenance

- Sign installers and updates; publish provenance, checksums, changelog, privacy policy, support matrix, and vulnerability reporting.
- Maintain CPU/GPU/software compatibility data with revisions and citations.
- Measure field coverage, scan failures, unsupported devices, false positives, and workload prediction error; publish limitations.

## Release acceptance criteria

- No exact hardware or health value appears without a traceable source/status; unavailable values remain visibly unavailable.
- The same saved inventory imports to the same result offline and online; schema versions migrate safely.
- At least representative Windows and Linux laptops produce verified model/topology/memory/storage records, with unsupported fields explicitly reported.
- A workload result names its user assumptions, profile version, evidence, bottleneck, confidence, and constraints; no fixed core/RAM threshold alone produces a “good” verdict.
- Every benchmark states duration, load, disk writes, cancellation behavior, and stop reason; quick mode completes safely on supported minimum hardware.
- Thermal and SMART limitations are visible, and unavailable telemetry never gets represented as a pass.
- PDF pages are rendered and visually checked for clipping, overlap, and unreadable tables; sample reports cannot be mistaken for a real scan.
- The scanner does not silently upload inventories or request unnecessary administrator privileges.

## Evidence and references

The visible site behavior and values described above were observed directly on the deployed site. Technical implementation should follow current OS interfaces and software documentation. For example, Microsoft documents that Windows processor core/logical processor and clock fields can come from SMBIOS, making them firmware-reported values; the Linux kernel documents optional, driver-specific `hwmon` sensors and warns that unlabeled channels may need platform-specific interpretation. Quantum ESPRESSO's guide describes multiple MPI parallelization levels and workload-dependent scaling, which is why raw thread count is not a sufficient DFT suitability score.

- [Microsoft Win32_Processor documentation](https://learn.microsoft.com/en-us/windows/win32/cimwin32prov/win32-processor)
- [Linux kernel hwmon sysfs interface](https://docs.kernel.org/5.3/hwmon/sysfs-interface.html)
- [Quantum ESPRESSO user guide: parallelization levels](https://www.quantum-espresso.org/Doc/user_guide_PDF/user_guide.pdf)
- [MDN: File System API and browser sandbox](https://developer.mozilla.org/en-US/docs/Web/API/FileSystem)
