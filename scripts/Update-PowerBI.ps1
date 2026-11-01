[CmdletBinding()]
param(
    [string]$FontName = '',
    [switch]$SkipPull,
    [switch]$NoOpen
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
Add-Type -AssemblyName System.Drawing
$FontCollection = New-Object System.Drawing.Text.InstalledFontCollection
try { $InstalledFonts = @($FontCollection.Families | ForEach-Object { $_.Name }) }
finally { $FontCollection.Dispose() }
if ([string]::IsNullOrWhiteSpace($FontName)) {
    if ($InstalledFonts -contains 'Avenir Next') { $FontName = 'Avenir Next' } else { $FontName = 'Arial' }
}
if ($InstalledFonts -notcontains $FontName) { throw "Font '$FontName' is not installed. Install it or omit -FontName for automatic selection." }
$SafeFont = $FontName -replace '[^A-Za-z0-9_-]', '_'
$RuntimeRoot = Join-Path $RepoRoot 'work/powerbi-desktop'
$Runtime = Join-Path $RuntimeRoot ($Commit + '-' + $SafeFont)
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
    if ($FontName -ne 'Avenir Next') {
        $JsonFont = ConvertTo-Json -InputObject $FontName -Compress
        foreach ($File in Get-ChildItem -LiteralPath $Stage -Recurse -File -Filter '*.json') {
            if ($File.FullName -match '[\\/]data[\\/]') { continue }
            $Content = [System.IO.File]::ReadAllText($File.FullName, $Utf8)
            $Content = $Content.Replace('"Avenir Next"', $JsonFont)
            [System.IO.File]::WriteAllText($File.FullName, $Content, $Utf8)
        }
    }
    [System.IO.File]::WriteAllText((Join-Path $Stage '.source-commit'), $Commit + "`n", $Utf8)
    Move-Item -LiteralPath $Stage -Destination $Runtime
}
if (-not (Test-Path -LiteralPath $Stamp) -or -not (Test-Path -LiteralPath $ProjectPath)) { throw 'Incomplete local runtime; inspect its folder before retrying.' }
if ([System.IO.File]::ReadAllText($Stamp, $Utf8).Trim() -ne $Commit) { throw 'Local runtime commit stamp differs from the checkout.' }
# Configure only the ignored runtime copy; tracked source files stay untouched.
& (Join-Path $Runtime 'Configure-DataFolder.ps1')
$TrackedChanges = Invoke-RepositoryGit -GitArguments @('status', '--porcelain', '--untracked-files=no')
if ($TrackedChanges) {
    throw 'Tracked source files changed unexpectedly; Desktop was not opened.'
}
Write-Host "Verified $TableCount CSV inputs. Commit: $Commit. Font: $FontName."
Write-Host "Working project: $ProjectPath"
Write-Host 'Select Refresh after opening the project in Power BI Desktop.'
if (-not $NoOpen) { Start-Process -FilePath $ProjectPath }
