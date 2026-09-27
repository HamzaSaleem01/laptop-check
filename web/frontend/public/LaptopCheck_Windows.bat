@echo off
title LaptopCheck - Real Hardware Diagnostic Scanner
echo ======================================================================
echo   LaptopCheck - Shop-Safe Laptop Hardware Diagnostic Scanner
echo ======================================================================
echo   Scanning local hardware components via Windows Management Engine...
echo   Please wait 3-5 seconds...
echo.

powershell -NoProfile -ExecutionPolicy Bypass -Command "& {
    Write-Host '----------------------------------------------------------------------' -ForegroundColor Cyan
    Write-Host '  LAPTOPCHECK v1.0.0 - GENUINE LOCAL HARDWARE DETECTION REPORT' -ForegroundColor Green
    Write-Host '----------------------------------------------------------------------' -ForegroundColor Cyan

    $cs = Get-CimInstance Win32_ComputerSystem
    $bios = Get-CimInstance Win32_BIOS
    $proc = Get-CimInstance Win32_Processor
    $ramModules = Get-CimInstance Win32_PhysicalMemory
    $gpus = Get-CimInstance Win32_VideoController
    $disks = Get-CimInstance Win32_DiskDrive
    $os = Get-CimInstance Win32_OperatingSystem

    $mfg = $cs.Manufacturer
    $model = $cs.Model
    $serial = $bios.SerialNumber
    $cpuName = ($proc | Select-Object -First 1).Name
    $cores = ($proc | Select-Object -First 1).NumberOfCores
    $threads = ($proc | Select-Object -First 1).NumberOfLogicalProcessors

    $totalRamBytes = 0
    $ramSpeed = 0
    $ramDetails = @()
    foreach ($m in $ramModules) {
        $totalRamBytes += $m.Capacity
        $ramSpeed = $m.Speed
        $sizeGb = [math]::Round($m.Capacity / 1GB, 1)
        $ramDetails += \"$($sizeGb)GB ($($m.Manufacturer) $($m.PartNumber.Trim()))\"
    }
    $totalRamGb = [math]::Round($totalRamBytes / 1GB, 1)

    Write-Host \"[MACHINE]      : $mfg $model\" -ForegroundColor Yellow
    Write-Host \"[SERIAL / BIOS]: Serial: $serial | BIOS: $($bios.SMBIOSBIOSVersion)\" -ForegroundColor White
    Write-Host \"[OPERATING SYS]: $($os.Caption) ($($os.OSArchitecture)) Build $($os.BuildNumber)\" -ForegroundColor White
    Write-Host \"[PROCESSOR]    : $cpuName ($cores Cores / $threads Threads)\" -ForegroundColor White
    Write-Host \"[MEMORY (RAM)] : $totalRamGb GB at $ramSpeed MHz ($($ramModules.Count) module(s): $($ramDetails -join ', '))\" -ForegroundColor White

    Write-Host \"[GRAPHICS / GPU]:\" -ForegroundColor White
    foreach ($g in $gpus) {
        $vram = [math]::Round($g.AdapterRAM / 1MB, 0)
        Write-Host \"  -> $($g.Name) (Driver: $($g.DriverVersion), VRAM: $($vram) MB)\" -ForegroundColor Gray
    }

    Write-Host \"[STORAGE DRIVES]:\" -ForegroundColor White
    foreach ($d in $disks) {
        $szGb = [math]::Round($d.Size / 1GB, 1)
        Write-Host \"  -> $($d.Model) ($szGb GB - $($d.InterfaceType)) Status: $($d.Status)\" -ForegroundColor Gray
    }

    Write-Host \"[BATTERY STATUS]:\" -ForegroundColor White
    $bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
    if ($bat) {
        $statusStr = if ($bat.BatteryStatus -eq 2) { 'Plugged in & Charging' } else { 'On Battery / Discharging' }
        Write-Host \"  -> Charge: $($bat.EstimatedChargeRemaining)% ($statusStr)\" -ForegroundColor Gray
    } else {
        Write-Host \"  -> No internal battery detected (Desktop or AC power).\" -ForegroundColor Gray
    }

    Write-Host '======================================================================' -ForegroundColor Cyan
    Write-Host '  VERDICT: Hardware profile successfully extracted directly from system!' -ForegroundColor Green
    Write-Host '======================================================================' -ForegroundColor Cyan
    
    # Generate standalone HTML report
    $htmlPath = Join-Path $PSScriptRoot 'LaptopCheck_Report.html'
    $htmlContent = @\"
<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8'>
    <title>LaptopCheck Diagnostic - $mfg $model</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 2rem; }
        .card { max-width: 800px; margin: 0 auto; background: #1e293b; border-radius: 12px; padding: 2rem; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        h1 { color: #38bdf8; margin-top: 0; font-size: 1.6rem; }
        .row { display: flex; justify-content: space-between; padding: 0.75rem 0; border-bottom: 1px solid #334155; }
        .label { color: #94a3b8; font-weight: 600; width: 180px; }
        .val { color: #f1f5f9; font-weight: 500; flex: 1; }
        .badge { background: #059669; color: white; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem; font-weight: bold; }
    </style>
</head>
<body>
    <div class='card'>
        <div style='display:flex; justify-content:space-between; align-items:center;'>
            <h1>LaptopCheck Diagnostic</h1>
            <span class='badge'>REAL HARDWARE</span>
        </div>
        <p style='color:#94a3b8;'>Scan generated on $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
        <div class='row'><div class='label'>Machine:</div><div class='val'>$mfg $model</div></div>
        <div class='row'><div class='label'>Serial:</div><div class='val'>$serial</div></div>
        <div class='row'><div class='label'>OS:</div><div class='val'>$($os.Caption) $($os.OSArchitecture)</div></div>
        <div class='row'><div class='label'>Processor:</div><div class='val'>$cpuName ($cores Cores / $threads Threads)</div></div>
        <div class='row'><div class='label'>Memory (RAM):</div><div class='val'>$totalRamGb GB ($($ramModules.Count) modules at $ramSpeed MHz)</div></div>
        <div class='row'><div class='label'>Graphics:</div><div class='val'>$(($gpus | ForEach-Object { $_.Name }) -join ' | ')</div></div>
        <div class='row'><div class='label'>Storage:</div><div class='val'>$(($disks | ForEach-Object { \"$($_.Model) ($([math]::Round($_.Size/1GB, 0)) GB)\" }) -join ' | ')</div></div>
    </div>
</body>
</html>
\"@
    Set-Content -Path $htmlPath -Value $htmlContent -Encoding UTF8
    Write-Host \"Report saved to: $htmlPath\" -ForegroundColor Yellow
    Start-Process $htmlPath
}"

echo.
echo Press any key to exit...
pause >nul
