# Business-layer column dictionary

Four intermediate and ten business models; 327 columns. Native warehouse columns are documented separately.

| Model | Column | DuckDB type | Meaning |
| --- | --- | --- | --- |
| int_analysis_context | source_selection_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| int_analysis_context | selected_snapshot_count | INTEGER | Number of selected request snapshots, including empty responses. |
| int_trade_measures | trade_flow_key | VARCHAR | Snapshot/reporter/partner/product/reference-year/flow identity; independent indicator cells are preserved. |
| int_trade_measures | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| int_trade_measures | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| int_trade_measures | reporter_key | VARCHAR | Reporting geography role key. |
| int_trade_measures | partner_key | VARCHAR | Trade partner geography role key, including flagged aggregates/special categories. |
| int_trade_measures | period_key | VARCHAR | Annual reference-period identity. |
| int_trade_measures | flow_key | VARCHAR | Native import/export direction identity. |
| int_trade_measures | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| int_trade_measures | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| int_trade_measures | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| int_trade_measures | partner_entity_type | VARCHAR | Partner area category; exclude aggregates when summing components. |
| int_trade_measures | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| int_trade_measures | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| int_trade_measures | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| int_trade_measures | partner_name | VARCHAR | Canonical display name for the source-qualified reported partner. |
| int_trade_measures | partner_iso_alpha2 | VARCHAR | Reviewed ISO alpha-2 where assigned; geopolitical areas can remain null. |
| int_trade_measures | flow_name | VARCHAR | Reporting-perspective import or export direction. |
| int_trade_measures | measure_basis | VARCHAR | Separate measure family: trade_value in EUR, product_mass in product tonnes, or explicitly labelled native scenario output; never sum across bases. |
| int_trade_measures | measure_unit | VARCHAR | Unit matching the measure basis; native scenario tonnes retain unverified equivalent basis. |
| int_trade_measures | measure_value | DOUBLE | Native trade indicator after documented scale conversion, without inferring missing values. |
| int_trade_measures | source_status | VARCHAR | Original source status for this indicator; null means no supplied status, not certified observed actual. |
| int_trade_measures | source_record_id | VARCHAR | Deterministic original record identity retained for native lineage. |
| int_trade_denominators | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| int_trade_denominators | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| int_trade_denominators | reporter_key | VARCHAR | Reporting geography role key. |
| int_trade_denominators | period_key | VARCHAR | Annual reference-period identity. |
| int_trade_denominators | flow_key | VARCHAR | Native import/export direction identity. |
| int_trade_denominators | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| int_trade_denominators | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| int_trade_denominators | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| int_trade_denominators | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| int_trade_denominators | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| int_trade_denominators | flow_name | VARCHAR | Reporting-perspective import or export direction. |
| int_trade_denominators | measure_basis | VARCHAR | Separate measure family: trade_value in EUR, product_mass in product tonnes, or explicitly labelled native scenario output; never sum across bases. |
| int_trade_denominators | measure_unit | VARCHAR | Unit matching the measure basis; native scenario tonnes retain unverified equivalent basis. |
| int_trade_denominators | world_row_count | INTEGER | Count of native World rows at the selected product/reporter/year/flow/measure grain; exactly one is required. |
| int_trade_denominators | world_total | DOUBLE | Native World amount for this measure. Denominator includes intra-EU and extra-EU partners; excludes summing overlapping regional aggregates. |
| int_trade_denominators | named_partner_total | DOUBLE | Sum of reported country/territory and explicitly typed geopolitical partner values; World and regional/special aggregates excluded. |
| int_trade_denominators | reported_special_partner_total | DOUBLE | Reported special trade partner amount, separately disclosed; it is not assigned to a named supplier. |
| int_trade_denominators | missing_named_measure_count | INTEGER | Reported named-partner rows lacking this measure; never converted to zero. |
| int_trade_denominators | flagged_measure_count | INTEGER | Number of source measure rows with a non-null source status; not a quality certification. |
| int_trade_denominators | negative_measure_count | INTEGER | Source measure rows below zero; invalidate this denominator rather than dropping the offending rows. |
| int_trade_denominators | native_reconciliation_delta | DOUBLE | Native World minus named partner sum, retaining floating-point discrepancies before tolerance handling. |
| int_trade_denominators | numeric_tolerance | DOUBLE | Engineering-only tolerance: max(0.01 EUR or 0.000001 product tonnes, absolute World times 1e-9). No economic materiality threshold is inferred. |
| int_trade_denominators | denominator_status | VARCHAR | Availability reason after checking one positive World row, nonnegative detail and reconciliation within numeric tolerance. |
| int_trade_denominators | unallocated_amount | DOUBLE | World less known partner amounts, with numerical noise within tolerance represented as zero. Unknown/residual shares remain unassigned. |
| int_trade_denominators | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| int_outlook_series | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| int_outlook_series | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| int_outlook_series | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| int_outlook_series | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| int_outlook_series | stage_key | VARCHAR | Mining/refining output-stage identity. |
| int_outlook_series | end_use_key | VARCHAR | Native demand end-use identity. |
| int_outlook_series | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| int_outlook_series | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| int_outlook_series | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| int_outlook_series | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| int_outlook_series | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| int_outlook_series | series_kind | VARCHAR | Native end-use demand, sum of returned demand end uses, or expected supply panel output. These series are not interchangeable. |
| int_outlook_series | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| int_outlook_series | native_scope_tonnes | DOUBLE | Native quantity scaled to tonnes within the exact definition. Unverified equivalent basis remains attached. |
| int_outlook_series | source_observation_count | INTEGER | Count of native observations contributing to this point; no missing end uses or countries fabricated. |
| int_outlook_series | missing_value_count | INTEGER | Count of source observations without a value; blocks aggregate growth if nonzero. |
| int_outlook_series | category_set_key | VARCHAR | Exact end-use membership fingerprint; supply aggregate uses a declared country-plus-residual scope whose internal membership may change. |
| mart_trade_partner_shares | partner_share_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_trade_partner_shares | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_trade_partner_shares | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_trade_partner_shares | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| mart_trade_partner_shares | reporter_key | VARCHAR | Reporting geography role key. |
| mart_trade_partner_shares | partner_key | VARCHAR | Trade partner geography role key, including flagged aggregates/special categories. |
| mart_trade_partner_shares | period_key | VARCHAR | Annual reference-period identity. |
| mart_trade_partner_shares | flow_key | VARCHAR | Native import/export direction identity. |
| mart_trade_partner_shares | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| mart_trade_partner_shares | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| mart_trade_partner_shares | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_trade_partner_shares | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| mart_trade_partner_shares | flow_name | VARCHAR | Reporting-perspective import or export direction. |
| mart_trade_partner_shares | partner_name | VARCHAR | Canonical display name for the source-qualified reported partner. |
| mart_trade_partner_shares | partner_iso_alpha2 | VARCHAR | Reviewed ISO alpha-2 where assigned; geopolitical areas can remain null. |
| mart_trade_partner_shares | partner_entity_type | VARCHAR | Partner area category; exclude aggregates when summing components. |
| mart_trade_partner_shares | measure_basis | VARCHAR | Separate measure family: trade_value in EUR, product_mass in product tonnes, or explicitly labelled native scenario output; never sum across bases. |
| mart_trade_partner_shares | measure_unit | VARCHAR | Unit matching the measure basis; native scenario tonnes retain unverified equivalent basis. |
| mart_trade_partner_shares | measure_value | DOUBLE | Native trade indicator after documented scale conversion, without inferring missing values. |
| mart_trade_partner_shares | source_status | VARCHAR | Original source status for this indicator; null means no supplied status, not certified observed actual. |
| mart_trade_partner_shares | source_record_id | VARCHAR | Deterministic original record identity retained for native lineage. |
| mart_trade_partner_shares | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_trade_partner_shares | world_total | DOUBLE | Native World amount for this measure. Denominator includes intra-EU and extra-EU partners; excludes summing overlapping regional aggregates. |
| mart_trade_partner_shares | unallocated_amount | DOUBLE | World less known partner amounts, with numerical noise within tolerance represented as zero. Unknown/residual shares remain unassigned. |
| mart_trade_partner_shares | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| mart_trade_partner_shares | denominator_status | VARCHAR | Availability reason after checking one positive World row, nonnegative detail and reconciliation within numeric tolerance. |
| mart_trade_partner_shares | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| mart_trade_partner_shares | partner_share | DOUBLE | Reported bilateral partner amount divided by native World, separately by measure. Null when unavailable. |
| mart_trade_partner_shares | reported_partner_rank | INTEGER | Deterministic amount rank among reported named partners, descending with key tie break; null for a missing measure. Not a claim of unique economic leadership. |
| mart_country_material_dependency | dependency_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_country_material_dependency | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_country_material_dependency | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_country_material_dependency | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| mart_country_material_dependency | reporter_key | VARCHAR | Reporting geography role key. |
| mart_country_material_dependency | period_key | VARCHAR | Annual reference-period identity. |
| mart_country_material_dependency | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| mart_country_material_dependency | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| mart_country_material_dependency | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_country_material_dependency | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| mart_country_material_dependency | measure_basis | VARCHAR | Separate measure family: trade_value in EUR, product_mass in product tonnes, or explicitly labelled native scenario output; never sum across bases. |
| mart_country_material_dependency | measure_unit | VARCHAR | Unit matching the measure basis; native scenario tonnes retain unverified equivalent basis. |
| mart_country_material_dependency | world_total | DOUBLE | Native World amount for this measure. Denominator includes intra-EU and extra-EU partners; excludes summing overlapping regional aggregates. |
| mart_country_material_dependency | named_partner_total | DOUBLE | Sum of reported country/territory and explicitly typed geopolitical partner values; World and regional/special aggregates excluded. |
| mart_country_material_dependency | reported_special_partner_total | DOUBLE | Reported special trade partner amount, separately disclosed; it is not assigned to a named supplier. |
| mart_country_material_dependency | unallocated_amount | DOUBLE | World less known partner amounts, with numerical noise within tolerance represented as zero. Unknown/residual shares remain unassigned. |
| mart_country_material_dependency | native_reconciliation_delta | DOUBLE | Native World minus named partner sum, retaining floating-point discrepancies before tolerance handling. |
| mart_country_material_dependency | numeric_tolerance | DOUBLE | Engineering-only tolerance: max(0.01 EUR or 0.000001 product tonnes, absolute World times 1e-9). No economic materiality threshold is inferred. |
| mart_country_material_dependency | missing_named_measure_count | INTEGER | Reported named-partner rows lacking this measure; never converted to zero. |
| mart_country_material_dependency | flagged_measure_count | INTEGER | Number of source measure rows with a non-null source status; not a quality certification. |
| mart_country_material_dependency | reported_named_partner_count | INTEGER | Count of returned named partner rows, not a claim that absent partners have zero trade. |
| mart_country_material_dependency | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| mart_country_material_dependency | denominator_status | VARCHAR | Availability reason after checking one positive World row, nonnegative detail and reconciliation within numeric tolerance. |
| mart_country_material_dependency | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| mart_country_material_dependency | largest_named_partner_key | VARCHAR | A maximum-amount reported named partner; deterministic key tie break. Does not assign unknown residual to a country. |
| mart_country_material_dependency | unallocated_share | DOUBLE | Unallocated amount divided by native World. Kept outside named supplier ranks. |
| mart_country_material_dependency | hhi_lower | DOUBLE | Conservative HHI lower bound on the 0–1 scale: sum of squared known shares; unresolved residual is infinitely dispersed. |
| mart_country_material_dependency | hhi_upper | DOUBLE | Conservative HHI upper bound on the 0–1 scale. Supply Other countries is additional to named countries; unallocated trade may augment the largest known supplier, adding 2*largest_share*residual_share as well as residual_share squared. |
| mart_country_material_dependency | top_supplier_share_lower | DOUBLE | Conservative top-1 share lower bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_country_material_dependency | top_supplier_share_upper | DOUBLE | Conservative top-1 share upper bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_country_material_dependency | top3_share_lower | DOUBLE | Conservative top-3 share lower bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_country_material_dependency | top3_share_upper | DOUBLE | Conservative top-3 share upper bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_country_material_dependency | top5_share_lower | DOUBLE | Conservative top-5 share lower bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_country_material_dependency | top5_share_upper | DOUBLE | Conservative top-5 share upper bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_country_material_dependency | named_leader_guaranteed | BOOLEAN | Whether the largest known amount is at least second-largest known plus the entire unallocated amount. Unknown trade can augment an existing supplier; ties are permitted. |
| mart_country_material_dependency | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_country_material_dependency | import_dependency | DOUBLE | Unavailable consumption-based import dependency. Always null until compatible domestic output and consumption exist. |
| mart_country_material_dependency | import_dependency_status | VARCHAR | Explicit missing-input reason; supplier concentration must never substitute for import dependency. |
| mart_european_trade_analysis | trade_analysis_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_european_trade_analysis | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_european_trade_analysis | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_european_trade_analysis | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| mart_european_trade_analysis | reporter_key | VARCHAR | Reporting geography role key. |
| mart_european_trade_analysis | period_key | VARCHAR | Annual reference-period identity. |
| mart_european_trade_analysis | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| mart_european_trade_analysis | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| mart_european_trade_analysis | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_european_trade_analysis | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| mart_european_trade_analysis | measure_basis | VARCHAR | Separate measure family: trade_value in EUR, product_mass in product tonnes, or explicitly labelled native scenario output; never sum across bases. |
| mart_european_trade_analysis | measure_unit | VARCHAR | Unit matching the measure basis; native scenario tonnes retain unverified equivalent basis. |
| mart_european_trade_analysis | classification_status | VARCHAR | Annual native product scope retained; longitudinal concordance remains unverified. |
| mart_european_trade_analysis | imports | DOUBLE | Source World imports for a valid measure denominator, in the selected basis and annual product scope. |
| mart_european_trade_analysis | exports | DOUBLE | Source World exports for a valid measure denominator, in the selected basis and annual product scope. |
| mart_european_trade_analysis | import_unallocated_amount | DOUBLE | Unallocated import amount relative to the source World row. |
| mart_european_trade_analysis | export_unallocated_amount | DOUBLE | Unallocated export amount relative to the source World row. |
| mart_european_trade_analysis | flagged_measure_count | INTEGER | Number of source measure rows with a non-null source status; not a quality certification. |
| mart_european_trade_analysis | valid_flow_count | INTEGER | Count of valid import/export denominators; both are required for trade balance. |
| mart_european_trade_analysis | trade_balance | DOUBLE | Source World exports minus imports, within one annual product and measure scope. CIF/FOB and re-export limitations remain. |
| mart_european_trade_analysis | balance_status | VARCHAR | Availability of the reporting-perspective trade balance at the same annual product and measure scope. |
| mart_european_trade_analysis | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| mart_european_trade_analysis | interpretation_status | VARCHAR | CIF/FOB and origin/consumption limitations attached to the reported balance. |
| mart_european_trade_analysis | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_supply_country_shares | supply_share_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_supply_country_shares | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_supply_country_shares | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_supply_country_shares | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| mart_supply_country_shares | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| mart_supply_country_shares | period_key | VARCHAR | Annual reference-period identity. |
| mart_supply_country_shares | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| mart_supply_country_shares | stage_key | VARCHAR | Mining/refining output-stage identity. |
| mart_supply_country_shares | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| mart_supply_country_shares | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| mart_supply_country_shares | source_record_id | VARCHAR | Deterministic original record identity retained for native lineage. |
| mart_supply_country_shares | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_supply_country_shares | geography_entity_type | VARCHAR | Country/territory, World or opaque residual; residuals cannot be treated as a single country. |
| mart_supply_country_shares | supply_native_scope_tonnes | DOUBLE | Expected output scaled by 1,000 within its native stage/definition; not additive across stages. |
| mart_supply_country_shares | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| mart_supply_country_shares | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_supply_country_shares | panel_output_tonnes | DOUBLE | Sum of captured country output plus the opaque Other countries residual for one definition/scenario/stage/year; not nameplate capacity. |
| mart_supply_country_shares | invalid_panel_observations | INTEGER | Panel records with missing or negative expected output; invalidate shares rather than silently dropping them. |
| mart_supply_country_shares | supply_share | DOUBLE | Native expected output divided by the captured named-country-plus-residual panel. The residual remains a non-country component. |
| mart_supply_country_shares | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| mart_supply_country_shares | supply_measure_kind | VARCHAR | Explicit expected_output_not_capacity classification. |
| mart_global_supply_concentration | concentration_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_global_supply_concentration | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_global_supply_concentration | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_global_supply_concentration | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| mart_global_supply_concentration | period_key | VARCHAR | Annual reference-period identity. |
| mart_global_supply_concentration | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| mart_global_supply_concentration | stage_key | VARCHAR | Mining/refining output-stage identity. |
| mart_global_supply_concentration | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| mart_global_supply_concentration | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| mart_global_supply_concentration | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_global_supply_concentration | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| mart_global_supply_concentration | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_global_supply_concentration | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| mart_global_supply_concentration | panel_output_tonnes | DOUBLE | Sum of captured country output plus the opaque Other countries residual for one definition/scenario/stage/year; not nameplate capacity. |
| mart_global_supply_concentration | invalid_panel_observations | INTEGER | Panel records with missing or negative expected output; invalidate shares rather than silently dropping them. |
| mart_global_supply_concentration | residual_share | DOUBLE | Other countries share; membership is unresolved and may change over time. Never rank it as one producer. |
| mart_global_supply_concentration | named_country_count | INTEGER | Count of captured named country/territory output records, including reported zeroes. |
| mart_global_supply_concentration | largest_named_share | DOUBLE | Maximum named-country share within the captured panel; residual may conceal another large producer. |
| mart_global_supply_concentration | hhi_lower | DOUBLE | Conservative HHI lower bound on the 0–1 scale: sum of squared known shares; unresolved residual is infinitely dispersed. |
| mart_global_supply_concentration | hhi_upper | DOUBLE | Conservative HHI upper bound on the 0–1 scale. Supply Other countries is additional to named countries; unallocated trade may augment the largest known supplier, adding 2*largest_share*residual_share as well as residual_share squared. |
| mart_global_supply_concentration | top3_share_lower | DOUBLE | Conservative top-3 share lower bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_global_supply_concentration | top3_share_upper | DOUBLE | Conservative top-3 share upper bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_global_supply_concentration | top5_share_lower | DOUBLE | Conservative top-5 share lower bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_global_supply_concentration | top5_share_upper | DOUBLE | Conservative top-5 share upper bound, on the 0–1 scale. Lower uses largest known shares. Supply upper permits one additional residual country; trade upper adds unresolved mass to the leading known suppliers, capped at one. |
| mart_global_supply_concentration | metric_status | VARCHAR | Exact captured panel, residual-bounded estimate or unavailable panel. Does not certify observed production. |
| mart_global_supply_concentration | hhi_unit | VARCHAR | HHI uses the 0–1 scale. A 10,000-scale value requires an explicitly separate conversion. |
| mart_global_supply_concentration | supply_measure_kind | VARCHAR | Explicit expected_output_not_capacity classification. |
| mart_supplier_composition_changes | composition_change_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_supplier_composition_changes | product_code | VARCHAR | Native CN8 commodity code; one selected product form rather than a full material basket. |
| mart_supplier_composition_changes | reporter_key | VARCHAR | Reporting geography role key. |
| mart_supplier_composition_changes | measure_basis | VARCHAR | Separate measure family: trade_value in EUR, product_mass in product tonnes, or explicitly labelled native scenario output; never sum across bases. |
| mart_supplier_composition_changes | base_year | INTEGER | Explicit comparison baseline year; growth uses the native 2025 baseline whose observed/estimated status remains unverified. |
| mart_supplier_composition_changes | end_year | INTEGER | Explicit comparison endpoint year; composition comparisons require adjacent calendar years. |
| mart_supplier_composition_changes | base_product_key | VARCHAR | Native CN8 and reference-year product key on the base side; continuity across years is unverified. |
| mart_supplier_composition_changes | end_product_key | VARCHAR | Native CN8 and reference-year product key on the end side; continuity across years is unverified. |
| mart_supplier_composition_changes | base_snapshot_key | VARCHAR | Immutable source snapshot for the base side of this comparison. |
| mart_supplier_composition_changes | end_snapshot_key | VARCHAR | Immutable source snapshot for the end side of this comparison. |
| mart_supplier_composition_changes | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_supplier_composition_changes | base_world_total | DOUBLE | Base-year native World total for the same product code and measure. |
| mart_supplier_composition_changes | end_world_total | DOUBLE | End-year native World total for the same product code and measure. |
| mart_supplier_composition_changes | partner_key | VARCHAR | Trade partner geography role key, including flagged aggregates/special categories. |
| mart_supplier_composition_changes | base_share | DOUBLE | Reported partner share in the base-year product scope; null if partner or measure is absent. |
| mart_supplier_composition_changes | end_share | DOUBLE | Reported partner share in the end-year product scope; null if partner or measure is absent. |
| mart_supplier_composition_changes | base_amount | DOUBLE | Reported comparison-base partner amount or scenario amount in the explicit measure unit. |
| mart_supplier_composition_changes | end_amount | DOUBLE | Reported comparison-end partner amount in the same declared measure basis. |
| mart_supplier_composition_changes | conditional_share_change_pp | DOUBLE | 100 times end share minus base share only when both are reported. Diagnostic conditional on unverified same-CN8 continuity; not a verified trend. |
| mart_supplier_composition_changes | presence_pattern | VARCHAR | Both reported, base-only reported or end-only reported. Query absence is not market entry or exit. |
| mart_supplier_composition_changes | comparison_status | VARCHAR | Explicit availability/comparability condition for this comparison, including unverified annual classification continuity. |
| mart_supplier_composition_changes | verified_share_change_pp | DOUBLE | Always null while annual CN concordance is unverified; conditional diagnostics are kept separately. |
| mart_supplier_composition_changes | entry_exit_status | VARCHAR | Market entry/exit is not established from source-query presence alone. |
| mart_material_outlook | outlook_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_material_outlook | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_material_outlook | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_material_outlook | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| mart_material_outlook | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| mart_material_outlook | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| mart_material_outlook | stage_key | VARCHAR | Mining/refining output-stage identity. |
| mart_material_outlook | end_use_key | VARCHAR | Native demand end-use identity. |
| mart_material_outlook | source_release_key | VARCHAR | Source plus native compilation edition/revision identity. |
| mart_material_outlook | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| mart_material_outlook | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_material_outlook | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| mart_material_outlook | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_material_outlook | series_kind | VARCHAR | Native end-use demand, sum of returned demand end uses, or expected supply panel output. These series are not interchangeable. |
| mart_material_outlook | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| mart_material_outlook | native_scope_tonnes | DOUBLE | Native quantity scaled to tonnes within the exact definition. Unverified equivalent basis remains attached. |
| mart_material_outlook | source_observation_count | INTEGER | Count of native observations contributing to this point; no missing end uses or countries fabricated. |
| mart_material_outlook | missing_value_count | INTEGER | Count of source observations without a value; blocks aggregate growth if nonzero. |
| mart_material_outlook | category_set_key | VARCHAR | Exact end-use membership fingerprint; supply aggregate uses a declared country-plus-residual scope whose internal membership may change. |
| mart_material_outlook | base_year | INTEGER | Explicit comparison baseline year; growth uses the native 2025 baseline whose observed/estimated status remains unverified. |
| mart_material_outlook | base_native_scope_tonnes | DOUBLE | Matched native 2025 baseline value for the same edition/scenario/case/definition/stage/end-use/basis/snapshot. |
| mart_material_outlook | base_evidence_class | VARCHAR | Evidence class of the comparison baseline, retained separately from the endpoint. |
| mart_material_outlook | base_category_set_key | VARCHAR | Baseline end-use membership fingerprint used to block changed-category aggregate growth. |
| mart_material_outlook | base_missing_value_count | INTEGER | Baseline missing source-component count; a nonzero value blocks growth. |
| mart_material_outlook | base_observation_count | INTEGER | Number of source observations contributing to the baseline point. |
| mart_material_outlook | growth_status | VARCHAR | Availability of native-scope growth after baseline, horizon, positive-base, missingness and category-set checks. |
| mart_material_outlook | comparison_contract_key | VARCHAR | Deterministic identity of comparison kind, base/end years, stage, measure/basis and denominator scope; retained in risk grain. |
| mart_material_outlook | growth_fraction | DOUBLE | Endpoint divided by matched positive 2025 baseline minus one. Fraction, not percentage points; unavailable on baseline rows. |
| mart_material_outlook | cagr_fraction | DOUBLE | Annualised native-scope growth: (end/base)^(1/(end year-base year))-1; sparse reference years are not interpolated. |
| mart_material_outlook | measure_unit | VARCHAR | Unit matching the measure basis; native scenario tonnes retain unverified equivalent basis. |
| mart_material_outlook | physical_supply_demand_gap | DOUBLE | Always null because matched primary requirements and verified equivalent basis are not available. |
| mart_material_outlook | physical_gap_status | VARCHAR | Reason physical shortage/surplus is unavailable; total demand is not substituted for primary requirements. |
| mart_material_outlook | nameplate_capacity | DOUBLE | Always null; source expected output is not a capacity series. |
| mart_material_outlook | capacity_status | VARCHAR | Reason nameplate-capacity level/growth is unavailable. |
| mart_scenario_comparison | scenario_comparison_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_scenario_comparison | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_scenario_comparison | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_scenario_comparison | material_definition_key | VARCHAR | Exact native IEA definition key; graphite scopes remain distinct. |
| mart_scenario_comparison | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| mart_scenario_comparison | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_scenario_comparison | series_kind | VARCHAR | Native end-use demand, sum of returned demand end uses, or expected supply panel output. These series are not interchangeable. |
| mart_scenario_comparison | end_use_key | VARCHAR | Native demand end-use identity. |
| mart_scenario_comparison | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| mart_scenario_comparison | measure_unit | VARCHAR | Unit matching the measure basis; native scenario tonnes retain unverified equivalent basis. |
| mart_scenario_comparison | reference_scenario_key | VARCHAR | Edition/scenario/case dimension key for the reference side; never collapse scenario contexts. |
| mart_scenario_comparison | alternative_scenario_key | VARCHAR | Edition/scenario/case dimension key for the alternative side; never collapse scenario contexts. |
| mart_scenario_comparison | reference_snapshot_key | VARCHAR | Immutable source snapshot for the reference side of this comparison. |
| mart_scenario_comparison | alternative_snapshot_key | VARCHAR | Immutable source snapshot for the alternative side of this comparison. |
| mart_scenario_comparison | reference_amount | DOUBLE | CPS amount at the same edition/case/definition/end-use/year/basis used for scenario comparison. |
| mart_scenario_comparison | alternative_amount | DOUBLE | Alternative demand scenario amount at matched native scope; no supply scenario is cloned. |
| mart_scenario_comparison | relative_difference_fraction | DOUBLE | Alternative amount / positive CPS reference amount - 1, only for matching end-use sets and complete values. |
| mart_scenario_comparison | comparison_status | VARCHAR | Explicit availability/comparability condition for this comparison, including unverified annual classification continuity. |
| mart_scenario_comparison | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_material_supply_risk | risk_component_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_material_supply_risk | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_material_supply_risk | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_material_supply_risk | scope_kind | VARCHAR | Polymorphic scope discriminator: native material definition or annual traded product. Family context alone never merges forms. |
| mart_material_supply_risk | scope_key | VARCHAR | Key into the dimension identified by scope_kind; native definition and annual product keys remain distinct. |
| mart_material_supply_risk | geography_key | VARCHAR | Canonical ISO or source-qualified area key; entity_type controls aggregation. |
| mart_material_supply_risk | scenario_key | VARCHAR | Composite source edition/scenario/case identity; never omit scenario during aggregation. |
| mart_material_supply_risk | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_material_supply_risk | base_year | INTEGER | Explicit comparison baseline year; growth uses the native 2025 baseline whose observed/estimated status remains unverified. |
| mart_material_supply_risk | end_year | INTEGER | Explicit comparison endpoint year; composition comparisons require adjacent calendar years. |
| mart_material_supply_risk | stage_key | VARCHAR | Mining/refining output-stage identity. |
| mart_material_supply_risk | measure_basis | VARCHAR | Separate measure family: trade_value in EUR, product_mass in product tonnes, or explicitly labelled native scenario output; never sum across bases. |
| mart_material_supply_risk | quantity_basis | VARCHAR | Measurement scope: unverified native IEA equivalent or Comext traded product mass; never interchangeable. |
| mart_material_supply_risk | denominator_scope | VARCHAR | Explicit denominator population or aggregate scope. Scenario panel sums and reported-end-use sums do not certify independent World totals. |
| mart_material_supply_risk | component_name | VARCHAR | Individually inspectable concentration, growth or unavailable dependency/gap/capacity component; no composite weighting. |
| mart_material_supply_risk | component_unit | VARCHAR | HHI on 0–1 scale, fraction, or explicitly labelled native-scope tonnes. Values across components are not additive. |
| mart_material_supply_risk | component_value | DOUBLE | Exact native-scope metric when available; null for a residual-bounded metric or unavailable component. |
| mart_material_supply_risk | component_lower | DOUBLE | Conservative lower bound, or point value for an available exact native-scope calculation; null when unavailable. |
| mart_material_supply_risk | component_upper | DOUBLE | Conservative upper bound, or point value for an available exact native-scope calculation; null when unavailable. |
| mart_material_supply_risk | availability | VARCHAR | available, bounded or unavailable; bounded is not a fabricated point estimate. |
| mart_material_supply_risk | availability_reason | VARCHAR | Machine-readable reason describing the applicable measurement contract or unavailable inputs. |
| mart_material_supply_risk | evidence_class | VARCHAR | Explicit baseline-unverified, scenario-projection or historical-trade-status-unverified class. |
| mart_material_supply_risk | lineage_snapshot_key | VARCHAR | Immutable source snapshot supporting this risk component, including unavailable-input context. |
| mart_material_supply_risk | comparison_kind | VARCHAR | Level component with no growth horizon, or growth from native 2025 baseline; different horizons remain separate risk records. |
| mart_material_supply_risk | comparison_contract_key | VARCHAR | Deterministic identity of comparison kind, base/end years, stage, measure/basis and denominator scope; retained in risk grain. |
| mart_material_supply_risk | composite_risk_score | DOUBLE | Always null. No arbitrary weighting, normalisation or risk thresholds are introduced. |
| mart_material_supply_risk | risk_policy | VARCHAR | Components remain unweighted and separately inspectable; no composite or unsupported high/medium/low bands. |
| mart_supplier_basis_sensitivity | sensitivity_key | VARCHAR | Deterministic surrogate identity of the full documented model grain. |
| mart_supplier_basis_sensitivity | source_selection_key | VARCHAR | MD5 of the ordered complete selected snapshot-ID set. Changes when any selected source snapshot changes; replay of identical snapshots retains identity. |
| mart_supplier_basis_sensitivity | material_key | VARCHAR | Contextual material-family key. This is not evidence that quantities can be added across definitions. |
| mart_supplier_basis_sensitivity | product_key | VARCHAR | CN8 plus native product code plus reference-year identity. |
| mart_supplier_basis_sensitivity | reporter_key | VARCHAR | Reporting geography role key. |
| mart_supplier_basis_sensitivity | reference_year | INTEGER | Native calendar reference year; forecasts are sparse model years, not interpolated history. |
| mart_supplier_basis_sensitivity | snapshot_key | VARCHAR | Request plus original-byte-hash lineage key, including empty responses. |
| mart_supplier_basis_sensitivity | value_hhi_lower | DOUBLE | EUR supplier HHI lower bound for the same annual product and reporter. |
| mart_supplier_basis_sensitivity | value_hhi_upper | DOUBLE | EUR supplier HHI upper bound including unresolved residual concentration. |
| mart_supplier_basis_sensitivity | mass_hhi_lower | DOUBLE | Product-mass supplier HHI lower bound for the same annual product and reporter. |
| mart_supplier_basis_sensitivity | mass_hhi_upper | DOUBLE | Product-mass supplier HHI upper bound including unresolved residual concentration. |
| mart_supplier_basis_sensitivity | mass_minus_value_hhi_lower | DOUBLE | Mass HHI lower bound minus value HHI upper bound: conservative lower bound of basis sensitivity. |
| mart_supplier_basis_sensitivity | mass_minus_value_hhi_upper | DOUBLE | Mass HHI upper bound minus value HHI lower bound: conservative upper bound of basis sensitivity. |
| mart_supplier_basis_sensitivity | value_largest_named_partner_key | VARCHAR | Largest known supplier key under the labelled measure basis, with deterministic tie break; not an origin or ownership claim. |
| mart_supplier_basis_sensitivity | mass_largest_named_partner_key | VARCHAR | Largest known supplier key under the labelled measure basis, with deterministic tie break; not an origin or ownership claim. |
| mart_supplier_basis_sensitivity | sensitivity_result | VARCHAR | Whether mass or value HHI is higher under every residual allocation, or ordering remains unresolved/unavailable. |
| mart_supplier_basis_sensitivity | same_guaranteed_leading_partner | BOOLEAN | Known leading partner matches across bases when each leader is guaranteed against its residual; null otherwise. Ties are not excluded. |
| mart_supplier_basis_sensitivity | sensitivity_scope | VARCHAR | Sensitivity compares value and mass within one product/year, with all trade partners included in the World denominator. |
| mart_supplier_basis_sensitivity | external_reconciliation_caveat | VARCHAR | Explicit unresolved G04 cobalt external-quantity discrepancy; this caveat does not assert all products have the same discrepancy. |
