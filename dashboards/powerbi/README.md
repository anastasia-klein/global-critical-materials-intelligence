# Power BI report

**[Open the interactive report](https://app.powerbi.com/view?r=eyJrIjoiYWM2MzI5NjMtOGUzNi00ZDI1LThkMzYtOGUwNTU3NWJmMjI1IiwidCI6IjM5YTFiNjM3LTFmODktNGQzOS1iZjNlLWFiNzczZGRmOGJhZSJ9)**

The report explores global mining/refining concentration, European trade exposure and material demand scenarios across four pages. Its semantic model contains 25 tables, 23 one-direction relationships and 103 explicit measures. Versioned CSV inputs and the source-SQL/fingerprint manifest are under `data/`.

## Open and reproduce

Use [the setup script](../../scripts/Update-PowerBI.ps1) to prepare a local project with configured file paths, then select **Refresh** in Power BI Desktop. See [report setup and validation](../../docs/operations/powerbi.md).

## Filters and interpretation

- Material tiles select copper, cobalt, lithium, nickel, graphite or magnet rare earths. Native IEA definitions and traded CN8 forms remain distinct. The All grades toggle changes only the graphite definition.
- Reporting area, basis and year retain their own scopes. EU27 covers external trade; national reporters include intra-EU partners. Material selections are independent across pages.
- Mining/Imports use forest green; Refining/Exports use leaf green. Material tile colours identify chemical categories, not risk levels.
- Country-share bars include the opaque Other countries residual; the map shows only geographically identified countries. Each supply stage has its own denominator.
- Import-partner and end-use categories retain a fixed order. Other partners groups the remaining reported partners without rebasing totals. Reported zeroes stay zero; missing observations remain blank.
- Outlook compares CPS, STEPS and HDS using consistent colours and separate bars. Scenario levels are alternatives and must not be added. Supply is available only for STEPS, through 2040; demand extends to 2050.

[Report interpretation](../../docs/methodology/report_interpretation.md) explains country residuals, HHI bounds, the scatter diagonal and scenario assumptions. [Metric definitions](../../docs/methodology/metrics.md) document the calculations.

## Attribution

IEA Critical Minerals Dataset, GCMO2026 (CC BY 4.0), captured 30 October 2026; Eurostat DS-045409, captured 30 October–1 November 2026. Analysis by Anastasia Klein. Source data and adaptations retain the notices in [NOTICE](../../NOTICE.md).
