# Flight_Track: Delhi ⇄ Srinagar fares for a January 2027 trip

**Trip:** 2 adults, DEL→SXR on **Thu 7 Jan 2027**, return SXR→DEL 1–2 weeks later (13–22 Jan).
**Analysis date:** 1 Nov 2026 (67 days before departure).

## Interactive demo

`public/index.html` is a self-contained page. All the data is baked in, so there's no backend and no API keys. With it you can:
- change the number of travellers and see the totals update
- switch to nonstop flights only
- click any departure/return pair on a heat-map of round-trip prices
- hover the 60-day price history for each leg
- set your own price target and get a book-now / wait signal per leg

**Deploy to Vercel**
1. Go to [vercel.com/new](https://vercel.com/new) and import `rizvonium/flight_track`.
2. Leave every setting as it is. `vercel.json` already tells Vercel to serve `public/` with no build step.
3. Deploy. Vercel builds from the default branch, so either merge `claude/dazzling-hopper-2dysdy` first or pick that branch under *Settings → Git*.

Or from a terminal: `npx vercel --prod` in the repo root.

**After collecting new data**, rebuild the page with `python tracker/build_web.py` and push. Vercel redeploys automatically.

## Bottom line

| Leg | What to do | Why |
|---|---|---|
| **Return SXR→DEL, 13 or 14 Jan** | **Book now.** IndiGo nonstop 6E527 (10:45) or 6E963 (20:15): **₹14,647 for 2** (₹7,324 each) | Fell from about ₹9,100 to ₹6,829 per person on 22 Oct. That's the lowest in 60 days and inside Google's typical range. Return fares out of Srinagar are the ones that spike in winter (snow closures, highway shutdowns), so lock this leg in. |
| **Outbound DEL→SXR, 7 Jan** | **Watch it, but book by about 8 Dec** (30 days out). Buy straight away if the cheapest fare drops back to about ₹6,150 per person or below. | It fell from ₹8,594 to ₹6,147 per person in Sept–Oct and has just ticked up to ₹6,512, still above Google's typical ₹4,000–5,200. There's a small chance it gets cheaper and a real risk it rises after early December. |

**Budget today (2 people, round trip):**
- Cheapest any-stop: ~₹26,700 (SpiceJet SG160 via Jammu, ₹13,024 out + IndiGo via Jammu, ₹13,658 back)
- Cheapest nonstop both ways: **~₹30,500** (SpiceJet SG904/SG199 or IndiGo 6E912, ₹15,830 out + IndiGo 6E527/6E963, ₹14,647 back on 13/14 Jan)

Returning on **13 or 14 Jan is ~₹2,800 cheaper for 2** than 15–24 Jan (nonstop ₹14,647 vs ₹17,411).
Leaving on **12 Jan** instead of 7 Jan would save ~₹2,200 on the nonstop (₹13,654 vs ₹15,830).

## What the data covers, and what it doesn't

You asked for 5 years of history. **No free public dataset of historical DEL⇄SXR fares exists.** Airlines and OTAs
don't publish past fares, and DGCA only publishes traffic, not prices. Here is what this repo has:

| File | What it is |
|---|---|
| `data/fare_grid_2026-11-01.csv` | Every priced flight, both directions, for each day 3–24 Jan, as seen on Google Flights today (370 rows, 2 adults) |
| `data/google_price_history.csv` | Google Flights' own ~60-day history of the cheapest fare for **each of your travel dates** (Sept 3 → Nov 1) |
| `data/google_typical_range.csv` | What Google calls a "typical" cheapest fare for those dates, based on fares it has seen over the past year |
| `data/historical_context.csv` | Fare spikes on this route reported in news coverage, 2020–2025, with sources |
| `reports/STATUS.md`, `reports/price_history.png` | Generated summary + chart |

### What multi-year history tells us about this route
- **Cheapest month:** Google's 12-month data says November. **Most expensive:** October. January is mid-range, not peak.
- **Spikes are event-driven, not seasonal drift.** Snowfall closing Srinagar airport or the Jammu–Srinagar highway has
  repeatedly pushed SXR→DEL from ₹3.5–5k to ₹10–15k within days. The same happened at Eid (June 2024, up to ₹16k),
  with the highway closure (Sept 2025, ₹13–15k), and after the Pahalgam attack (Apr 2025, up to ₹65k). A ticket
  you have **already booked** protects you from all of these. That's the main argument for booking the return early.
- **Booking window:** Indian domestic fares are usually lowest about **3–6 weeks before departure** and rise sharply in
  the last 2–3 weeks (MakeMyTrip, ixigo, HappyFares guides). For Jan 7 that window is roughly **26 Nov – 17 Dec**, so
  "book by 8 Dec" stays on the safe side.

## Re-running

```bash
pip install -r requirements.txt
python tracker/analyze.py          # rebuild reports/ from data/
```

`tracker/track.py` and `tracker/history.py` fetch fresh data from Google Flights through the
[`fast-flights`](https://github.com/AWeirdDev/fast-flights) scraper. They aren't scheduled. Automated scraping may
break Google's terms, so the simplest way to follow prices day to day is Google Flights' own
**Track prices** toggle for DEL→SXR on 7 Jan and SXR→DEL on 13/14 Jan. It emails you when the fare moves.
Edit `tracker/config.py` to change dates or passenger count.

## Practical tips
- Before paying, compare the same flight on the airline's own site against the OTAs. OTA coupons often take ₹300–800 off.
- Pick a fare type that lets you change the date cheaply. January snow cancellations happen, and if the airline
  cancels, you get a free rebooking or a refund.
- If you leave on 7 Jan, a morning departure gives you the most room to rebook the same day if fog or snow causes delays.
