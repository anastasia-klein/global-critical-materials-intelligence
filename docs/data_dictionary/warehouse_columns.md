# DuckDB warehouse column dictionary

Derived from the executed model schemas and reviewed column definitions. Nullable source values remain nullable.

| Model | Column | DuckDB type | Meaning |
| --- | --- | --- | --- |
| stg_iea_observations | record_id | VARCHAR | Deterministic identity of a source observation within a selected immutable snapshot. |
| stg_iea_observations | request_id | VARCHAR | Stable source and canonical-query identity; not a source revision. |
| stg_iea_observations | snapshot_id | VARCHAR | Request plus original response-byte hash; all source revisions remain separately addressable. |
| stg_iea_observations | payload_sha256 | VARCHAR | SHA-256 of the unchanged original source response bytes. |
| stg_iea_observations | source_locator | VARCHAR | Original IEA array index or Comext JSON-stat value/status offset. |
| stg_iea_observations | ingested_at_utc | TIMESTAMP WITH TIME ZONE | First ingestion time of this request/payload; replays do not refresh it. |
| stg_iea_observations | source_release | VARCHAR | Native IEA model edition or Comext published revision timestamp. |
| stg_iea_observations | edition | VARCHAR | Exact IEA model edition; scenarios from different editions must not be merged. |
| stg_iea_observations | material_definition | VARCHAR | Exact native IEA definition, including separate Graphite and Graphite: all grades. |
| stg_iea_observations | scenario_name | VARCHAR | Exact source scenario name; no scenario substitution or cloning. |
| stg_iea_observations | case_name | VARCHAR | Exact technology/project case, distinct from the scenario. |
| stg_iea_observations | category | VARCHAR | Native Material demand or Material supply category. |
| stg_iea_observations | native_flow | VARCHAR | Native IDLE demand, Mining or Refining flow; not an inferred trade direction. |
| stg_iea_observations | geography_native | VARCHAR | Unchanged IEA geography label, including World and Other countries. |
| stg_iea_observations | end_use_native | VARCHAR | Unchanged source product/end-use label; demand end uses must retain scope. |
| stg_iea_observations | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| stg_iea_observations | native_unit | VARCHAR | Unchanged native unit; inspected IEA values are Thousand tonnes. |
| stg_iea_observations | native_value | DOUBLE | Original source numeric observation, nullable; missing is never replaced with zero. |
| stg_iea_observations | native_scope_tonnes | DOUBLE | IEA native value scaled by 1,000 only; the equivalent material basis remains unverified. |
| stg_iea_observations | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| stg_iea_observations | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| stg_iea_observations | conversion_status | VARCHAR | Applied physical scale conversion, separate from semantic equivalence. |
| stg_comext_cells | record_id | VARCHAR | Deterministic identity of a source observation within a selected immutable snapshot. |
| stg_comext_cells | request_id | VARCHAR | Stable source and canonical-query identity; not a source revision. |
| stg_comext_cells | snapshot_id | VARCHAR | Request plus original response-byte hash; all source revisions remain separately addressable. |
| stg_comext_cells | payload_sha256 | VARCHAR | SHA-256 of the unchanged original source response bytes. |
| stg_comext_cells | source_locator | VARCHAR | Original IEA array index or Comext JSON-stat value/status offset. |
| stg_comext_cells | ingested_at_utc | TIMESTAMP WITH TIME ZONE | First ingestion time of this request/payload; replays do not refresh it. |
| stg_comext_cells | source_release | VARCHAR | Native IEA model edition or Comext published revision timestamp. |
| stg_comext_cells | dataset_code | VARCHAR | Native Eurostat dataset identifier DS-045409. |
| stg_comext_cells | reporter_native | VARCHAR | Unchanged source reporter code; current approved reporter is Germany DE. |
| stg_comext_cells | partner_native | VARCHAR | Unchanged source partner code; can be a country, territory, special code or aggregate. |
| stg_comext_cells | reporter_label | VARCHAR | Unchanged source reporter label including any historical scope notes. |
| stg_comext_cells | partner_label | VARCHAR | Unchanged source partner label; it does not establish upstream mine origin. |
| stg_comext_cells | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| stg_comext_cells | product_label | VARCHAR | Native source product description; annual concordance is not asserted. |
| stg_comext_cells | flow_code | VARCHAR | Native German reporter direction: 1 import, 2 export. |
| stg_comext_cells | indicator | VARCHAR | Native VALUE_IN_EUROS, QUANTITY_IN_100KG or SUPPLEMENTARY_QUANTITY indicator. |
| stg_comext_cells | frequency | VARCHAR | Annual source frequency A; no annual/monthly summation. |
| stg_comext_cells | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| stg_comext_cells | native_value | DOUBLE | Original source numeric observation, nullable; missing is never replaced with zero. |
| stg_comext_cells | source_status | VARCHAR | Unchanged observation status, nullable; absent flags do not certify an actual measurement. |
| stg_comext_cells | source_missingness | VARCHAR | Explicit source null or status without value when present; sparse absence is not manufactured. |
| stg_comext_cells | native_classification | VARCHAR | Native CN8 classification; reference-year product identities are kept separately. |
| stg_comext_cells | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| stg_comext_cells | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| stg_source_snapshots | snapshot_id | VARCHAR | Request plus original response-byte hash; all source revisions remain separately addressable. |
| stg_source_snapshots | source | VARCHAR | Source contract name iea or comext. |
| stg_source_snapshots | request_id | VARCHAR | Stable source and canonical-query identity; not a source revision. |
| stg_source_snapshots | payload_sha256 | VARCHAR | SHA-256 of the unchanged original source response bytes. |
| stg_source_snapshots | source_release | VARCHAR | Native IEA model edition or Comext published revision timestamp. |
| stg_source_snapshots | source_release_timestamp | TIMESTAMP WITH TIME ZONE | Native published dataset revision time; null when the source did not supply one. |
| stg_source_snapshots | first_retrieved_at_utc | TIMESTAMP WITH TIME ZONE | Original first acquisition timestamp from the accepted capture manifest. |
| stg_source_snapshots | run_id | VARCHAR | Complete selected acquisition run; a partial refresh cannot replace the warehouse selection. |
| stg_source_snapshots | validation_status | VARCHAR | Accepted or accepted_empty source-contract result; empty does not imply zero activity. |
| stg_source_snapshots | source_observations | INTEGER | Count of native observations returned for the snapshot, including explicit null/status cells. |
| stg_source_snapshots | licence_name | VARCHAR | Source-specific reuse terms; project code licensing does not replace these. |
| stg_source_snapshots | licence_url | VARCHAR | Authoritative source rights/attribution notice URL. |
| stg_source_snapshots | publication_status | VARCHAR | Publication conditions retained from the reviewed source contract. |
| stg_source_snapshots | request_url | VARCHAR | Exact public bounded source request URL, without credentials. |
| int_iea_observations | record_id | VARCHAR | Deterministic identity of a source observation within a selected immutable snapshot. |
| int_iea_observations | request_id | VARCHAR | Stable source and canonical-query identity; not a source revision. |
| int_iea_observations | snapshot_id | VARCHAR | Request plus original response-byte hash; all source revisions remain separately addressable. |
| int_iea_observations | payload_sha256 | VARCHAR | SHA-256 of the unchanged original source response bytes. |
| int_iea_observations | source_locator | VARCHAR | Original IEA array index or Comext JSON-stat value/status offset. |
| int_iea_observations | ingested_at_utc | TIMESTAMP WITH TIME ZONE | First ingestion time of this request/payload; replays do not refresh it. |
| int_iea_observations | source_release | VARCHAR | Native IEA model edition or Comext published revision timestamp. |
| int_iea_observations | edition | VARCHAR | Exact IEA model edition; scenarios from different editions must not be merged. |
| int_iea_observations | material_definition | VARCHAR | Exact native IEA definition, including separate Graphite and Graphite: all grades. |
| int_iea_observations | scenario_name | VARCHAR | Exact source scenario name; no scenario substitution or cloning. |
| int_iea_observations | case_name | VARCHAR | Exact technology/project case, distinct from the scenario. |
| int_iea_observations | category | VARCHAR | Native Material demand or Material supply category. |
| int_iea_observations | native_flow | VARCHAR | Native IDLE demand, Mining or Refining flow; not an inferred trade direction. |
| int_iea_observations | geography_native | VARCHAR | Unchanged IEA geography label, including World and Other countries. |
| int_iea_observations | end_use_native | VARCHAR | Unchanged source product/end-use label; demand end uses must retain scope. |
| int_iea_observations | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| int_iea_observations | native_unit | VARCHAR | Unchanged native unit; inspected IEA values are Thousand tonnes. |
| int_iea_observations | native_value | DOUBLE | Original source numeric observation, nullable; missing is never replaced with zero. |
| int_iea_observations | native_scope_tonnes | DOUBLE | IEA native value scaled by 1,000 only; the equivalent material basis remains unverified. |
| int_iea_observations | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| int_iea_observations | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| int_iea_observations | conversion_status | VARCHAR | Applied physical scale conversion, separate from semantic equivalence. |
| int_iea_observations | family_id | VARCHAR | Contextual material family identifier; not an additive physical quantity definition. |
| int_iea_observations | geography_id | VARCHAR | Canonical ISO area or source-qualified aggregate/residual/special-area identifier. |
| int_iea_observations | geography_entity_type | VARCHAR | Country/territory, World or opaque residual; residuals cannot be treated as a single country. |
| int_iea_observations | geography_mapping_status | VARCHAR | Reviewed mapping rule applied to the native source geography. |
| int_iea_observations | stage_code | VARCHAR | Mining or refining expected-output stage; not nameplate capacity. |
| int_iea_observations | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| int_iea_observations | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| int_iea_observations | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| int_iea_observations | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| int_iea_observations | period_key | VARCHAR | Annual reference-period identity. |
| int_iea_observations | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| int_iea_observations | end_use_key | VARCHAR | Native demand end-use identity. |
| int_iea_observations | quality_state | VARCHAR | Structural validation state; valid records may still have unresolved semantic gates. |
| int_trade_flows | snapshot_id | VARCHAR | Request plus original response-byte hash; all source revisions remain separately addressable. |
| int_trade_flows | request_id | VARCHAR | Stable source and canonical-query identity; not a source revision. |
| int_trade_flows | payload_sha256 | VARCHAR | SHA-256 of the unchanged original source response bytes. |
| int_trade_flows | source_release | VARCHAR | Native IEA model edition or Comext published revision timestamp. |
| int_trade_flows | reporter_native | VARCHAR | Unchanged source reporter code; current approved reporter is Germany DE. |
| int_trade_flows | partner_native | VARCHAR | Unchanged source partner code; can be a country, territory, special code or aggregate. |
| int_trade_flows | reporter_id | VARCHAR | Mapped reporter area identity; separate from source code. |
| int_trade_flows | partner_id | VARCHAR | Mapped partner area identity; special and aggregate members retain distinct identities. |
| int_trade_flows | partner_entity_type | VARCHAR | Partner area category; exclude aggregates when summing components. |
| int_trade_flows | reporter_mapping_status | VARCHAR | Reviewed source reporter-to-geography mapping rule. |
| int_trade_flows | partner_mapping_status | VARCHAR | Reviewed source partner-to-geography mapping rule. |
| int_trade_flows | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| int_trade_flows | product_label | VARCHAR | Native source product description; annual concordance is not asserted. |
| int_trade_flows | native_classification | VARCHAR | Native CN8 classification; reference-year product identities are kept separately. |
| int_trade_flows | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| int_trade_flows | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| int_trade_flows | flow_code | VARCHAR | Native German reporter direction: 1 import, 2 export. |
| int_trade_flows | family_id | VARCHAR | Contextual material family identifier; not an additive physical quantity definition. |
| int_trade_flows | product_form | VARCHAR | Specific traded form such as ore/concentrate, carbonate, oxide or finished magnet article. |
| int_trade_flows | definition_scope | VARCHAR | Explicit native material/product boundaries and incompatibilities. |
| int_trade_flows | basis | VARCHAR | Source-qualified traded-product quantity basis; not contained metal. |
| int_trade_flows | concordance_status | VARCHAR | Annual classification correspondence remains unverified; no predecessor product is spliced. |
| int_trade_flows | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| int_trade_flows | ingested_at_utc | TIMESTAMP WITH TIME ZONE | First ingestion time of this request/payload; replays do not refresh it. |
| int_trade_flows | trade_value_eur | DOUBLE | Native trade value in EUR for the selected product/reporter/partner/period/direction. |
| int_trade_flows | native_quantity_100kg | DOUBLE | Native Comext mass indicator; one unit represents 100 kg of the traded product. |
| int_trade_flows | supplementary_quantity | DOUBLE | Native supplementary observation when supplied; missing remains null and no generic mass conversion is permitted. |
| int_trade_flows | value_record_id | VARCHAR | Nullable original EUR-cell record ID; absence is not zero. |
| int_trade_flows | quantity_record_id | VARCHAR | Nullable original 100kg-cell record ID; absence is not zero. |
| int_trade_flows | supplementary_record_id | VARCHAR | Nullable original supplementary-cell record ID; absence is not zero. |
| int_trade_flows | value_source_status | VARCHAR | Unchanged source status for the EUR cell, nullable. |
| int_trade_flows | quantity_source_status | VARCHAR | Unchanged source status for the 100kg quantity cell, nullable. |
| int_trade_flows | supplementary_source_status | VARCHAR | Unchanged supplementary-cell source status; no generic mass unit inferred. |
| int_trade_flows | source_cell_count | BIGINT | Number of native indicator cells retained in this trade-flow pivot; duplicates are independently tested. |
| int_trade_flows | product_mass_tonnes | DOUBLE | Comext native 100kg quantity multiplied by 0.1; not contained metal mass. |
| int_trade_flows | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| int_trade_flows | conversion_status | VARCHAR | Applied physical scale conversion, separate from semantic equivalence. |
| int_trade_flows | trade_flow_key | VARCHAR | Snapshot/reporter/partner/product/reference-year/flow identity; independent indicator cells are preserved. |
| int_trade_flows | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| int_trade_flows | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| int_trade_flows | reporter_key | VARCHAR | Reporting geography role key. |
| int_trade_flows | partner_key | VARCHAR | Trade partner geography role key, including flagged aggregates/special categories. |
| int_trade_flows | period_key | VARCHAR | Annual reference-period identity. |
| int_trade_flows | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| int_trade_flows | quality_state | VARCHAR | Structural validation state; valid records may still have unresolved semantic gates. |
| dim_material | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| dim_material | family_id | VARCHAR | Contextual material family identifier; not an additive physical quantity definition. |
| dim_material | material_family | VARCHAR | Contextual material family label; compatible native definitions/products remain separate. |
| dim_material | definition_note | VARCHAR | Non-additivity and scope note for the contextual family. |
| dim_material_definition | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| dim_material_definition | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| dim_material_definition | native_material | VARCHAR | Exact IEA material definition, not a harmonised all-forms material total. |
| dim_material_definition | definition_scope | VARCHAR | Explicit native material/product boundaries and incompatibilities. |
| dim_material_definition | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| dim_geography | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| dim_geography | geography_id | VARCHAR | Canonical ISO area or source-qualified aggregate/residual/special-area identifier. |
| dim_geography | canonical_name | VARCHAR | Reference geography name; native source labels remain in mapping/staging. |
| dim_geography | iso_alpha2 | VARCHAR | ISO 3166 alpha-2 when assigned; Namibia NA is preserved, special/residual categories remain null. |
| dim_geography | iso_alpha3 | VARCHAR | ISO 3166 alpha-3 when assigned; no invented code for Kosovo, World or residuals. |
| dim_geography | entity_type | VARCHAR | Country_or_territory, world, residual, regional aggregate, special partner or source geopolitical area. |
| dim_period | period_key | VARCHAR | Annual reference-period identity. |
| dim_period | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| dim_period | period_start | DATE | Derived January 1 boundary of an annual reference period; not an observation timestamp. |
| dim_period | period_end | DATE | Derived December 31 boundary of an annual reference period; not an observation timestamp. |
| dim_period | frequency | VARCHAR | Annual source frequency A; no annual/monthly summation. |
| dim_scenario | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| dim_scenario | edition | VARCHAR | Exact IEA model edition; scenarios from different editions must not be merged. |
| dim_scenario | scenario_name | VARCHAR | Exact source scenario name; no scenario substitution or cloning. |
| dim_scenario | case_name | VARCHAR | Exact technology/project case, distinct from the scenario. |
| dim_scenario | scenario_kind | VARCHAR | Scenario model member or explicit not_applicable member. |
| dim_end_use | end_use_key | VARCHAR | Native demand end-use identity. |
| dim_end_use | end_use_name | VARCHAR | Native IEA demand end-use category. |
| dim_supply_chain_stage | stage_key | VARCHAR | Mining/refining output-stage identity. |
| dim_supply_chain_stage | stage_code | VARCHAR | Mining or refining expected-output stage; not nameplate capacity. |
| dim_supply_chain_stage | stage_name | VARCHAR | Mining or Refining source stage label. |
| dim_supply_chain_stage | measure_kind | VARCHAR | Expected output rather than nameplate capacity. |
| dim_trade_flow | flow_key | VARCHAR | Native import/export direction identity. |
| dim_trade_flow | flow_code | VARCHAR | Native German reporter direction: 1 import, 2 export. |
| dim_trade_flow | flow_name | VARCHAR | Import or Export from the reporter perspective. |
| dim_product | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| dim_product | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| dim_product | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| dim_product | product_label | VARCHAR | Native source product description; annual concordance is not asserted. |
| dim_product | classification_reference_year | INTEGER | Native product reference year included in the product key; no assumed historical concordance. |
| dim_product | native_classification | VARCHAR | Native CN8 classification; reference-year product identities are kept separately. |
| dim_product | product_form | VARCHAR | Specific traded form such as ore/concentrate, carbonate, oxide or finished magnet article. |
| dim_product | definition_scope | VARCHAR | Explicit native material/product boundaries and incompatibilities. |
| dim_product | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| dim_product | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| dim_source_release | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| dim_source_release | source | VARCHAR | Source contract name iea or comext. |
| dim_source_release | source_release | VARCHAR | Native IEA model edition or Comext published revision timestamp. |
| dim_source_release | source_release_timestamp | TIMESTAMP WITH TIME ZONE | Native published dataset revision time; null when the source did not supply one. |
| dim_source_release | licence_name | VARCHAR | Source-specific reuse terms; project code licensing does not replace these. |
| dim_source_release | licence_url | VARCHAR | Authoritative source rights/attribution notice URL. |
| dim_source_release | publication_status | VARCHAR | Publication conditions retained from the reviewed source contract. |
| dim_source_release | source_timestamp_status | VARCHAR | Whether a native source publication timestamp was supplied; local load freshness is separate. |
| dim_snapshot | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| dim_snapshot | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| dim_snapshot | source | VARCHAR | Source contract name iea or comext. |
| dim_snapshot | request_id | VARCHAR | Stable source and canonical-query identity; not a source revision. |
| dim_snapshot | payload_sha256 | VARCHAR | SHA-256 of the unchanged original source response bytes. |
| dim_snapshot | first_retrieved_at_utc | TIMESTAMP WITH TIME ZONE | Original first acquisition timestamp from the accepted capture manifest. |
| dim_snapshot | request_url | VARCHAR | Exact public bounded source request URL, without credentials. |
| dim_snapshot | validation_status | VARCHAR | Accepted or accepted_empty source-contract result; empty does not imply zero activity. |
| dim_snapshot | source_observations | INTEGER | Count of native observations returned for the snapshot, including explicit null/status cells. |
| fct_material_demand | demand_key | VARCHAR | Native source-record identity at the complete demand grain. |
| fct_material_demand | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| fct_material_demand | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| fct_material_demand | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| fct_material_demand | period_key | VARCHAR | Annual reference-period identity. |
| fct_material_demand | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| fct_material_demand | end_use_key | VARCHAR | Native demand end-use identity. |
| fct_material_demand | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| fct_material_demand | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| fct_material_demand | source_record_id | VARCHAR | Deterministic original record identity retained for native lineage. |
| fct_material_demand | native_demand | DOUBLE | Demand in the unchanged IEA native unit and equivalent scope. |
| fct_material_demand | native_unit | VARCHAR | Unchanged native unit; inspected IEA values are Thousand tonnes. |
| fct_material_demand | demand_native_scope_tonnes | DOUBLE | Demand scaled from Thousand tonnes to tonnes within its native definition; basis remains unverified. |
| fct_material_demand | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| fct_material_demand | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| fct_material_demand | conversion_status | VARCHAR | Applied physical scale conversion, separate from semantic equivalence. |
| fct_material_demand | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| fct_material_demand | quality_state | VARCHAR | Structural validation state; valid records may still have unresolved semantic gates. |
| fct_material_supply | supply_key | VARCHAR | Native source-record identity at the complete supply grain. |
| fct_material_supply | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| fct_material_supply | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| fct_material_supply | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| fct_material_supply | period_key | VARCHAR | Annual reference-period identity. |
| fct_material_supply | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| fct_material_supply | stage_key | VARCHAR | Mining/refining output-stage identity. |
| fct_material_supply | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| fct_material_supply | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| fct_material_supply | source_record_id | VARCHAR | Deterministic original record identity retained for native lineage. |
| fct_material_supply | native_supply | DOUBLE | Expected supply output in the unchanged native IEA unit, not capacity. |
| fct_material_supply | native_unit | VARCHAR | Unchanged native unit; inspected IEA values are Thousand tonnes. |
| fct_material_supply | supply_native_scope_tonnes | DOUBLE | Expected output scaled by 1,000 within its native stage/definition; not additive across stages. |
| fct_material_supply | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| fct_material_supply | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| fct_material_supply | conversion_status | VARCHAR | Applied physical scale conversion, separate from semantic equivalence. |
| fct_material_supply | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| fct_material_supply | geography_entity_type | VARCHAR | Country/territory, World or opaque residual; residuals cannot be treated as a single country. |
| fct_material_supply | quality_state | VARCHAR | Structural validation state; valid records may still have unresolved semantic gates. |
| fct_material_supply | supply_measure_kind | VARCHAR | Explicit expected_output_not_capacity classification. |
| fct_trade_flows | trade_flow_key | VARCHAR | Snapshot/reporter/partner/product/reference-year/flow identity; independent indicator cells are preserved. |
| fct_trade_flows | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| fct_trade_flows | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| fct_trade_flows | reporter_key | VARCHAR | Reporting geography role key. |
| fct_trade_flows | partner_key | VARCHAR | Trade partner geography role key, including flagged aggregates/special categories. |
| fct_trade_flows | period_key | VARCHAR | Annual reference-period identity. |
| fct_trade_flows | flow_key | VARCHAR | Native import/export direction identity. |
| fct_trade_flows | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| fct_trade_flows | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| fct_trade_flows | value_record_id | VARCHAR | Nullable original EUR-cell record ID; absence is not zero. |
| fct_trade_flows | quantity_record_id | VARCHAR | Nullable original 100kg-cell record ID; absence is not zero. |
| fct_trade_flows | supplementary_record_id | VARCHAR | Nullable original supplementary-cell record ID; absence is not zero. |
| fct_trade_flows | trade_value_eur | DOUBLE | Native trade value in EUR for the selected product/reporter/partner/period/direction. |
| fct_trade_flows | native_quantity_100kg | DOUBLE | Native Comext mass indicator; one unit represents 100 kg of the traded product. |
| fct_trade_flows | product_mass_tonnes | DOUBLE | Comext native 100kg quantity multiplied by 0.1; not contained metal mass. |
| fct_trade_flows | supplementary_quantity | DOUBLE | Native supplementary observation when supplied; missing remains null and no generic mass conversion is permitted. |
| fct_trade_flows | value_source_status | VARCHAR | Unchanged source status for the EUR cell, nullable. |
| fct_trade_flows | quantity_source_status | VARCHAR | Unchanged source status for the 100kg quantity cell, nullable. |
| fct_trade_flows | supplementary_source_status | VARCHAR | Unchanged supplementary-cell source status; no generic mass unit inferred. |
| fct_trade_flows | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| fct_trade_flows | conversion_status | VARCHAR | Applied physical scale conversion, separate from semantic equivalence. |
| fct_trade_flows | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| fct_trade_flows | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| fct_trade_flows | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| fct_trade_flows | partner_entity_type | VARCHAR | Partner area category; exclude aggregates when summing components. |
| fct_trade_flows | source_cell_count | BIGINT | Number of native indicator cells retained in this trade-flow pivot; duplicates are independently tested. |
| fct_trade_flows | quality_state | VARCHAR | Structural validation state; valid records may still have unresolved semantic gates. |
| fct_trade_flows | supplementary_unit_status | VARCHAR | Product-specific supplementary unit is not yet documented. |
| fct_ingestion_coverage | coverage_key | VARCHAR | Selected source snapshot identity, including empty requests. |
| fct_ingestion_coverage | run_id | VARCHAR | Complete selected acquisition run; a partial refresh cannot replace the warehouse selection. |
| fct_ingestion_coverage | source | VARCHAR | Source contract name iea or comext. |
| fct_ingestion_coverage | request_id | VARCHAR | Stable source and canonical-query identity; not a source revision. |
| fct_ingestion_coverage | source_release | VARCHAR | Native IEA model edition or Comext published revision timestamp. |
| fct_ingestion_coverage | source_observations | INTEGER | Count of native observations returned for the snapshot, including explicit null/status cells. |
| fct_ingestion_coverage | validation_status | VARCHAR | Accepted or accepted_empty source-contract result; empty does not imply zero activity. |
| fct_ingestion_coverage | first_retrieved_at_utc | TIMESTAMP WITH TIME ZONE | Original first acquisition timestamp from the accepted capture manifest. |
| fct_ingestion_coverage | source_release_timestamp | TIMESTAMP WITH TIME ZONE | Native published dataset revision time; null when the source did not supply one. |
| fct_ingestion_coverage | empty_source_response | BOOLEAN | True for a validated empty source response, not an estimated zero. |
| fct_ingestion_coverage | coverage_state | VARCHAR | Native observations available or no observations returned; never zero-market-activity inference. |
| dq_observation_issues | source_record_id | VARCHAR | Deterministic original record identity retained for native lineage. |
| dq_observation_issues | source | VARCHAR | Source contract name iea or comext. |
| dq_observation_issues | issue_code | VARCHAR | Blocking structural reference, unit or sign anomaly requiring review. |
| dq_semantic_gates | source | VARCHAR | Source contract name iea or comext. |
| dq_semantic_gates | gate | VARCHAR | Unresolved measurement/interpretation limitation; not a composite risk score. |
| dq_semantic_gates | affected_records | BIGINT | Number of source/fact records subject to this specific semantic gate. |
| dq_semantic_gates | required_policy | VARCHAR | Restriction to retain when consuming the affected records. |
