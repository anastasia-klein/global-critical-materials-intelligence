# Independent web report

[Open the GitHub Pages report](https://anastasia-klein.github.io/global-critical-materials-intelligence/).

A public HTML/CSS/JavaScript/SVG edition of the four-page Power BI report. It works independently of Microsoft sign-in, Power BI licences, external JavaScript libraries, fonts, map tiles and live source APIs. It serves a fixed snapshot from GitHub Pages; it does not refresh market data automatically.

## Pages and interactions

- **Global Supply Landscape:** six material groups, supply year, separate mining/refining output, country shares, HHI/Top-3 bounds, local SVG world map and full supply timeline.
- **European Trade & Dependency:** material/product, seven reporting areas, year and EUR/product-mass basis; imports/exports, trade balance, top supplier, HHI and fixed-order partner shares.
- **Supply Chain Risk:** all materials or one selected family, supply year, reporting area and independent trade year; physical-output HHI scatter/bars and EUR/mass supplier-HHI table.
- **Future Outlook:** material, endpoint year and graphite definition toggle; three scenario KPI values, demand timelines, end-use bars and STEPS output. End-use ordering stays fixed; unavailable observations remain missing.

Primary filters are encoded in the URL hash for sharing and browser Back/Forward. Selections are remembered independently per page during a visit. Charts provide keyboard-focusable tooltips, data tables and CSV downloads. CSS adapts to narrow screens; the UI uses Avenir Next with Arial/system fallbacks. No font files are redistributed.

The web report implements the report queries directly in JavaScript; it does not embed or execute Power BI/DAX. Layout and map rendering are web-native. The map uses public-domain Natural Earth geometry and the original display anchors; residual Other countries has no point. Tooltips and the methodology disclose scope and measurement limits.

## Data and reproducibility

Run from the repository root:

```sh
python scripts/build_web_data.py
node --test web/tests/*.test.mjs
python -m http.server 8768 --directory web
```

Open `http://localhost:8768/`. The builder requires only Python's standard library. It verifies all 24 original report CSV fingerprints before projecting selected fields into `web/data/snapshot.json`; partner presentation groups use the same SUM/null semantics as the Power BI chart. It strips lineage payloads from the browser projection, while retaining the selection key and input hashes. The original lineage, source SQL and attributions remain in the committed report export manifest. `world.json` retains only country geometry and names.

Source capture: IEA 30 October 2026; Eurostat 30 October–1 November 2026. Demand 2025–2050; expected supply 2025–2040; trade 2018–2024 with sparse product/year slices. The 2025 IEA baseline is not certified here as an independently observed actual. This is a derived analysis, not an IEA/Eurostat product or endorsement.

## Checks and publishing

Node tests independently read the original CSV inputs and compare report queries over 48 supply panels, 588 trade selections and 126 scenario endpoints. They verify EU27 external-only scope, independent metric bases, fixed categories, null/zero handling, graphite scope and documented examples. DOM contract tests exercise filter handlers without a browser; SVG tests check valid finite coordinates at mobile and desktop chart sizes. These checks do not establish native browser rendering or visual fidelity.

GitHub Actions rebuilds the snapshot, rejects uncommitted data drift, runs the tests and publishes only the static site files via Pages. No credentials or server-side application are needed at runtime. Repository Settings → Pages must use **GitHub Actions** as the publishing source. The workflow handles subsequent updates when web source or report inputs change.

[Original project and findings](../README.md) · [Metric definitions](../docs/methodology/metrics.md) · [Source rights and attribution](../NOTICE.md).
