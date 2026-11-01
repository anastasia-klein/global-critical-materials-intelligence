# Reproduce and operate the warehouse

Use Python 3.12 and requirements-warehouse.lock.txt. Environment variables are explicitly exported; .env is not automatically loaded. Approved public IEA/Comext endpoints need no project credential. See .env.example for request budgets.

```sh
python -m ingestion plan
python -m ingestion run --data-root data/raw
python -m ingestion run --offline --data-root data/raw
python scripts/build_warehouse.py --data-root data/raw
```

Ingestion stores immutable source objects, request/attempt manifests, deterministic Bronze records, coverage summaries and a transactional SQLite lookup catalogue. Source payload hashes distinguish revisions. Offline replay preserves first acquisition timestamps. A failed or rejected attempt cannot replace an accepted snapshot.

A selected refresh can use `--source comext --reporters DE FR --years 2024`, restricted to the approved config. The pipeline supports bounded re-fetch and content deduplication, not an assumed upstream append-only change feed. A partial run cannot replace a complete analytical selection: complete the approved plan or explicitly build from a correspondingly reviewed bounded config. Edition, unit or label mismatches require inspection; they fail rather than enter analytics silently.

The build wrapper creates data/warehouse/gcm.duckdb and performs dbt build, source freshness and static docs generation. Temporary checks and build reports default to work/validation; dbt docs output is generated, not committed. Use `--historical-snapshot` only for deliberately fixed captures/CI; it skips time-relative freshness while retaining source timestamps. Keep a built database's basename when moving it, or rebuild its catalogue-qualified views.

```sh
python scripts/validate_business_metrics.py --database data/warehouse/gcm.duckdb --output work/validation/metrics.json
python scripts/check_quality_controls.py --database data/warehouse/gcm.duckdb --phase all --output work/validation/negative_controls.json
python scripts/validate_reporting_areas.py --database data/warehouse/gcm.duckdb --output work/validation/reporting_areas
python scripts/export_powerbi.py --database data/warehouse/gcm.duckdb --output dashboards/powerbi/data
python scripts/build_powerbi.py
python scripts/validate_powerbi.py --project dashboards/powerbi --database data/warehouse/gcm.duckdb --output work/validation/powerbi.json
python scripts/validate_powerbi_design.py --project dashboards/powerbi --output work/validation/presentation.json
```

Review the data/model diff together before committing refreshed report inputs. Export manifest fingerprints and CSVs are one atomic Git change. No database or large raw archive is required on the Windows VM. Its update script checks those fingerprints before opening Desktop.

The independent validator recomputes metrics from native facts with Decimal. Negative controls deliberately corrupt disposable copies and require the expected tests to fail; they never modify the accepted database. CI uses actual bounded source fixtures without live API calls. Local tests and hosted Actions runs are separate evidence.

Source records remain versioned; SCD2 dimensions are not invented for attributes without a justified historical requirement. Full analytical refresh is appropriate for the current bounded volume; source acquisition remains idempotent. See [grains](../architecture/model_grains.md), [metrics](../methodology/metrics.md) and [Bronze contract](../architecture/bronze_contract.md).
