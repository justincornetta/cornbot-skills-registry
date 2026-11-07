---
name: jmj-capital-13f
description: Create navy-and-gold Robinhood portfolio graphics, including allocations, asset price returns, and net position changes from private dated snapshots.
---
# JMJ Capital 13F

Create two PNGs: the approved square navy/gold donut and before-and-after ranked list with allocation change in percentage points, asset price return, and net position change. Synthetic reference layouts: `assets/example-donut.png` and `assets/example-comparison.png`. These use invented allocations and are not the owner's holdings. Preserve their titles (donut: “JMJ Capital 13F”; list: “JMJ Capital Portfolio”). The skill name is JMJ Capital 13F; these are personal portfolio graphics, not SEC filings.

## Data and history

- Use read-only Robinhood MCP tools. Never place, review, cancel or modify trades through this skill. If authentication fails, request reconnection and stop the live update; cached data may support an explicitly labeled preview.
- Read [data-workflow.md](references/data-workflow.md) for each update. Persistent history is a recipient-selected private `HISTORY` directory outside this repository and the skill folder. `config.json` records scope/cutoff; `latest.json` identifies the forward comparison baseline. Use the latest saved snapshot unless the user specifies a date.
- Re-fetch accounts. On first use, confirm which of the recipient's accounts belong in scope and record masked identifiers locally. Never assume the original owner's account selection. Preserve the same scope across a comparison. Reconcile new/disappearing accounts before attributing changes to trades. Previously included accounts remain in scope even if now empty.
- Collect complete quantities for equities, crypto and options, all pagination, net portfolio cash and timestamped quotes. Preserve decimal quantity strings and instrument identities. ETH ETF and ETH cryptocurrency remain separate. Capture short options with signed values.
- Net position change measures split-adjusted shares/coins, independent of prices. Transfers, rewards, reinvestment and exercise/assignment require reconciliation. Use filled executions to attribute trades. A holdings difference alone cannot prove net buying/selling. Unchanged net quantity does not mean no trades. Missing starting quantities mean Pending, never zero.
- Save the exact snapshot used for charts, including tiny holdings, quote times, scope and discrepancies. Archive immutably before advancing the baseline. A layout-only revision must not advance it. Baseline-only captures must be labeled separately from approved graphic pulls.

## Graphics

- Read [design.md](references/design.md). Preserve navy, subtle texture, gold accents, elegant serif titles, crown/wordmark and accurate logos. Preferred user-supplied IREN/EOSE/atai Beckley logos override bundled assets. Adapt rows and callouts to holding count.
- No monetary amounts or full account numbers in graphics, notes or Excel review copies. Internal local snapshots retain prices/values for calculation. Compute at full precision, display percentages to two decimals.
- Material cutoff is 0.04%, inferred from the original smallest label and retained in the approved design. Exclude smaller labels, retain every holding in history/denominator. Use zero allocation baseline for new material holdings only when the baseline is complete. Keep material exited holdings in “No longer held”; disappearance alone does not prove a sale.
- Asset price return is market performance over the comparison period, not personal P&L. Use comparable timestamped price bases and split adjustments. Exclude distributions/staking income and state that. Cash is N/A; missing starting market data is unavailable. A newly acquired holding may have full-period market return.
- Verify counts, total full-precision allocations, signs, timestamps, asset identity, exclusions, no monetary amounts and no overlap/clipping. Visually inspect both final PNGs. Export opaque PNGs and self-contained SVGs; save dated chart data and source snapshot. Deliver both PNGs and a short pull-time/scope/methodology note. After a validated live update, retain its exact snapshot as the next baseline.

## Helpers

- `scripts/portfolio_history.py save INPUT --history HISTORY`: archive a validated normalized snapshot and advance the local forward baseline.
- `scripts/portfolio_history.py compare CURRENT BASELINE --catalog assets/catalog.json --out DATASET`: calculate net weights, quantity changes and price returns. Refuses incomplete/changed-scope comparisons. Read schema/event rules first.
- `scripts/render_graphics.py DATASET OUTPUT_DIRECTORY`: render approved-style SVGs; `scripts/export_pngs.mjs OUTPUT_DIRECTORY` exports PNGs through bundled sharp.

Use Python 3.10+ for the Python helpers. For PNG export, run `npm ci` in this skill folder to install the locked Sharp dependency, then run `node scripts/export_pngs.mjs OUTPUT_DIRECTORY`. No bundled Codex runtime or private Notion access is required for these helpers. Optional Excel export from the owner's installation is not included because it depends on a host-provided Artifact Tool runtime and historical owner data.

No credentials, complete account numbers, source snapshots, or generated live chart data belong in this repository. Keep financial history outside the package.

## First use and portability

Read [setup.md](references/setup.md) before the first run. The recipient must connect their own Robinhood MCP server. This package does not include authentication, market data, account configuration, or a prior baseline.

With no baseline, capture and validate the first snapshot and label it **baseline-only**. Do not invent a comparison or mark starting quantities as zero. On a later update, compare against that recipient's latest validated capture.

The bundled catalog is a starting identity map, not a statement of current holdings. Verify names and instrument identities on every live run. Assets without a supplied logo require official or user-supplied artwork before rendering. Preserve the JMJ design by default; changing titles and wordmarks requires editing the exported renderer.

For offline validation only, `examples/make_demo.py` creates two synthetic snapshots and exercises comparison, archive idempotency, and both SVG renderers. Its examples are fictional and must never seed live history.

Distribution source: exported from the owner's canonical skill on 2026-11-07, with private history and host-specific dependencies removed. The original installed skill and Notion source remain unchanged.
