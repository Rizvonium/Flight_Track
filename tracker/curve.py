"""Empirical booking curve: price history for near-term departures (they cover ~60 -> ~2 days before)."""
import csv, datetime as dt, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import gflights
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "booking_curve_samples.csv")
start, end, step = sys.argv[1], sys.argv[2], int(sys.argv[3])
rows = []
for o, dst in (("DEL", "SXR"), ("SXR", "DEL")):
    d = dt.date.fromisoformat(start)
    while d <= dt.date.fromisoformat(end):
        ins = None
        for a in range(4):
            try:
                _, ins = gflights.fetch(d.isoformat(), o, dst, adults=1); break
            except Exception:
                time.sleep(10 * (a + 1))
        if ins:
            for obs, v in ins["history"]:
                rows.append({"origin": o, "dest": dst, "travel_date": d.isoformat(), "observed_on": obs,
                             "days_before": (d - dt.date.fromisoformat(obs)).days, "lowest_fare_pp_inr": v})
        print(o, dst, d, "ok" if ins else "none", flush=True)
        d += dt.timedelta(days=step); time.sleep(4)
with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("rows", len(rows))
