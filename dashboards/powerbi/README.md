# Power BI report

The report contains four pages, 25 tables, 23 one-direction relationships and 103 explicit measures. Portable CSV inputs and their source-SQL/fingerprint manifest are versioned under data/. Numeric columns have no implicit summarisation.

Use [the Windows update script](../../scripts/Update-PowerBI.ps1) from the repository checkout. It pulls main and opens a separate local runtime with DataFolder configured; do not edit the checkout parameter just to configure a VM path. See [operation and acceptance checks](../../docs/operations/powerbi.md).

Material-family tiles filter both native IEA definitions and native Comext product forms. Graphite/all-grades remain separate. Reporting area, measure basis and reference-year choices preserve their own scopes. Chart selections do not rebase denominators. Material selection is not synchronised between pages; Risk starts with all families; Supply and Outlook start with copper, Trade with rare earths. Supply starts at 2025 and Outlook at 2030. All grades starts selected and only affects graphite.

Mining/Imports use forest green; Refining/Exports leaf green. Material tile colours identify chemical categories, not risk levels. The report preserves the reader-side font chain `'Avenir Next', Arial, sans-serif`; publishing from Windows keeps this chain. No font files are distributed.

Fixed import-partner categories are leading suppliers per reporter/product in 2024 EUR, alphabetically ordered plus Other partners. Remaining reported amounts are grouped without rebasing native totals. End-use axes retain all eight source category names. Zero is a reported zero; missing data stay blank.

Source: IEA (2026), Critical Minerals Dataset, GCMO2026, https://www.iea.org/data-and-statistics/data-product/critical-minerals-dataset, CC BY 4.0; source capture 30 October 2026. Eurostat DS-045409; source captures 30 October–1 November 2026. Analysis by Anastasia Klein. Source data and adaptations retain the notices in [NOTICE](../../NOTICE.md). Native Desktop rendering/DAX acceptance is pending.

Outlook compares CPS, STEPS and HDS simultaneously in each KPI and demand chart. Colours are fixed across visuals. End uses use three bars at a common baseline: 17 source end-use/year groups are nonmonotonic in CPS/STEPS/HDS order, so fixed additive increment stacks would misrepresent scenario levels. Supply still has only STEPS data. All grades is a native pill toggle at the top of the Graphite card on Outlook: On/green/right uses all grades; Off/grey/left restores the Graphite default. It only changes graphite scope. Supply and outlook years use compact single-row buttons.

Map marker identities are country × stage, with no Legend/Series binding that could trigger automatic pie charts. Marker colours use the same fixed stage colours as the other supply visuals. Country offsets are documented in accessibility/tooltips and source metadata. Number annotation boxes use fixed layer order and sufficient text height. Native Service hover behaviour still requires verification after publication.

The graphite scope control uses two embedded SVG images with a drawn circular thumb and explicit On/Off labels, including selected hover and press states. Its artwork does not depend on a callout font or external image hosting.

Interpretation of EU27, country residuals, physical-output versus trade HHI, the scatter diagonal and IEA scenarios: [report interpretation](../../docs/methodology/report_interpretation.md). Country shares include percentage labels; the report header identifies the work as exploratory analysis of public IEA and Eurostat data.
