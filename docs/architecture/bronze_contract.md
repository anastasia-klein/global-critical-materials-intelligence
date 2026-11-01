# Bronze record contract

One record identifies a native observation within one request-specific immutable payload. Historical revisions remain different snapshots. This is source preservation and decoding, not harmonised Silver data.

| Field | JSON type | Meaning |
| --- | --- | --- |
| record_id | string | SHA-256 identity over snapshot ID and source locator |
| source | string | iea or comext |
| request_id | string | Stable source/canonical-URL identity |
| snapshot_id | string | Stable request/payload-hash identity |
| source_locator | string | IEA array index or JSON-stat value/status offset in the original body |
| payload_sha256 | string | Original byte fingerprint |
| source_object_path | string | Relative immutable object path in the capture store |
| ingested_at_utc | string | First retrieval time for that request and payload; replay does not create new source freshness |
| source_record | object | Original IEA record, or a decoded native Comext coordinate/value/status cell |

IEA source records retain their exact edition, scenario, category, unit, geography label, product, reference year, material definition, case, numeric value and flow. Unknown additive fields are preserved and reported; required-field/type/edition changes fail validation.

Comext decoded cells retain native coordinates, source labels, numeric or null value, observation status, source offset, dataset code and source update time. A returned null cell is tagged explicit_null; a status without a value is tagged status_without_value. Sparse combinations absent from both maps are counted in coverage and are not synthesised as records or zeroes. The complete JSON-stat structure and original maps remain in the immutable source object.

Native units and values are not converted into contained metal. No country is reassigned to a successor, no trade partner is inferred to be the mine origin, no case is copied into another scenario and no missing value is estimated. Source aggregation rows are retained for reconciliation and must be filtered explicitly in later facts/marts.

The DuckDB loader preserves the native JSON record, original object reference and immutable selected-snapshot lineage.
