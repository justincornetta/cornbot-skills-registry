# Data capture and position changes

## Robinhood reads

Discover current tool schemas. Read-only names currently start `mcp__robinhood_trading__`.

Fetch `get_accounts`, then `get_equity_positions`, `get_option_positions(nonzero=true)` and `get_portfolio` for every account in scope. Linked crypto uses `get_crypto_positions(rhs_account_number=...)`, not the crypto account number. Follow every `next` cursor, deduplicate account/instrument records. Failed/missing pages cannot mean no holdings.

Fetch equity quotes in batches of at most 20; pick the most recent valid regular/nonregular trade by timestamp. Use crypto marks (same account routing) and option marks times actual multiplier. Zero/unavailable prices are missing data. Save per-quote timestamps and the pull window. Use total quantity, not sellable/transferable quantity. Crypto total can exclude pending withdrawal holds; reconcile transfers before attributing differences. Equity negative quantity means short; options positive quantity plus `type=short` must be signed negative.

Cash is summed portfolio cash, not buying power. Reconcile all signed positions plus net cash against broker totals and inspect gaps by account/asset class. Re-fetch inconsistencies instead of assuming an options-summary error: a summary can disagree with detailed positions, especially for short options.

For trade attribution fetch equity/crypto/option order history with all pagination. Include actual executions in `(baseline, current]`, including partially filled orders created before the baseline. Created-at filtering alone misses such fills. Ignore unfilled cancellations/rejections. History tools may not expose transfers, corporate actions and rewards; keep these unresolved visibly. A verified quantity difference can be shown with a quantity-only caveat while net trade attribution remains unavailable.

## Persistent schema

`history/snapshots/<id>.json` are immutable. `history/latest.json` is a forward-baseline pointer. `history/config.json` holds scope/cutoff. Any recipient-owned allocation-only reference must be kept separately from quantity snapshots. No historical owner data is bundled. A repeated identical save is idempotent; never replace a snapshot ID with different data. No credentials/full account numbers.

Normalized snapshot:

- `schema_version: 1`, `id`, `captured_start`, `captured_end` (UTC ISO recommended), `timezone`, `scope`, `scope_refs` (stable masked suffix identifiers), `complete: true` only when every scoped account/page is read.
- `accounts`: `account_ref`, `label`, `portfolio` with decimal-string broker cash/value breakdown.
- `holdings`: `account_ref`, canonical `key` (`equity:IREN`, `crypto:ETH`, `option:<UUID>`), `asset_type`, `symbol`, decimal-string `quantity`, `price`, `price_at`, `price_source`. Options require `position_type`, `multiplier`. Crypto may record `quantity_basis`.
- `events` on CURRENT are adjustments for the chosen comparison interval only: canonical `key`, `split_factor` (default 1), `nontrade_quantity_delta` (default 0 in ending units), effective date and evidence. Set `events_complete: true` only after checking the interval. Empty events with false means unverified. Reinvestment counts as nontrade for user-directed activity unless user chooses otherwise.
- `graphic_status`, `role` distinguish published-chart pulls from baseline-only captures. Keep output paths/exclusions with the dated run.

For reorganized/renamed equities use a documented instrument mapping. The equity positions response currently provides tickers rather than stable IDs; do not equate ticker matching with identity across corporate actions.

## Math

Signed position value = signed quantity × price × option multiplier if applicable. Denominator = all signed position values + net cash. Weight = 100 × value / denominator. Displayed weights are not renormalized. Δ allocation is current minus old weight, in percentage points.

Normalize old quantity by cumulative split factor. Net quantity Δ = current − normalized old. Net position change % = 100 × Δ / abs(normalized old). Verified old zero yields New, no infinite percentage. Current zero yields No longer held, cause unverified absent evidence. Unknown old quantity yields Pending. Short exposure needs explicit wording; generic Added/Trimmed long-position wording can mislead.

When nontrade flows are verified, trade-attributable Δ = quantity Δ − nontrade_quantity_delta, separately from overall net quantity change. Validate with filled executions before labeling net bought/sold. Zero net change may still include trades.

Price return = 100 × (ending / adjusted starting price − 1). Adjusted starting price = stored old price / split factor. Require comparable price source/basis. Complex reorganizations need normalized prices or unavailable returns. Future Robinhood crypto snapshot marks support same-source comparisons without historical endpoints.

If a new holding was not owned in the prior snapshot, its starting quantity can be verified zero while its starting market price is absent. Fetch historical market prices at the prior snapshot's timestamp when available, preserving the same comparison period and compatible price basis, then enrich the chart dataset's return/source fields. Do not substitute a since-purchase return. Include crypto quote routing in future `price_source` identifiers so routing changes cannot silently look comparable; record account routing locally and mark return unavailable when venue continuity cannot be established.

For a date-only baseline, document the time assumption and use comparable split-adjusted historical quotes; reject interpolated bars. Check current tool coverage before a historical-price fallback. If no compatible starting price exists, mark return unavailable. Exclude dividends, distributions and staking rewards.

## Negative positions and donut

Net-asset portfolios with shorts can have positive weights totaling more than 100%. Pie geometry cannot represent negative slices. The helper scales arcs across positive assets and explicitly labels “positive-asset composition” when negatives exist; labels/list retain net-portfolio weights, and negative exposure is disclosed separately. Never draw negative arcs or omit liabilities from the denominator. Adapt the panel if negative positions become numerous.

## Review exports

JSON is authoritative. If creating a separate review workbook, omit monetary amounts and account numbers, and disclose rounding of high-precision quantities. No historical owner workbook or Excel helper is distributed.
