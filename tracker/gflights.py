"""Thin, tolerant wrapper around fast-flights (Google Flights scraper)."""
import datetime as dt, json, os
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")
from selectolax.lexbor import LexborHTMLParser
from fast_flights import FlightQuery, Passengers, create_query, fetch_flights_html


def _t(v):
    v = v or [0, 0]
    return f"{(v[0] or 0):02d}:{(v[1] if len(v) > 1 and v[1] else 0):02d}"


def search(date, origin, dest, adults=1, nonstop_only=False):
    """List of flights (price_total_inr is for all `adults`)."""
    return fetch(date, origin, dest, adults, nonstop_only)[0]


def _insight(payload):
    """Google's 'price insights' block: typical range + ~60-day lowest-fare history."""
    try:
        p = payload[5]
        hist = [(dt.datetime.fromtimestamp(ts / 1000, IST).date().isoformat(), v) for ts, v in p[10][0]]
        return {"current_low": p[1][1], "typical_low": p[4][1], "typical_high": p[5][1], "history": hist}
    except (IndexError, TypeError, KeyError):
        return None


def fetch(date, origin, dest, adults=1, nonstop_only=False):
    """Returns (flights, insight). Raises RuntimeError if Google returned no data block."""
    q = create_query(
        flights=[FlightQuery(date=date, from_airport=origin, to_airport=dest)],
        trip="one-way", seat="economy", passengers=Passengers(adults=adults),
        language="en-US", currency="INR", max_stops=0 if nonstop_only else None,
    )
    html = fetch_flights_html(q, proxy=os.environ.get("HTTPS_PROXY"))
    tree = LexborHTMLParser(html)
    script = tree.css_first(r"script.ds\:1")
    if script is None:
        raise RuntimeError("no data block (rate-limited or page changed)")
    data = script.text().split("data:", 1)[1].rsplit(",", 1)[0]
    if data.endswith("errorHasStatus: true"):
        return [], None
    payload = json.loads(data)
    out, seen = [], set()
    for bucket in (2, 3):
        try:
            items = payload[bucket][0] or []
        except (IndexError, TypeError):
            continue
        for k in items:
            try:
                fl = k[0]
                price = k[1][0][1] if k[1] and k[1][0] and len(k[1][0]) > 1 else None
                legs = fl[2]
                key = tuple((l[22][0] if len(l) > 22 and l[22] else None, _t(l[8])) for l in legs)
                if key in seen:
                    continue
                seen.add(key)
                out.append({
                    "airline": ", ".join(fl[1]) if isinstance(fl[1], list) else str(fl[1]),
                    "flight_no": " / ".join(f"{l[22][0]}{l[22][1]}" for l in legs if len(l) > 22 and l[22]),
                    "dep": _t(legs[0][8]), "arr": _t(legs[-1][10]),
                    "stops": len(legs) - 1,
                    "duration_min": sum(l[11] or 0 for l in legs),
                    "price_total_inr": price,
                })
            except Exception:
                continue
    return out, _insight(payload)
