import json, sys, time, datetime as dt
import gflights
start, end, o, d, adults = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5])
day = dt.date.fromisoformat(start); res = {}
while day <= dt.date.fromisoformat(end):
    for attempt in range(3):
        try:
            r = gflights.search(day.isoformat(), o, d, adults=adults); break
        except Exception as e:
            r = []; time.sleep(3)
    priced = [x for x in r if x["price_total_inr"]]
    ns = [x["price_total_inr"] for x in priced if x["stops"] == 0]
    anyp = [x["price_total_inr"] for x in priced]
    res[day.isoformat()] = {"min_nonstop": min(ns) if ns else None, "min_any": min(anyp) if anyp else None,
                            "n_flights": len(r), "flights": r}
    print(day, res[day.isoformat()]["min_nonstop"], res[day.isoformat()]["min_any"], len(r), flush=True)
    day += dt.timedelta(days=1); time.sleep(1.5)
json.dump(res, open(sys.argv[6], "w"), indent=1)
