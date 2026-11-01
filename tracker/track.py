"""Take one price snapshot of every DEL<->SXR flight for the trip window.

Appends one row per (flight, travel date) to data/snapshots.csv. Run daily
(GitHub Actions does this automatically - see .github/workflows/track.yml).
"""
import csv, datetime as dt, os, sys, time
from zoneinfo import ZoneInfo
sys.path.insert(0, os.path.dirname(__file__))
import gflights
from config import ADULTS, ROUTES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "snapshots.csv")
FIELDS = ["checked_at_ist", "days_before", "travel_date", "origin", "dest", "airline",
          "flight_no", "dep", "arr", "stops", "adults", "price_total_inr", "price_per_person_inr"]


def daterange(a, b):
    d = dt.date.fromisoformat(a)
    while d <= dt.date.fromisoformat(b):
        yield d
        d += dt.timedelta(days=1)


def main():
    now = dt.datetime.now(ZoneInfo("Asia/Kolkata"))
    new = not os.path.exists(OUT)
    rows = 0
    with open(OUT, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if new:
            w.writeheader()
        for origin, dest, start, end in ROUTES:
            for day in daterange(start, end):
                if day < now.date():
                    continue
                flights = []
                for attempt in range(3):
                    try:
                        flights = gflights.search(day.isoformat(), origin, dest, adults=ADULTS)
                        break
                    except Exception as e:
                        print(f"retry {origin}-{dest} {day}: {e}", file=sys.stderr)
                        time.sleep(5 * (attempt + 1))
                for x in flights:
                    if not x["price_total_inr"]:
                        continue
                    w.writerow({
                        "checked_at_ist": now.strftime("%Y-%m-%d %H:%M"),
                        "days_before": (day - now.date()).days,
                        "travel_date": day.isoformat(), "origin": origin, "dest": dest,
                        "airline": x["airline"], "flight_no": x["flight_no"], "dep": x["dep"],
                        "arr": x["arr"], "stops": x["stops"], "adults": ADULTS,
                        "price_total_inr": x["price_total_inr"],
                        "price_per_person_inr": round(x["price_total_inr"] / ADULTS),
                    })
                    rows += 1
                print(f"{origin}->{dest} {day}: {len(flights)} flights", flush=True)
                time.sleep(2)
    print(f"wrote {rows} rows")
    if rows == 0:
        sys.exit("no prices captured - Google Flights may have changed its page")


if __name__ == "__main__":
    main()
