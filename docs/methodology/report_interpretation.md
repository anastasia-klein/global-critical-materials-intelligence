# Reading the report

## Scope and geography

This is exploratory analysis of the captured public IEA and Eurostat datasets. The supply page shows the selected IEA expected-output panel, not a complete independently observed production census. Its 2030/2035/2040 values are projections. The native 2025 baseline is not certified as an observed actual in this project.

EU27 · Extra-EU is the whole 27-member EU bloc, with fixed 2020 membership and external partners only. It does not mean the countries missing from the country selector. National reporters include their intra-EU trade. Never add a national reporter to the bloc or infer a common denominator between them.

A small disclosed EU output share does not quantify European consumption-based import dependency. Other countries is an opaque residual and may contain EU production. Geographic Europe is broader than the EU. Missing country-level disclosure is not evidence of no production.

## Country shares

Country bars include individually identified countries and the source residual Other countries. The residual is an undisclosed group, not one country; it stays off the map because it has no single location. Within an available material/year/stage panel, the complete bars sum to 100% before display rounding. Mining and refining have independent denominators. Selecting or scrolling countries does not rebase the shares.

## HHI and the diagonal

The supply scatter and paired supply-concentration bars use country shares of expected physical output, expressed in native-scope tonnes, separately for each stage. They do not use EUR or import trade quantities. HHI is dimensionless on a 0–1 scale: sum of squared country shares. The plotted lower bound excludes the unknown allocation of Other countries; the upper bound treats the residual as one additional country. See [metric contracts](metrics.md).

X is mining HHI and Y is refining HHI. Above the equality diagonal, refining's lower-bound concentration exceeds mining's; below it, mining is more concentrated. This does not identify a physical surplus, deficit or conversion yield. Mining and refining volumes must not be subtracted to infer a balance.

The supplier table separately compares HHI based on import value (EUR) with HHI based on product mass (tonnes). These refer to reported partners, not upstream mine origin.

## Scenario attribution and graphite

The CPS, STEPS and HDS series are IEA scenarios, not project-generated forecasts. CPS reflects enacted policy; STEPS explores current policy settings; HDS illustrates a higher-demand pathway. The 2026 report defines them on page 18.

Graphite's returned STEPS demand sum peaks in 2035. Its EV component falls between 2035 and 2050 while grid-storage demand rises. IEA discusses anode substitution by silicon, lithium metal and hard carbon on page 171. The capture does not quantify each technology's causal contribution. Keep Graphite and Graphite: all grades separate.

Source: [IEA, Global Critical Minerals Outlook 2026, pages 18, 171 and 344](https://www.iea.org/files/19c60aa0-ee07-4a20-a138-33c967ac5008/GlobalCriticalMineralsOutlook2026.pdf), CC BY 4.0. Captured values and SQL lineage: [report export manifest](../../dashboards/powerbi/data/export_manifest.json).
