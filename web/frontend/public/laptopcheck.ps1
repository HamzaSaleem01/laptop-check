# LaptopCheck - One-Liner PowerShell Hardware Diagnostic
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  LAPTOPCHECK v1.0.0 - INSTANT REAL HARDWARE SCANNER" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan

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
    $ramDetails += "$($sizeGb)GB ($($m.Manufacturer) $($m.PartNumber.Trim()))"
}
$totalRamGb = [math]::Round($totalRamBytes / 1GB, 1)

Write-Host "[MACHINE]       : $mfg $model" -ForegroundColor Yellow
Write-Host "[SERIAL / BIOS] : Serial: $serial | BIOS: $($bios.SMBIOSBIOSVersion)" -ForegroundColor White
Write-Host "[OPERATING SYS] : $($os.Caption) ($($os.OSArchitecture))" -ForegroundColor White
Write-Host "[PROCESSOR]     : $cpuName ($cores Cores / $threads Threads)" -ForegroundColor White
Write-Host "[MEMORY (RAM)]  : $totalRamGb GB at $ramSpeed MHz ($($ramModules.Count) modules: $($ramDetails -join ', '))" -ForegroundColor White

Write-Host "[GRAPHICS / GPU]:" -ForegroundColor White
foreach ($g in $gpus) {
    $vram = [math]::Round($g.AdapterRAM / 1MB, 0)
    Write-Host "  -> $($g.Name) (Driver: $($g.DriverVersion), VRAM: $($vram) MB)" -ForegroundColor Gray
}

Write-Host "[STORAGE DRIVES]:" -ForegroundColor White
foreach ($d in $disks) {
    $szGb = [math]::Round($d.Size / 1GB, 1)
    Write-Host "  -> $($d.Model) ($szGb GB - $($d.InterfaceType)) Status: $($d.Status)" -ForegroundColor Gray
}

Write-Host "[BATTERY STATUS]:" -ForegroundColor White
$bat = Get-CimInstance Win32_Battery -ErrorAction SilentlyContinue
if ($bat) {
    $statusStr = if ($bat.BatteryStatus -eq 2) { 'Plugged in & Charging' } else { 'On Battery / Discharging' }
    Write-Host "  -> Charge: $($bat.EstimatedChargeRemaining)% ($statusStr)" -ForegroundColor Gray
} else {
    Write-Host "  -> No internal battery detected (Desktop or AC power)." -ForegroundColor Gray
}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  SCAN COMPLETE - 100% REAL HARDWARE EXTRACTED SAFELY" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
