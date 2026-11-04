# Power BI setup and validation

## Requirements

To view the published report, follow the link in the [project README](../../README.md). To edit the source, use Git, Power BI Desktop with PBIP/PBIR/TMDL support, and Windows PowerShell 5.1 or PowerShell 7. The report and semantic model are versioned as text definitions. See [Microsoft’s project documentation](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview).

## Open the project

```powershell
git clone https://github.com/anastasia-klein/global-critical-materials-intelligence.git
cd global-critical-materials-intelligence
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Update-PowerBI.ps1
```

The script checks CSV fingerprints against the export manifest, prepares a separate local copy under `work/powerbi-desktop/`, configures its `DataFolder` parameter and opens `GlobalCriticalMaterials.pbip`. Select **Refresh** to load the included CSVs. Python and the warehouse are required only when rebuilding the analytical pipeline.

The execution-policy option applies to this PowerShell process only. Organisation-managed script policies still apply.

## Update and save changes

Close Power BI Desktop and run the same command to pull the latest source and open its local copy. The script stops if the checkout contains uncommitted changes or cannot be updated with a fast-forward pull.

Desktop edits are saved in the opened local copy. To retain them in Git, copy the intended report/model definition changes into `dashboards/powerbi/`, inspect the diff and commit the relevant files. Local caches and working folders are ignored by Git. Preserve any edits before preparing a newer copy.

Useful options:

```powershell
# Prepare the checked-out version without pulling or opening Desktop
.\scripts\Update-PowerBI.ps1 -SkipPull -NoOpen
# Prepare a fresh copy while preserving existing local copies
.\scripts\Update-PowerBI.ps1 -FreshCopy
# Use Arial explicitly
.\scripts\Update-PowerBI.ps1 -FontName Arial
```

The default font configuration requests Avenir Next with Arial as a fallback. Rendering depends on the fonts supported by the viewing environment. Font files are not distributed with the project.

## Validate and publish

Automated checks validate project schemas, field references, presentation contracts and exported values against SQL results. They do not execute the Power BI rendering engine or DAX; check the following in Desktop and the published report after substantive changes:

- All 24 CSV tables refresh without path, relationship or measure errors.
- Material, reporting-area, basis and year filters retain their intended scopes; graphite definitions remain separate.
- Germany / lithium carbonates / 2024 / EUR agrees with the reproducible queries for imports, exports, partner shares and HHI.
- Country shares, including Other countries, sum to 100% per available stage panel before rounding; map points represent identified countries only.
- Risk visuals compare physical-output concentration for mining/refining, while the trade table distinguishes EUR and product-mass concentration.
- Scenario colours and end-use ordering remain consistent; reported zeroes and missing observations stay distinct.
- Labels, cards, map interactions and navigation remain readable in the published report.

Refreshing the source project does not update Power BI Service. Publish and replace the existing report from Desktop to update the published version. Review the [licensing requirements](../sources/licensing.md) before publishing a new source capture.

The committed PNGs are SQL-derived design previews, not native screenshots. The published report and repository may have different update times; record the source capture when interpreting results.
