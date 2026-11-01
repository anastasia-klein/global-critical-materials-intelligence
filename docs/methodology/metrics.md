# Implemented business metric contracts

The `analytics` schema is the SQL semantic layer above native Gold facts. Metrics are deliberately separated by annual product/native definition, measure basis, stage, geography and edition/scenario/case. Rows across these contexts are not additive. Source selection is the MD5 of the ordered selected snapshot IDs, including empty responses; rebuilding/replaying the same source set retains this identity.

## Trade metrics and denominators

One measure row represents either EUR value or product tonnes. Both are kept independent. The denominator is the single positive native reporting-total row for the same reporter, CN8/reference year, import/export direction and snapshot. For national reporters the denominator is World/all partners, including intra-EU trade. For EU27_2020 it is the native EXT_EU27_2020 external-partner total with fixed 2020 membership. The bloc is not a sum of the six acquired countries.

Country/territory and explicitly typed geopolitical partner rows are eligible for named shares. World and overlapping regional aggregates are excluded from the partner sum. Special partner amounts are disclosed separately. `unallocated = native reporting total - named sum`; it is not silently assigned to countries. A negative residual beyond numeric tolerance makes the denominator unavailable. Numerical noise within max(0.01 EUR or 0.000001 product tonnes, abs(native reporting total) × 1e-9) becomes zero, with the original reconciliation delta preserved.

For named amounts x, positive native reporting total W, shares s=x/W, and unknown share r:

- Partner share is x/W. Rankings refer to reported partner location, not upstream mine origin or ownership.
- Supplier HHI lower bound is sum(s²). Because unallocated trade could belong to an already reported supplier, its conservative upper bound is sum(s²) + 2 × max(s) × r + r².
- Top-k lower bound is the sum of the largest k known shares; upper bound is min(1, lower + r). Top supplier is k=1. HHI is on the 0–1 scale.
- A known leading supplier is guaranteed against residual reassignment only if its amount is at least the second-largest known amount plus all unallocated trade. Ties can remain.
- Trade balance is native reporting-total exports minus imports within one product/year and measure. Imports are CIF and exports FOB; the balance does not establish consumption, origin or domestic production.

`mart_country_material_dependency` is a supplier-exposure mart. Its consumption-based `import_dependency` column is always null with an explicit missing-input reason. Value share or import volume is never substituted for consumption-based dependency.

## Supply concentration

`mart_supply_country_shares` uses the captured named-country plus Other countries expected-output sum as denominator. It does not claim an independently observed World production total. Mining and refining are separate stages and must never be added.

For named shares s and Other countries share r, lower HHI is sum(s²), and upper HHI is sum(s²)+r². Here the residual is explicitly **other** countries, not an allocation to the named countries. Top-k lower bound sums the k largest named shares. Upper bound sums the k largest elements after appending r as one additional country. A residual split into unknown countries cannot support exact ranks or exact HHI. All 48 captured panels currently have opaque residuals.

HHI/top-k values are dimensionless within one native definition. Quantities retain unverified equivalent basis. The 2025 baseline is not certified as an observed actual; later values are scenario projections. Expected supply output is not nameplate capacity.

## Scenario levels and growth

Three series kinds remain explicit: native demand end use, sum of returned demand end uses, and expected supply panel output. Returned end-use sums are not labelled matched primary requirements. They are not added to the end-use detail when reporting a total.

Growth is endpoint / positive native 2025 baseline - 1. CAGR is (endpoint/base)^(1/(end year-2025)) - 1. No growth is returned for the baseline itself or a zero/missing base, missing components, invalid endpoint or changed demand end-use membership. The category-set fingerprint prevents silently changing the aggregate. Supply panel internal country membership may change but the named-plus-residual boundary remains explicit. Sparse source reference years are not interpolated.

CPS is the reference for alternative demand-scenario comparisons at the same edition, case, definition, geography, end-use/sum, period and basis. Relative scenario difference is alternative / positive CPS - 1. Zero reference categories yield unavailable ratios, not zero or infinity. Supply exists only in STEPS and is never cloned into other scenarios.

Physical supply-demand gaps, shortage shares, nameplate capacity and capacity growth remain unavailable: matched primary requirements and verified physical equivalence/capacity inputs are absent.

## Composition change and sensitivity

Adjacent-year composition rows pair the same native CN8 code and basis. Their `conditional_share_change_pp` is 100 × (end share - base share) **only when both shares are reported**, conditional on unverified code continuity. `verified_share_change_pp` remains null. Reported presence patterns are not market entry/exit flags, and absent partners are not zero-filled. Product keys retain both native reference years and both source snapshots.

`mart_supplier_basis_sensitivity` compares value and mass HHI intervals for the same product/year. Difference bounds are mass lower - value upper and mass upper - value lower. Direction is considered stable only when the whole difference interval lies on one side of zero. This is unit-basis sensitivity, not a causal risk rating.

Residual HHI widths expose sensitivity to opaque country allocation; CPS/STEPS/HDS comparisons expose scenario sensitivity. EU27_2020 uses fixed 2020 membership and external trade; national all-partner totals and bloc totals must not be added. Alternative-source and reported-versus-estimated quantity sensitivity remain unavailable without eligible equivalent source series or reliable status classification. A null source flag is not a certification of a measured observation.

## Explainable risk component grain

`mart_material_supply_risk` contains one row per source selection × scope kind/key × geography × reference period × scenario key (edition/scenario/case) × component × comparison contract × lineage snapshot. The comparison contract contains comparison kind, base/end years, stage, measure basis, quantity basis and denominator scope. Historical trade uses the explicit not-applicable scenario member. A 2025→2030 growth record cannot collide with a 2025→2040 record.

Available point metrics have equal lower/value/upper fields. Bounded concentration has lower/upper and a null point. Unavailable metrics have all three null and a reason. Empty IEA supply responses yield unavailable concentration components for the approved stage/year/scenario contract, never zero output. Trade empty slices remain in the request coverage table; annual product dimensions and market values are not invented for them.

Mining/refining HHI, import supplier HHI, demand growth and expected-output growth remain inspectable independently. Import dependency, physical gap and capacity growth are explicitly unavailable. There are no arbitrary weights, normalisation, high/medium/low thresholds or combined score. `composite_risk_score` remains null.
