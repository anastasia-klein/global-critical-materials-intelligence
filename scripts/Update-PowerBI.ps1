[CmdletBinding()]
param(
    [string]$FontName = '',
    [switch]$SkipPull,
    [switch]$NoOpen,
    [switch]$FreshCopy
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path

function Invoke-RepositoryGit {
    param([string[]]$GitArguments)
    $Result = & git -C $RepoRoot @GitArguments
    if ($LASTEXITCODE -ne 0) { throw "Git failed: $($GitArguments -join ' ')" }
    return $Result
}

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw 'Install Git for Windows first.' }
if (Get-Process -Name PBIDesktop -ErrorAction SilentlyContinue) {
    throw 'Save your work and close Power BI Desktop before updating.'
}
if (-not $SkipPull) {
    $Branch = [string](Invoke-RepositoryGit -GitArguments @('branch', '--show-current'))
    if ($Branch.Trim() -ne 'main') { throw 'Switch the checkout to main before updating.' }
    $Changes = Invoke-RepositoryGit -GitArguments @('status', '--porcelain')
    if ($Changes) { throw 'The checkout has local changes. Commit or preserve them before pulling; nothing was discarded.' }
    Invoke-RepositoryGit -GitArguments @('pull', '--ff-only') | Write-Host
}
$Commit = ([string](Invoke-RepositoryGit -GitArguments @('rev-parse', '--short=12', 'HEAD'))).Trim()
$Source = (Resolve-Path (Join-Path $RepoRoot 'dashboards/powerbi')).Path
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$ManifestPath = Join-Path $Source 'data/export_manifest.json'
$Manifest = [System.IO.File]::ReadAllText($ManifestPath, $Utf8) | ConvertFrom-Json
$TableCount = 0
foreach ($Table in $Manifest.tables.PSObject.Properties) {
    if ($Table.Name -notmatch '^[A-Za-z][A-Za-z0-9_]*$') { throw 'Invalid table name in export manifest.' }
    $CsvPath = Join-Path $Source ('data/' + $Table.Name + '.csv')
    if (-not (Test-Path -LiteralPath $CsvPath -PathType Leaf)) { throw "Missing report input: $CsvPath" }
    $Actual = (Get-FileHash -LiteralPath $CsvPath -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Actual -ne ([string]$Table.Value.sha256).ToLowerInvariant()) { throw "Fingerprint mismatch: $($Table.Name).csv" }
    $TableCount++
}
# A shared report must keep its reader-side font fallback chain on publication.
$FontStack = "'Avenir Next', Arial, sans-serif"
if ([string]::IsNullOrWhiteSpace($FontName)) {
    $EffectiveFont = $FontStack
    $SafeFont = 'Auto'
} else {
    Add-Type -AssemblyName System.Drawing
    $FontCollection = New-Object System.Drawing.Text.InstalledFontCollection
    try { $InstalledFonts = @($FontCollection.Families | ForEach-Object { $_.Name }) }
    finally { $FontCollection.Dispose() }
    if ($InstalledFonts -notcontains $FontName) { throw "Font '$FontName' is not installed. Omit -FontName to keep the shared font fallback chain." }
    $EffectiveFont = $FontName
    $SafeFont = $FontName -replace '[^A-Za-z0-9_-]', '_'
}
function Set-ReportFont {
    param($Node, [string]$Family)
    if ($null -eq $Node -or $Node -is [string]) { return }
    if ($Node -is [pscustomobject]) {
        foreach ($Property in $Node.PSObject.Properties) {
            if ($Property.Name -in @('fontFamily', 'fontFace')) {
                if ($Property.Value -is [string]) { $Property.Value = $Family }
                elseif ($null -ne $Property.Value.expr.Literal) {
                    $Property.Value.expr.Literal.Value = "'" + $Family.Replace("'", "''") + "'"
                }
            } else { Set-ReportFont -Node $Property.Value -Family $Family }
        }
    } elseif ($Node -is [System.Collections.IEnumerable]) {
        foreach ($Child in $Node) { Set-ReportFont -Node $Child -Family $Family }
    }
}
$RuntimeRoot = Join-Path $RepoRoot 'work/powerbi-desktop'
$Runtime = Join-Path $RuntimeRoot ($Commit + '-' + $SafeFont)
if ($FreshCopy) { $Runtime += '-' + [guid]::NewGuid().ToString('N').Substring(0,8) }
$Stamp = Join-Path $Runtime '.source-commit'
$ProjectPath = Join-Path $Runtime 'GlobalCriticalMaterials.pbip'
if (-not (Test-Path -LiteralPath $Runtime)) {
    New-Item -ItemType Directory -Path $RuntimeRoot -Force | Out-Null
    $Stage = Join-Path $RuntimeRoot ('.partial-' + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Stage | Out-Null
    foreach ($File in Get-ChildItem -LiteralPath $Source -Recurse -File) {
        $Relative = $File.FullName.Substring($Source.Length + 1)
        if ($Relative -match '(^|[\\/])\.pbi([\\/]|$)' -or $File.Extension -eq '.pbix') { continue }
        $Destination = Join-Path $Stage $Relative
        New-Item -ItemType Directory -Path (Split-Path -Parent $Destination) -Force | Out-Null
        [System.IO.File]::Copy($File.FullName, $Destination, $false)
    }
    foreach ($File in Get-ChildItem -LiteralPath $Stage -Recurse -File -Filter '*.json') {
        if ($File.FullName -match '[\\/]data[\\/]') { continue }
        $Json = [System.IO.File]::ReadAllText($File.FullName, $Utf8) | ConvertFrom-Json
        Set-ReportFont -Node $Json -Family $EffectiveFont
        [System.IO.File]::WriteAllText($File.FullName, ($Json | ConvertTo-Json -Depth 100), $Utf8)
    }
    [System.IO.File]::WriteAllText((Join-Path $Stage '.source-commit'), $Commit + "`n", $Utf8)
    Move-Item -LiteralPath $Stage -Destination $Runtime
}
if (-not (Test-Path -LiteralPath $Stamp) -or -not (Test-Path -LiteralPath $ProjectPath)) { throw 'Incomplete local runtime; inspect its folder before retrying.' }
if ([System.IO.File]::ReadAllText($Stamp, $Utf8).Trim() -ne $Commit) { throw 'Local runtime commit stamp differs from the checkout.' }
# Reused runtime inputs must match the selected source commit, not merely exist.
foreach ($Table in $Manifest.tables.PSObject.Properties) {
    $RuntimeCsv = Join-Path $Runtime ('data/' + $Table.Name + '.csv')
    if (-not (Test-Path -LiteralPath $RuntimeCsv -PathType Leaf)) { throw 'Local report inputs are incomplete. Run this script with -FreshCopy; the existing copy will be preserved.' }
    $Actual = (Get-FileHash -LiteralPath $RuntimeCsv -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($Actual -ne ([string]$Table.Value.sha256).ToLowerInvariant()) { throw "Local $($Table.Name).csv differs from the selected commit. Run with -FreshCopy to preserve it and open a new copy." }
}
# Configure only the ignored runtime copy; tracked source files stay untouched.
& (Join-Path $Runtime 'Configure-DataFolder.ps1')
$TrackedChanges = Invoke-RepositoryGit -GitArguments @('status', '--porcelain', '--untracked-files=no')
if ($TrackedChanges) {
    throw 'Tracked source files changed unexpectedly; Desktop was not opened.'
}
Write-Host "Verified $TableCount CSV inputs. Commit: $Commit. Font: $EffectiveFont."
Write-Host "Working project: $ProjectPath"
Write-Host 'Select Refresh after opening the project in Power BI Desktop.'
if (-not $NoOpen) { Start-Process -FilePath $ProjectPath }
