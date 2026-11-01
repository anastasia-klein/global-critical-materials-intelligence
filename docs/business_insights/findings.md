# Findings from the included report capture

Run `python scripts/run_findings.py` with the warehouse dependencies installed. [The SQL](findings.sql) reads the committed report projections after verifying their fingerprints. The export manifest provides their exact underlying warehouse SQL and source selection. No live source request is needed.

| Finding | Evidence and context | Where to inspect |
|---|---|---|
| Lithium refining is more concentrated than mining | 2030 STEPS lower HHI 0.483 vs 0.185 | Global Supply Landscape: Li, 2030; HHI cards and country bars. Supply Chain Risk: 2030, clear material selection; paired HHI bars |
| Graphite refining is particularly concentrated | 2030 lower HHI 0.815 vs mining 0.348; exact Graphite definition | Risk: 2030; C paired bars and scatter. Global: C, 2030; refining country shares |
| Nickel has greater concentration at the mining stage | 2030 mining lower HHI 0.499 vs refining 0.325 | Risk: 2030; Ni paired bars and below-equality scatter point |
| Germany's lithium-carbonate import value is led by Chile | 2024 EUR shares: Chile 40.6%, Belgium 26.8%, United States 24.6% | Trade: Li, Germany, 2024, Value EUR; fixed-order import-partner bars |
| EVs dominate returned lithium end-use demand | STEPS 2040: 765.3 kt of 932.5 kt, approximately 82.1% | Future Outlook: Li, STEPS, 2040; end-use bars and endpoint card |

The concentration comparisons concern lower bounds in named/residual source panels; inspect upper bounds before making an interval-sensitive decision. Expected supply is a scenario estimate, not an observed historical production panel or installed capacity. Graphite/all-grades are different scopes. Partner shares are reported trading locations, not mine origin; CN8 lithium carbonate is not all lithium trade. EV share refers to the sum of returned native end uses, not verified primary-material requirements. Rounded display values are not new source precision.

Visual locations describe the authored report. Native Desktop interactions and DAX values must pass the operation checklist before using screenshots as runtime evidence. These findings can also be checked directly with the SQL, independently of Desktop.
