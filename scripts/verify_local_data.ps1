[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$DataRoot,

    [string]$TargetRoot = (Split-Path -Parent $PSScriptRoot)
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$sections = @('news', 'experiments', 'aggregated', 'prices', 'prices_extended')
$dataRootPath = [System.IO.Path]::GetFullPath($DataRoot)
$targetRootPath = [System.IO.Path]::GetFullPath($TargetRoot)

if (-not (Test-Path -LiteralPath $dataRootPath -PathType Container)) {
    throw "DataRoot does not exist or is not a directory: $dataRootPath"
}

if (-not (Test-Path -LiteralPath $targetRootPath -PathType Container)) {
    throw "TargetRoot does not exist or is not a directory: $targetRootPath"
}

$dataDirectory = Join-Path $targetRootPath 'data'
$failed = $false

foreach ($section in $sections) {
    $expected = Join-Path $dataRootPath $section
    $actual = Join-Path $dataDirectory $section

    if (-not (Test-Path -LiteralPath $expected -PathType Container)) {
        Write-Host "MISSING SOURCE  $section  $expected"
        $failed = $true
        continue
    }

    if (-not (Test-Path -LiteralPath $actual -PathType Container)) {
        Write-Host "MISSING TARGET  $section  $actual"
        $failed = $true
        continue
    }

    $item = Get-Item -LiteralPath $actual -Force
    $isLink = [bool]($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)
    if (-not $isLink) {
        Write-Host "LOCAL DIRECTORY  $section  $actual"
        continue
    }

    $target = $item.Target
    if (-not $target) {
        Write-Host "UNRESOLVED LINK  $section  $actual"
        $failed = $true
        continue
    }

    $resolved = [System.IO.Path]::GetFullPath([string]$target)
    if ($resolved -ne $expected) {
        Write-Host "WRONG TARGET  $section  $actual -> $resolved (expected $expected)"
        $failed = $true
        continue
    }

    Write-Host "OK  $section  $actual -> $resolved"
}

if ($failed) {
    exit 1
}
