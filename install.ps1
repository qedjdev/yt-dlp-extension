$installDir = "$env:LOCALAPPDATA\yt-dlp-extension"
$hostName = "yt_dlp_host"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

New-Item -ItemType Directory -Path $installDir -Force | Out-Null

# Copy the frozen host executable
$srcExe = Join-Path $scriptDir "dist\host.exe"
if (-not (Test-Path $srcExe)) {
    $srcExe = Join-Path $scriptDir "host.exe"
}
if (-not (Test-Path $srcExe)) {
    Write-Host "Error: host.exe not found. Run build.py first or place host.exe next to this script." -ForegroundColor Red
    exit 1
}

Copy-Item $srcExe "$installDir\host.exe" -Force
Write-Host "Installed host.exe to: $installDir\host.exe"

# Write native messaging host manifest
$manifest = @{
    name = $hostName
    description = "Native messaging host for yt-dlp downloads"
    path = "$installDir\host.exe"
    type = "stdio"
    allowed_extensions = @("yt-dlp-dl@wakefield.fyi")
} | ConvertTo-Json

$manifestPath = "$installDir\$hostName.json"
$manifest | Out-File -FilePath $manifestPath -Encoding utf8
Write-Host "Wrote host manifest to: $manifestPath"

# Set registry key
$regPath = "HKCU:\SOFTWARE\Mozilla\NativeMessagingHosts\$hostName"
if (-not (Test-Path (Split-Path $regPath))) {
    New-Item -Path "HKCU:\SOFTWARE\Mozilla\NativeMessagingHosts" -Force | Out-Null
}
New-Item -Path $regPath -Force | Out-Null
Set-ItemProperty -Path $regPath -Name "(Default)" -Value $manifestPath

Write-Host "Registry key set: $regPath"
Write-Host ""
Write-Host "Installation complete! Restart Firefox for changes to take effect." -ForegroundColor Green
