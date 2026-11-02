# Power BI on a Windows VM

## Requirements and first run

Use Git for Windows, Power BI Desktop with PBIP/PBIR/TMDL support, and Windows PowerShell 5.1 or PowerShell 7. The project is maintained as plain-text definitions; a binary PBIX is not the Git source of truth. See [Microsoft's project documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

```powershell
git clone https://github.com/anastasia-klein/global-critical-materials-intelligence.git
cd global-critical-materials-intelligence
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Update-PowerBI.ps1
```

The process-only execution policy does not change saved Windows policies. Follow organisation-managed restrictions if they disallow local scripts.

## Update

Close Power BI Desktop, then invoke the same script. It:

1. Requires a clean repository on main and runs `git pull --ff-only`.
2. Verifies every CSV fingerprint from the committed export manifest.
3. Creates `work/powerbi-desktop/<commit>-<font>/` from the report and model folders.
4. Sets DataFolder to that working copy's absolute data directory.
5. Opens GlobalCriticalMaterials.pbip. Select Refresh in Desktop.

The checkout's tracked parameter is never edited. Different source commits get different runtime folders, preserving existing local working copies. Reopening the same commit reuses its folder; Desktop edits there are local and are not automatically transferred to a later source commit. Make product changes in the source project and review/commit them through Git.

A dirty checkout or non-fast-forward branch causes a clear failure; the script does not discard changes, reset a branch or merge automatically. Local caches and working copies are ignored by Git. Raw downloaded data and warehouse files are not required on the VM.

Optional switches:

```powershell
# Explicit font installed on this VM
.\scripts\Update-PowerBI.ps1 -FontName 'Avenir Next LT Pro'
# Build the working copy without opening Desktop
.\scripts\Update-PowerBI.ps1 -NoOpen
# Prepare the currently checked-out commit without network access
.\scripts\Update-PowerBI.ps1 -SkipPull -NoOpen
```

By default the published report retains the reader-side font chain `'Avenir Next', Arial, sans-serif`. The reader's available fonts determine the rendering, so the same report URL supports Avenir Next on Mac and Arial on Windows. An explicit `-FontName Arial` forces Arial for all readers; omit it for the shared fallback chain. Explicit families must be installed. Both native font expressions and textbox/theme font strings are configured. Fonts are not embedded in the Power BI project or distributed in Git.

## Native acceptance checks

Static checks have passed; native Desktop rendering and DAX execution must be checked separately:

- All 24 imported CSV tables refresh; no path, relationship or measure errors.
- All six square material tiles are visible with full names and correct states/colours; KPI ranges fit. Hover/click each material tile in the published reading view: corner numbers stay visible with no grey text scrollbars.
- At Fit to page, no visual requires scrolling. Import partners keep the alphabetical reference order and Other partners last. End uses keep all eight categories.
- Compare Germany / Li carbonates / 2024 / EUR with the source query: imports, exports, Chile/Belgium/US shares and supplier HHI.
- Switch every reporter, basis and material. EU27 remains external-only; national totals include intra-EU. Multiple product/reporter selections must not create sums of incompatible scopes.
- On risk, clear material selection to compare all six. Mining/refining bars show lower HHI; upper bounds are in tooltips. The square 0–1 scatter compares concentration, not physical shortage.
- On outlook, each KPI and demand chart shows CPS, STEPS and HDS with the same fixed colours. There is no scenario selector. The year is a single-row button choice; the single All grades button is below C (green when selected; deselect to restore Graphite). Cobalt/grid storage retains reported 0. A source-missing category remains blank/dash with the status tooltip. Graphite scope changes do not affect other material families. Supply stops at 2040; demand extends to 2050.
- The combined map shows separate circles in two stage colours, not pies. Offsets of ±3° are display-only; they are not facility coordinates. Nearby circles may overlap. Other countries is excluded.

The preview PNGs are design previews, not proof of Desktop acceptance. No automatic Service publication is performed by this workflow.

Pulling updates the source checkout and prepares a Desktop copy. It does not replace the already published Power BI Service report. Refresh and publish the updated report from Desktop to make the new version visible in the Service.

Working-copy inputs are verified against the selected commit on every launch, including reused folders. To open a fresh copy while preserving an older runtime, run `powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Update-PowerBI.ps1 -FreshCopy`. The Supply import derives the presentation-only MapPoint from Country and Stage if an older CSV lacks it; other required fields must still be present. Refresh the model after opening the new copy, then publish and replace the existing report to retain its URL. Pulling Git alone does not update a published report.
