# Power BI report

The report contains four pages, 25 tables, 23 one-direction relationships and 86 explicit measures. Portable CSV inputs and their source-SQL/fingerprint manifest are versioned under data/. Numeric columns have no implicit summarisation.

Use [the Windows update script](../../scripts/Update-PowerBI.ps1) from the repository checkout. It pulls main and opens a separate local runtime with DataFolder configured; do not edit the checkout parameter just to configure a VM path. See [operation and acceptance checks](../../docs/operations/powerbi.md).

Material-family tiles filter both native IEA definitions and native Comext product forms. Graphite/all-grades remain separate. Reporting area, measure basis and reference-year choices preserve their own scopes. Chart selections do not rebase denominators. Material selection is not synchronised between pages; Risk starts with all families, other pages with lithium.

Mining/Imports use forest green; Refining/Exports leaf green. Material tile colours identify chemical categories, not risk levels. Avenir Next is the source font; the VM script uses Arial if Avenir Next is unavailable. No font files are distributed.

Fixed import-partner categories are leading suppliers per reporter/product in 2024 EUR, alphabetically ordered plus Other partners. Remaining reported amounts are grouped without rebasing native totals. End-use axes retain all eight source category names. Zero is a reported zero; missing data stay blank.

Source: IEA (2026), Critical Minerals Dataset, GCMO2026, https://www.iea.org/data-and-statistics/data-product/critical-minerals-dataset, CC BY 4.0; source capture 30 October 2026. Eurostat DS-045409; source captures 30 October–1 November 2026. Analysis by Anastasia Klein. Source data and adaptations retain the notices in [NOTICE](../../NOTICE.md). Native Desktop rendering/DAX acceptance is pending.
