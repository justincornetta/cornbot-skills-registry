# Recipient setup

1. Install this complete skill folder in a Codex skill location. Python 3.10+ and Node.js 20.9+ are required by the included helpers. Run `npm ci` in the skill folder for the locked Sharp dependency. Python helpers use only the standard library.
2. Connect your own Robinhood MCP server using the provider’s supported configuration and OAuth flow. Discover its current read-only tools. Do not copy another user’s credentials or authentication store. If the connection is unavailable, stop the live update.
3. Pick a private portfolio working directory outside the repository and skill folder. Store history, account configuration, raw evidence and runs there. Confirm account selection on first use; retain masked references only.
4. Record `scope_refs` and `materiality_threshold_pct` (default `0.04`) in local `history/config.json`. The helper does not automatically read this file: use its threshold explicitly when comparing.
5. Read `data-workflow.md` for schema, reconciliation and event rules. The first complete validated capture establishes a baseline; never substitute the synthetic demo or invent starting quantities. With no baseline, label the capture baseline-only and do not claim a before-and-after comparison.
6. For a later update, collect complete holdings and comparable quotes, reconcile account scope and broker totals, and compare to your latest saved snapshot. Inspect `reconciliation_gap_pct` and resolve material gaps before rendering or advancing history.

## Commands

Run from this skill’s directory; replace uppercase arguments with your own private paths:

```sh
python3 scripts/portfolio_history.py compare CURRENT.json BASELINE.json --catalog assets/catalog.json --threshold .04 --out DATASET.json
python3 scripts/render_graphics.py DATASET.json OUTPUT_DIRECTORY
node scripts/export_pngs.mjs OUTPUT_DIRECTORY
# Only after data and both graphics have been validated:
python3 scripts/portfolio_history.py save CURRENT.json --history HISTORY_DIRECTORY
```

`save` creates the history and snapshots directories when needed. Do not use it for a layout-only edit. The renderer writes chart data into the output directory; keep that directory private too. The sample scope and prices produced by `examples/make_demo.py` are fictional and must never become live history.

The supplied catalog does not contain usable logos for every possible security. Add official/user-provided artwork and a catalog entry when necessary. The renderer deliberately stops when a logo is missing. It has layout limits (22 positive donut labels; five exited holdings); adapt and visually verify the layout when those are exceeded. Titles and the wordmark are currently JMJ-specific in the renderer.

Optional Excel export from the original installation is excluded because it relied on a host-specific Artifact Tool runtime and owner history. No private Notion access or Codex-bundled runtime is required for the distributed core helpers.
