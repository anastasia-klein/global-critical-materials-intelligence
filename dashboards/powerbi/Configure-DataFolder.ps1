# Optional local helper. Does not change PowerShell execution policy.
$projectFolder = $PSScriptRoot
$dataFolder = (Join-Path $projectFolder 'data').Replace('\','/').Replace('"','""')
$expressionFile = Join-Path $projectFolder 'GlobalCriticalMaterials.SemanticModel/definition/expressions.tmdl'
$content = [System.IO.File]::ReadAllText($expressionFile)
$lines = $content -split "`r?`n"
$lines[0] = 'expression DataFolder = "' + $dataFolder + '" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'
[System.IO.File]::WriteAllText($expressionFile, ($lines -join "`n"), [System.Text.UTF8Encoding]::new($false))
Write-Output 'DataFolder configured. Open GlobalCriticalMaterials.pbip and refresh in Power BI Desktop.'
