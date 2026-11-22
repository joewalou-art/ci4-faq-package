# MongoDB 4.4 Crash Recovery - PowerShell wrapper (Windows)
#
# Designed to run on the Windows host that owns the data.
# Defaults match your environment:
#   Data path:  E:\Tam_data\4.4\data\
#   Log path:   E:\Tam_data\4.4\log\
#
# Usage (PowerShell, run as Administrator):
#   .\mongodb_recover.ps1                          # safe / report mode
#   .\mongodb_recover.ps1 -Execute                 # perform repair + dump
#   .\mongodb_recover.ps1 -Execute -DumpOnly       # only mongodump export
#   .\mongodb_recover.ps1 -DataPath "D:\mongo\data" -LogPath "D:\mongo\log"

[CmdletBinding()]
param(
    [string]$DataPath = "E:\Tam_data\4.4\data\",
    [string]$LogPath  = "E:\Tam_data\4.4\log\",
    [string]$MongoDBHome = $null,
    [switch]$Execute,
    [switch]$DumpOnly,
    [string]$BackupRoot = $null,
    [string]$DumpRoot   = $null
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) { $python = Get-Command python3 -ErrorAction SilentlyContinue }
if (-not $python) {
    Write-Error "Python is not on PATH. Install Python or run mongodb_recover.py directly."
    exit 1
}

$args = @("mongodb_recover.py",
          "--data-path", $DataPath,
          "--log-path",  $LogPath)
if ($MongoDBHome) { $args += @("--mongodb-home", $MongoDBHome) }
if ($Execute)     { $args += "--execute" }
if ($DumpOnly)    { $args += "--dump-only" }
if ($BackupRoot)  { $args += @("--backup-root", $BackupRoot) }
if ($DumpRoot)    { $args += @("--dump-root", $DumpRoot) }

Write-Host "=== MongoDB 4.4 Crash Recovery (PowerShell) ==="
Write-Host "Data path : $DataPath"
Write-Host "Log path  : $LogPath"
Write-Host "Mode      : $([bool]$Execute ? 'EXECUTE' : 'SAFE/REPORT')"
Write-Host ""

& $python $args
$exit = $LASTEXITCODE
Write-Host ""
Write-Host "Exit code: $exit"
exit $exit
