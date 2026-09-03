[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string]$DataRoot,

    [string]$TargetRoot = (Split-Path -Parent $PSScriptRoot),

    [switch]$ForceReplace
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

foreach ($section in $sections) {
    $source = Join-Path $dataRootPath $section
    if (-not (Test-Path -LiteralPath $source -PathType Container)) {
        throw "DataRoot is missing required section '$section': $source"
    }
}

$dataDirectory = Join-Path $targetRootPath 'data'
if (-not (Test-Path -LiteralPath $dataDirectory)) {
    New-Item -ItemType Directory -Path $dataDirectory | Out-Null
}

foreach ($section in $sections) {
    $source = Join-Path $dataRootPath $section
    $destination = Join-Path $dataDirectory $section

    if (Test-Path -LiteralPath $destination) {
        $item = Get-Item -LiteralPath $destination -Force
        $isLink = [bool]($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint)

        if ($isLink) {
            $target = $item.Target
            if ($target -and ([System.IO.Path]::GetFullPath([string]$target) -eq $source)) {
                Write-Host "Already linked: $destination -> $source"
                continue
            }
            throw "Destination is already a junction or link with a different target: $destination"
        }

        $children = @(Get-ChildItem -LiteralPath $destination -Force)
        if ($children.Count -gt 0) {
            throw "Refusing to replace non-empty local directory: $destination"
        }

        if (-not $ForceReplace) {
            throw "Destination is an empty local directory. Re-run with -ForceReplace to replace it: $destination"
        }

        Remove-Item -LiteralPath $destination -Force
    }

    New-Item -ItemType Junction -Path $destination -Target $source | Out-Null
    Write-Host "Linked: $destination -> $source"
}
