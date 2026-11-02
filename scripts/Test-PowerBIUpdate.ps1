# Integration checks for the Windows working-copy preparation; no Desktop engine.
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$Update = Join-Path $PSScriptRoot 'Update-PowerBI.ps1'
$RuntimeRoot = Join-Path (Split-Path $PSScriptRoot -Parent) 'work/powerbi-desktop'
function Assert-Fonts {
    param($Node, [string]$Expected)
    if ($null -eq $Node -or $Node -is [string]) { return }
    if ($Node -is [pscustomobject]) {
        foreach ($Property in $Node.PSObject.Properties) {
            if ($Property.Name -in @('fontFamily','fontFace')) {
                $Actual = if ($Property.Value -is [string]) { $Property.Value } else { $Property.Value.expr.Literal.Value.Substring(1, $Property.Value.expr.Literal.Value.Length - 2).Replace("''", "'") }
                if ($Actual -ne $Expected) { throw "Font mismatch: $Actual" }
                $script:FontCount++
            } else { Assert-Fonts $Property.Value $Expected }
        }
    } elseif ($Node -is [System.Collections.IEnumerable]) {
        foreach ($Child in $Node) { Assert-Fonts $Child $Expected }
    }
}
foreach ($Family in @('Arial', "'Avenir Next', Arial, sans-serif")) {
    if ($Family -eq 'Arial') { & $Update -SkipPull -NoOpen -FontName Arial }
    else { & $Update -SkipPull -NoOpen }
    $Slug = if ($Family -eq 'Arial') { 'Arial' } else { 'Auto' }
    $Runtime = Get-ChildItem $RuntimeRoot -Directory | Where-Object { $_.Name.EndsWith('-' + $Slug) }
    if (@($Runtime).Count -ne 1) { throw 'Expected exactly one runtime for the font mode.' }
    $script:FontCount = 0
    foreach ($File in Get-ChildItem $Runtime.FullName -Recurse -File -Filter '*.json') {
        if ($File.FullName -match '[\\/]data[\\/]') { continue }
        Assert-Fonts (Get-Content $File.FullName -Raw | ConvertFrom-Json) $Family
    }
    if ($script:FontCount -lt 100) { throw 'Font expressions were not inspected.' }
    $Expression = Get-Content (Join-Path $Runtime.FullName 'GlobalCriticalMaterials.SemanticModel/definition/expressions.tmdl') -Raw
    if ($Expression -notmatch 'work/powerbi-desktop') { throw 'DataFolder is not local to the runtime.' }
}
$Supply = Join-Path $Runtime.FullName 'data/Supply.csv'
Add-Content -LiteralPath $Supply -Value 'corrupted runtime sentinel'
$Rejected = $false
try { & $Update -SkipPull -NoOpen } catch {
    if ($_.Exception.Message -notmatch 'Local Supply.csv differs') { throw }
    $Rejected = $true
}
if (-not $Rejected) { throw 'Corrupted reused runtime was accepted.' }
& $Update -SkipPull -NoOpen -FreshCopy
if ((Get-Content $Supply -Tail 1) -ne 'corrupted runtime sentinel') { throw 'The previous runtime was changed.' }
$Projects = @(Get-ChildItem $RuntimeRoot -Recurse -Filter GlobalCriticalMaterials.pbip)
if ($Projects.Count -ne 3) { throw 'FreshCopy did not preserve both previous runtimes.' }
$Dirty = git status --porcelain
if ($Dirty) { throw "Tracked source files changed: $Dirty" }
Write-Host 'Passed: default fallback, explicit Arial, native and plain fonts, local paths, CSV integrity, FreshCopy preservation and clean checkout.'
