# Setup and reproduction

## Explore the published report

Open the public Power BI report from the [project README](../README.md). No local installation is needed to explore it. [Report interpretation](methodology/report_interpretation.md) explains scope, residual groups, HHI and scenarios.

## Open the Power BI source project

Use Git, Power BI Desktop on Windows with PBIP/PBIR/TMDL support, and Windows PowerShell 5.1 or PowerShell 7:

```powershell
git clone https://github.com/anastasia-klein/global-critical-materials-intelligence.git
cd global-critical-materials-intelligence
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\Update-PowerBI.ps1
```

The script verifies the included CSV inputs, configures local file paths and opens a separate project copy. Select **Refresh** to load the data. Python and DuckDB are needed only to rebuild the analytical pipeline. See [Power BI setup](operations/powerbi.md) for updates, saving edits and validation.

## Rebuild the analytical pipeline

Use Python 3.12. From the repository root, create an environment and install locked dependencies:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-warehouse.lock.txt
```

On Windows, activate it with `.\.venv\Scripts\Activate.ps1` instead of `source`. Then run:

```sh
python -m ingestion plan
python -m ingestion run --data-root data/raw
python scripts/build_warehouse.py --data-root data/raw
python scripts/export_powerbi.py --database data/warehouse/gcm.duckdb --output dashboards/powerbi/data
python scripts/build_powerbi.py
```

Live APIs can revise their data. Re-fetching creates a new capture; it does not guarantee identical historical bytes. The committed CSVs and fingerprints preserve the distributed report capture. Full raw archives and databases are excluded from Git. [Warehouse operations](operations/warehouse.md) cover replay, bounded refresh, source contracts and historical snapshots.

## Reproduce the documented findings

With the warehouse dependencies installed:

```sh
python scripts/run_findings.py
```

This verifies the committed CSV fingerprints and executes [the findings SQL](business_insights/findings.sql) in an in-memory DuckDB database. It needs neither a live API request nor the full warehouse. [Findings](business_insights/findings.md) link results to the actual report screenshots and filter settings; [captured query results](validation/findings_results.json) record the documented values.

## Run offline checks

```sh
python -B -m unittest discover -s tests -v
python scripts/create_ci_capture.py --output work/ci
python scripts/build_warehouse.py --data-root work/ci/capture --config work/ci/fixture_config.json --database work/ci/ci.duckdb --output work/ci/evidence --historical-snapshot
python scripts/validate_business_metrics.py --database work/ci/ci.duckdb --output work/ci/evidence/metrics.json
```

CI also checks deliberate business-rule failures, portable report definitions and the Windows setup script. Disposable outputs stay under `work/`; CI does not refresh the committed report capture from live APIs. Static checks do not execute DAX or the native rendering engine; use the [Power BI validation checklist](operations/powerbi.md) after model or report changes.
