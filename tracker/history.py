"""Download Google Flights' ~60-day lowest-fare history for each travel date.

Writes data/google_price_history.csv (per-person, one-way, any stops) and
data/google_typical_range.csv. Re-running extends the history; old points are kept.
"""
import csv, datetime as dt, os, sys, time
sys.path.insert(0, os.path.dirname(__file__))
import gflights
from config import ROUTES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HIST = os.path.join(ROOT, "data", "google_price_history.csv")
TYP = os.path.join(ROOT, "data", "google_typical_range.csv")


def load(path, key):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return {key(r): r for r in csv.DictReader(f)}


def main(routes=ROUTES):
    hist = load(HIST, lambda r: (r["origin"], r["dest"], r["travel_date"], r["observed_on"]))
    typ = load(TYP, lambda r: (r["origin"], r["dest"], r["travel_date"], r["checked_on"]))
    today = dt.date.today().isoformat()
    for origin, dest, start, end in routes:
        d = dt.date.fromisoformat(start)
        while d <= dt.date.fromisoformat(end):
            ins = None
            for attempt in range(4):
                try:
                    _, ins = gflights.fetch(d.isoformat(), origin, dest, adults=1)
                    break
                except Exception as e:
                    time.sleep(10 * (attempt + 1))
            if ins:
                for obs, v in ins["history"]:
                    hist[(origin, dest, d.isoformat(), obs)] = {"origin": origin, "dest": dest,
                        "travel_date": d.isoformat(), "observed_on": obs, "lowest_fare_pp_inr": v}
                typ[(origin, dest, d.isoformat(), today)] = {"origin": origin, "dest": dest,
                    "travel_date": d.isoformat(), "checked_on": today, "current_low_pp_inr": ins["current_low"],
                    "typical_low_pp_inr": ins["typical_low"], "typical_high_pp_inr": ins["typical_high"]}
                print(f"{origin}->{dest} {d}: now {ins['current_low']} typical {ins['typical_low']}-{ins['typical_high']}, {len(ins['history'])} pts", flush=True)
            else:
                print(f"{origin}->{dest} {d}: no insight", flush=True)
            d += dt.timedelta(days=1)
            time.sleep(4)
    for path, rows in ((HIST, hist), (TYP, typ)):
        rows = sorted(rows.values(), key=lambda r: tuple(r.values()))
        if rows:
            with open(path, "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader(); w.writerows(rows)


if __name__ == "__main__":
    main()
