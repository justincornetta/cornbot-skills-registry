# Approved layouts

Refer to `assets/example-donut.png` and `assets/example-comparison.png` (synthetic data). The list is selected version 2 plus asset price returns. Relative allocation change percent was replaced with asset return and net position change.

- Navy #03101e, subtle curved texture, gold #e8b153, warm white #f4f1e9, muted #aeb9c6. Gray baseline bars and gold current bars. Serif headings and readable sans-serif data labels. Vector crown/wordmark.
- Donut: current weights, accurate logos, callout labels and JMJ center. Major holdings get side labels; smaller holdings use a top strip. Adjust spacing/count and check leaders, tiny slices and label collisions.
- List: rank by current weight; identity, gray old weight above gold current weight, signed allocation change pp, signed asset price return %, signed net position change %. Cash has Cash movement and no shares-based return. Unavailable quantities remain Pending. Material exited holdings appear in a small section; merely falling below threshold is not an exit.
- Footer: sources, exact pull window, scope, cutoff, return period/basis, excluded income and unresolved quantity-change causes. Asset price return is not personal P&L.
- Green #80c2ac and muted red #d99493 with explicit plus/minus signs. Percent and pp units remain distinct.
- ETH ETF uses Grayscale branding, ETH crypto uses Ethereum. BMNR is BitMine Immersion Technologies, not Bitdeer. Verify company names/rebrandings on update.

Logo provenance is in `assets/logos/sources.json`; catalog entries map canonical keys to filenames. User's preferred uploads for IREN, EOSE and ATAI override existing artwork. No separate preferred uploads were available when the skill was created; IREN/EOSE use official artwork, ATAI was absent. If ATAI returns, fetch current official atai Beckley artwork. New assets require official/user-supplied logos and catalog entries, not generated logo approximations. Cream badges preserve dark wordmarks. Retain colors/proportions.

Renderer produces self-contained SVG. Node exporter uses bundled sharp: opaque 2700-pixel square donut, 2800-pixel-wide list with adaptive height. Inspect both PNGs for clipping, incorrect identity/date, stale footnotes and overlap. PNG reference previews are design guides, not current-data exports.
