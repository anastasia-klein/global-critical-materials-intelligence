# Model grains and relationships

| Fact / mart | Grain |
|---|---|
| fct_material_demand | Native source record: exact definition × geography × year × edition/scenario/case × end use × native basis/release |
| fct_material_supply | Native source record: exact definition × country/residual × year × mining/refining × edition/scenario/case × basis/release |
| fct_trade_flows | Selected snapshot × reporter × partner × annual CN8 product/reference year × import/export flow |
| fct_ingestion_coverage | Selected request snapshot, including empty responses |
| mart_supply_country_shares | Native supply observation × source selection |
| mart_global_supply_concentration | Exact definition × edition/scenario/case × stage × year × snapshot × selection |
| mart_trade_partner_shares | Reporter × annual product × partner × flow × snapshot × value/mass basis × selection |
| mart_country_material_dependency | Reporter × annual product × import snapshot × basis × selection |
| mart_european_trade_analysis | Reporter × annual product × snapshot × basis × selection |
| mart_supplier_composition_changes | Reporter × adjacent annual product keys × partner × basis × both snapshots × selection |
| mart_material_outlook | Definition × geography × scenario × endpoint × series kind × optional stage/end use × snapshot × selection |
| mart_scenario_comparison | Matched demand series/end use × year × scenario pair × selection |
| mart_material_supply_risk | Selection × polymorphic scope kind/key × geography × reference period × scenario × component × comparison contract × lineage snapshot |
| mart_supplier_basis_sensitivity | Reporter × annual product × snapshot × selection |

Risk comparison contracts retain comparison kind, base/end years, stage, measure basis, quantity basis and denominator scope. Different scenarios, stages or horizons cannot collide. Definition-scoped rows join material definitions; product-scoped rows join annual products. No composite score is calculated.

Eleven Gold dimensions describe material family, exact material definition, annual native product, source-qualified geography, period, scenario, end use, supply stage, trade direction, source release and snapshot. Native product identity includes reference year because CN concordance is unverified. Scenario includes edition and case. ISO aliases are reviewed, not fuzzy matched. Regions, special partners and opaque residuals stay explicitly typed.

Power BI adds presentation dimensions for material tiles, fixed partner groups and end-use order. These do not create physical material equivalence. Material-family relationships filter Definitions and Products in one direction; end-use/scenario/year/basis choices are explicitly applied by measures. Graphite/all-grades stay separate. Numeric columns do not use implicit summarisation.

Source observations and immutable snapshots preserve lineage throughout Bronze, Silver, Gold, marts and portable report exports. Missing values are not filled from other metrics; duplicate measurement grains fail tests.
