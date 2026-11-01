"""Bake data/*.csv into the interactive page.

  python tracker/build_web.py              -> public/index.html (what Vercel serves)
  python tracker/build_web.py --bare X.html -> same page without the <html>/<head> wrapper
"""
import csv, json, os, sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)


def rows(name):
    with open(P("data", name)) as f:
        return list(csv.DictReader(f))


def build():
    grid = defaultdict(lambda: defaultdict(list))
    as_of = None
    for r in rows("fare_grid_2026-11-01.csv"):
        as_of = r["checked_on"]
        grid[f'{r["origin"]}-{r["dest"]}'][r["travel_date"]].append({
            "a": r["airline"], "f": r["flight_no"], "d": r["dep"], "r": r["arr"],
            "s": int(r["stops"]), "p": round(int(r["price_2_adults_inr"]) / 2)})
    for leg in grid.values():
        for lst in leg.values():
            lst.sort(key=lambda x: x["p"])
    hist = defaultdict(lambda: defaultdict(list))
    for r in sorted(rows("google_price_history.csv"), key=lambda r: r["observed_on"]):
        hist[f'{r["origin"]}-{r["dest"]}'][r["travel_date"]].append([r["observed_on"], int(r["lowest_fare_pp_inr"])])
    typ = {}
    for r in rows("google_typical_range.csv"):
        typ[f'{r["origin"]}-{r["dest"]}'] = {"lo": int(r["typical_low_pp_inr"]), "hi": int(r["typical_high_pp_inr"])}
    events = [{"when": r["period"], "dir": r["direction"], "what": r["what_happened"],
               "fare": r["fare_one_way_pp_inr"], "src": r["source"]}
              for r in rows("historical_context.csv") if r["source"].startswith("http") and "google.com" not in r["source"]]
    return {"asOf": as_of, "grid": grid, "hist": hist, "typ": typ, "events": events}


def main():
    data = json.dumps(build(), separators=(",", ":"))
    page = open(P("web", "template.html")).read().replace("/*__DATA__*/null", data)
    head, body = page.split("<!--BODY-->", 1)
    full = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
            + head + "</head>\n<body>\n" + body + "</body>\n</html>\n")
    open(P("public", "index.html"), "w").write(full)
    if "--bare" in sys.argv:
        open(sys.argv[sys.argv.index("--bare") + 1], "w").write(head + body)
    print("built", len(full) // 1024, "KB")


if __name__ == "__main__":
    main()
