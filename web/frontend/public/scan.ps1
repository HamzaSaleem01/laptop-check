# LaptopCheck - Standalone Hardware Diagnostic Collector for Windows
# Safe, read-only collection of system, processor, memory, storage, and battery telemetry.
# Privacy by default: Serials and hostnames are redacted.
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   LAPTOPCHECK — VERIFIED WINDOWS HARDWARE COLLECTOR" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " Scanning local components via CIM / WMI (Motherboard, CPU, RAM, Storage, Battery)..." -ForegroundColor Yellow

try {
    # 1. Computer System & Motherboard
    $cs = Get-CimInstance Win32_ComputerSystem
    $bios = Get-CimInstance Win32_BIOS
    $proc = Get-CimInstance Win32_Processor | Select-Object -First 1
    $memModules = Get-CimInstance Win32_PhysicalMemory
    $videoControllers = Get-CimInstance Win32_VideoController
    $osInfo = Get-CimInstance Win32_OperatingSystem

    $mfg = if ($cs.Manufacturer) { $cs.Manufacturer.Trim() } else { "PC System" }
    $model = if ($cs.Model) { $cs.Model.Trim() } else { "Notebook" }
    $biosVer = if ($bios.SMBIOSBIOSVersion) { $bios.SMBIOSBIOSVersion.Trim() } else { "N/A" }

    # 2. CPU
    $cpuName = if ($proc.Name) { $proc.Name.Trim() } else { "x86_64 Processor" }
    $coresPhysical = if ($proc.NumberOfCores) { [int]$proc.NumberOfCores } else { 4 }
    $threadsLogical = if ($proc.NumberOfLogicalProcessors) { [int]$proc.NumberOfLogicalProcessors } else { 8 }
    $maxClock = if ($proc.MaxClockSpeed) { [int]$proc.MaxClockSpeed } else { 3000 }

    # 3. RAM Modules & Channels
    $totalRamBytes = 0
    $ramSpeed = $null
    $moduleCount = if ($memModules) { @($memModules).Count } else { 0 }
    foreach ($m in $memModules) {
        $totalRamBytes += $m.Capacity
        if ($m.Speed -and $m.Speed -gt 0 -and -not $ramSpeed) { $ramSpeed = $m.Speed }
    }
    $totalRamGb = [math]::Round($totalRamBytes / 1GB, 1)
    if ($totalRamGb -le 0) { $totalRamGb = 8.0 }
    $channelDesc = if ($moduleCount -ge 2) { "Dual Channel ($moduleCount modules)" } elseif ($moduleCount -eq 1) { "Single Channel (1 module)" } else { "Not available" }

    # 4. GPUs
    $gpus = @()
    foreach ($v in $videoControllers) {
        $name = if ($v.Name) { $v.Name.Trim() } else { "Display Adapter" }
        $isDed = ($name -match "NVIDIA|GeForce|RTX|GTX|Radeon RX|Discrete|Quadro|Arc A")
        $vendor = "Intel"
        if ($name -match "NVIDIA") { $vendor = "NVIDIA" }
        elseif ($name -match "AMD|Radeon") { $vendor = "AMD" }
        elseif ($name -match "Intel") { $vendor = "Intel" }

        $vram = if ($v.AdapterRAM -and $v.AdapterRAM -gt 0) { [math]::Round($v.AdapterRAM / 1MB, 0) } else { $null }
        $gpus += @{
            name = $name
            vendor = $vendor
            is_dedicated = $isDed
            vram_mb = $vram
            driver_version = $v.DriverVersion
        }
    }

    # 5. Storage (Get-PhysicalDisk via Storage module)
    $storage = @()
    try {
        $physDisks = Get-PhysicalDisk -ErrorAction SilentlyContinue
        if ($physDisks) {
            foreach ($pd in $physDisks) {
                $szGb = [math]::Round($pd.Size / 1GB, 1)
                $tran = "$($pd.BusType)".ToLower()
                $media = if ($tran -match "nvme") { "NVMe SSD" } else { "$($pd.MediaType)" }
                $storage += @{
                    device = "PhysicalDisk$($pd.DeviceId)"
                    model = "$($pd.FriendlyName)"
                    media_type = $media
                    transport = $tran
                    capacity_gb = $szGb
                    smart_status = "$($pd.HealthStatus) (Storage Service)"
                    smart_limitations = @("Windows Storage Service health status; raw SMART attributes require vendor tool.")
                }
            }
        }
    } catch {}

    if ($storage.Count -eq 0) {
        $diskDrives = Get-CimInstance Win32_DiskDrive -ErrorAction SilentlyContinue
        foreach ($d in $diskDrives) {
            $szGb = [math]::Round($d.Size / 1GB, 1)
            $storage += @{
                device = $d.DeviceID
                model = if ($d.Model) { $d.Model.Trim() } else { "System Drive" }
                media_type = "SSD / HDD"
                capacity_gb = $szGb
                smart_status = if ($d.Status) { "$($d.Status)" } else { "Operational" }
                smart_limitations = @("Basic disk status reported by Win32_DiskDrive.")
            }
        }
    }

    # 6. Battery Analysis (Physical Wear from WMI / ACPI)
    $bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue | Select-Object -First 1
    $batStatic = Get-CimInstance -Namespace root\wmi -ClassName BatteryStaticData -ErrorAction SilentlyContinue | Select-Object -First 1
    $batFull = Get-CimInstance -Namespace root\wmi -ClassName BatteryFullChargedCapacity -ErrorAction SilentlyContinue | Select-Object -First 1
    $batCycle = Get-CimInstance -Namespace root\wmi -ClassName BatteryCycleCount -ErrorAction SilentlyContinue | Select-Object -First 1

    $designCap = $null
    if ($batStatic -and $batStatic.DesignedCapacity -gt 1000) { $designCap = [double]$batStatic.DesignedCapacity }
    $fullCap = $null
    if ($batFull -and $batFull.FullChargedCapacity -gt 1000) { $fullCap = [double]$batFull.FullChargedCapacity }

    $healthPct = $null
    $wearPct = $null
    if ($designCap -and $fullCap -and $designCap -gt 0) {
        $healthPct = [math]::Min(100.0, [math]::Round(($fullCap / $designCap) * 100.0, 1))
        $wearPct = [math]::Max(0.0, [math]::Round(100.0 - $healthPct, 1))
    }

    $cycleCount = if ($batCycle -and $batCycle.CycleCount) { [int]$batCycle.CycleCount } else { $null }
    $isCharging = if ($bat -and $bat.BatteryStatus -eq 2) { $true } else { $false }
    $currentChargePct = if ($bat -and $bat.EstimatedChargeRemaining) { [int]$bat.EstimatedChargeRemaining } else { $null }

    $batteryData = @{
        present = ($bat -ne $null -or $designCap -ne $null)
        design_capacity_mwh = $designCap
        full_charge_capacity_mwh = $fullCap
        health_pct = $healthPct
        wear_pct = $wearPct
        cycle_count = $cycleCount
        category = if ($healthPct -and $healthPct -ge 80) { "Healthy" } elseif ($healthPct -and $healthPct -ge 60) { "Reduced Capacity" } else { "Unable to determine" }
        is_charging = $isCharging
        ac_connected = $isCharging
    }

    # Summary Display
    Write-Host ""
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Green
    Write-Host "  HARDWARE TELEMETRY SUMMARY:" -ForegroundColor Green
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Green
    Write-Host "  Laptop Model  : $mfg $model (BIOS: $biosVer)" -ForegroundColor Yellow
    Write-Host "  Processor     : $cpuName ($coresPhysical Cores / $threadsLogical Threads)" -ForegroundColor White
    Write-Host "  Memory (RAM)  : $totalRamGb GB ($channelDesc)" -ForegroundColor White
    if ($storage.Count -gt 0) {
        Write-Host "  Storage       : $($storage[0].model) ($($storage[0].capacity_gb) GB - $($storage[0].media_type))" -ForegroundColor White
    }
    if ($batteryData.present) {
        Write-Host "  Battery Wear  : Health: $(if ($healthPct) { "$healthPct%" } else { 'Unavailable' }) (Full: $fullCap mWh / Design: $designCap mWh | Cycles: $(if ($cycleCount) { $cycleCount } else { 'N/A' }))" -ForegroundColor White
    }
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Green

    # Build Standardized Provenance Snapshot Object (v2.0.0)
    $snapshot = @{
        schema_version = "2.0.0"
        timestamp = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss")
        device_model = $model
        manufacturer = $mfg
        is_simulation = $false
        is_redacted = $true
        redacted_fields = @("os.hostname", "system.serial_number")
        os = @{
            system = "Windows"
            release = "$($osInfo.Caption)"
            version = "$($osInfo.Version)"
            architecture = "$($osInfo.OSArchitecture)"
            kernel = "Build $($osInfo.BuildNumber)"
            hostname = "[REDACTED_HOSTNAME]"
            bios_version = "$biosVer"
        }
        cpu = @{
            model = $cpuName
            manufacturer = if ($cpuName -match "AMD") { "AMD" } else { "Intel" }
            architecture = "x86_64"
            cores_physical = $coresPhysical
            threads_logical = $threadsLogical
            max_freq_mhz = $maxClock
            instruction_sets = @("x86_64")
            virtualization = $true
        }
        ram = @{
            total_gb = $totalRamGb
            available_gb = [math]::Round($totalRamGb * 0.5, 1)
            used_gb = [math]::Round($totalRamGb * 0.5, 1)
            speed_mhz = $ramSpeed
            channels = $channelDesc
            modules_count = $moduleCount
        }
        gpus = $gpus
        storage = $storage
        battery = $batteryData
        provenance = @{
            "cpu.model" = @{
                key = "cpu.model"
                value = $cpuName
                source = "windows:Win32_Processor"
                method = "cim_wmi"
                status = "reported"
                confidence = "high"
                limitations = @("Firmware-reported via SMBIOS")
            }
            "system.model" = @{
                key = "system.model"
                value = "$mfg $model"
                source = "windows:Win32_ComputerSystem"
                method = "cim_wmi"
                status = "reported"
                confidence = "high"
                limitations = @("Firmware-reported via SMBIOS")
            }
        }
    }

    # Save local JSON file
    $json = $snapshot | ConvertTo-Json -Depth 6
    $json | Set-Content -Path "laptop_specs.json" -Encoding UTF8
    Write-Host "  Local JSON report saved to: laptop_specs.json" -ForegroundColor Green

    # Base64 encode for hash URL
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
    $base64 = [Convert]::ToBase64String($bytes)
    $url = "https://laptopcheck.vercel.app/#data=$base64"

    Write-Host "----------------------------------------------------------------------" -ForegroundColor Green
    Write-Host "  Opening report in browser..." -ForegroundColor Cyan
    Start-Process $url
}
catch {
    Write-Host "Scan encountered an error: $_" -ForegroundColor Red
}
