# Active source inventory

This inventory describes the source contracts and included capture, not universal upstream coverage.

| Property | IEA | Eurostat Comext |
|---|---|---|
| Endpoint | https://api.iea.org/minerals | https://ec.europa.eu/eurostat/api/comext/dissemination/statistics/1.0/data/DS-045409 |
| Format | JSON array of native records | JSON-stat cube; sparse value/status maps |
| Included observations | 1,006: 558 demand + 448 supply | 33,928 native indicator cells, pivoted to 16,964 native flows |
| Geography | World demand; named supply countries and Other countries | DE, FR, IT, ES, PL, NL, EU27_2020 reporters; source-qualified partners |
| Time | Demand 2025/30/35/40/45/50; supply 2025/30/35/40 | Annual 2018–2024; magnet product populated in 2023–2024 |
| Scenario | CPS/HDS/STEPS demand; STEPS Base Case supply | Not applicable |
| Units | Thousand tonnes, native material scope; scaled to native-scope tonnes | Native EUR, 100kg and supplementary-unit indicators; product tonnes derived from 100kg |
| Empty / absent | All-grades graphite supply returned no records | Empty product-year responses retained; sparse combinations not zero-filled |
| Updates | Edition/source revisions; no guaranteed cadence assumed | Source revisions; captured update 16 October 2026; no change-feed contract assumed |
| Acquisition | Bounded material/category requests, no paging envelope in inspected responses | Bounded reporter/product/year queries, no bulk paging assumption |

`config/sources.json` is the executable request contract. `dashboards/powerbi/data/export_manifest.json` records exact SQL, output types, hashes and source-capture ranges for the distributed report.

IEA fields: mcm, scenario, category, unit, region, product, year, material, case, value, flow. Required types and accepted editions/units/scenarios are validated. Unknown additional fields stay in the original record.

Comext retains dimension IDs/order, category indexes, labels, native coordinates, values/statuses, dataset update and cell offsets. Dense and sparse maps are decoded by their actual strides. Missing cells, explicit nulls, zero and status-without-value remain distinguishable. Original bytes are preserved separately from decoded Bronze records.

Material families provide context only. IEA definitions, annual CN8 forms, mining/refining stages, equivalent bases and scenario editions are not silently merged. Country mappings are source-qualified; regions, residuals and special partners are explicitly typed. EU27 external totals are not inferred from a subset of national reporters.

Coverage gaps: compatible consumption, contained-metal quantities, installed capacity and matched primary requirements are unavailable. Trade cannot establish upstream origin. Licensing and attribution: [source rights](licensing.md).
