#!/usr/bin/env python3
"""Offline check using wholly fictional quantities, prices, dates and account refs."""
import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("portfolio_history", ROOT / "scripts/portfolio_history.py")
ph = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ph)

def snapshot(day, quantities, prices, cash):
    at = f"2000-01-{day:02d}T21:00:00Z"
    holdings = [
        dict(account_ref="DEMO", key="crypto:"+symbol, symbol=symbol,
             asset_type="crypto", quantity=str(qty), price=str(price),
             price_at=at, price_source="synthetic-demo")
        for symbol, qty, price in zip(["BTC", "ETH", "SOL"], quantities, prices)
    ]
    return dict(schema_version=1, id=f"synthetic-2000-01-{day:02d}",
                captured_start=at, captured_end=at, timezone="UTC",
                scope="Synthetic demonstration only", scope_refs=["DEMO"],
                complete=True, events=[], events_complete=False,
                role="Fictional offline test; never use as a live baseline",
                accounts=[dict(account_ref="DEMO", label="Fictional account",
                               portfolio=dict(cash=str(cash), total_value="500"))],
                holdings=holdings)

out = Path(sys.argv[1]) if len(sys.argv) == 2 else None
if out is None:
    raise SystemExit("Usage: make_demo.py PRIVATE_OUTPUT_DIRECTORY")
out.mkdir(parents=True, exist_ok=True)
baseline = snapshot(1, [2,10,20], [100,10,5], 100)
current = snapshot(2, [2.5,10,10], [110,8,6], 85)
catalog = ph.read(ROOT/"assets/catalog.json")
data = ph.compare(current, baseline, catalog)
rows = {r["key"]: r for r in data["rows"]}
assert sum(r["allocation"] for r in data["rows"]) == 100
assert rows["crypto:BTC"]["allocation"] == 55
assert rows["crypto:BTC"]["pp"] == 15
assert rows["crypto:BTC"]["position_change_pct"] == 25
assert rows["crypto:BTC"]["price_return_pct"] == 10
assert rows["crypto:ETH"]["position_change_pct"] == 0
assert rows["crypto:ETH"]["price_return_pct"] == -20
assert rows["crypto:SOL"]["position_change_pct"] == -50
assert data["reconciliation_gap_pct"] == 0
assert rows["cash:USD"]["price_return_pct"] is None
assert all(r["trade_quantity_delta"] is None for r in data["rows"])
bad = copy.deepcopy(current)
bad["scope_refs"] = ["OTHER"]
bad["accounts"][0]["account_ref"] = "OTHER"
for h in bad["holdings"]:
    h["account_ref"] = "OTHER"
try:
    ph.compare(bad, baseline, catalog)
except ValueError:
    pass
else:
    raise AssertionError("Changed account scope must be rejected")
history = out/"history"
ph.save(baseline, history)
ph.save(current, history)
ph.save(current, history)  # Identical re-save is safe.
tampered = copy.deepcopy(current)
tampered["holdings"][0]["quantity"] = "999"
try:
    ph.save(tampered, history)
except ValueError:
    pass
else:
    raise AssertionError("An archived snapshot must not be overwritten")
data["date"] = "SYNTHETIC DEMO · 1/2/00"
data["sources"] = "Fictional offline data; no broker connection or actual holdings"
data["position_note"] = "Synthetic quantities; no actual trades"
for name, value in [("baseline",baseline),("current",current),("dataset",data)]:
    (out/(name+".json")).write_text(json.dumps(value,indent=2)+"\n")
subprocess.run([sys.executable,str(ROOT/"scripts/render_graphics.py"),
                str(out/"dataset.json"),str(out/"rendered")],check=True)
print("Passed synthetic allocation, return, quantity, scope and archive checks.")
