"""Turn collected data into charts + a BUY / WAIT signal (reports/STATUS.md)."""
import datetime as dt, os, sys
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
sys.path.insert(0, os.path.dirname(__file__))
from config import ADULTS, TARGET_ONE_WAY_TOTAL_INR

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = lambda *p: os.path.join(ROOT, *p)
OUT_DATE = "2027-01-07"
RET_DATES = ["2027-01-14", "2027-01-21"]          # 1 week / 2 weeks
BLUE, ORANGE, INK, INK2, GRID, SURF = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
BUY_BY_DAYS = 30   # fallback deadline; refined from the booking curve below


def style(ax, title):
    ax.set_facecolor(SURF)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=10)
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"₹{v:,.0f}"))


def history_chart(hist, typ):
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.2), facecolor=SURF, sharey=True)
    panels = [("DEL", "SXR", [OUT_DATE], "Delhi → Srinagar, departing 7 Jan"),
              ("SXR", "DEL", RET_DATES[:1], "Srinagar → Delhi, returning 14 Jan (21 Jan moved identically)")]
    for ax, (o, d, dates, title) in zip(axes, panels):
        style(ax, title)
        t = typ[(typ.origin == o) & (typ.dest == d)]
        if len(t):
            r = t.iloc[-1]
            ax.axhspan(r.typical_low_pp_inr, r.typical_high_pp_inr, color="#d9d8d3", alpha=0.5, lw=0)
            ax.text(0.01, r.typical_high_pp_inr, " Google's typical range", transform=ax.get_yaxis_transform(),
                    va="bottom", fontsize=8, color=INK2)
        for col, td in zip((BLUE, ORANGE), dates):
            h = hist[(hist.origin == o) & (hist.dest == d) & (hist.travel_date == td)].sort_values("observed_on")
            if h.empty:
                continue
            x = pd.to_datetime(h.observed_on)
            ax.step(x, h.lowest_fare_pp_inr, where="post", color=col, lw=2, label=td)
            ax.plot(x.iloc[-1], h.lowest_fare_pp_inr.iloc[-1], "o", color=col, ms=6, mec=SURF, mew=2)
            ax.annotate(f"₹{h.lowest_fare_pp_inr.iloc[-1]:,} now", (x.iloc[-1], h.lowest_fare_pp_inr.iloc[-1]),
                        xytext=(6, 6 if col == BLUE else -12), textcoords="offset points", fontsize=8, color=INK)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
        if len(dates) > 1:
            ax.legend(frameon=False, fontsize=8, labelcolor=INK2, loc="upper right")
    axes[0].set_ylabel("Cheapest one-way fare, per person", color=INK2, fontsize=9)
    fig.suptitle("How the cheapest fare for your dates has moved (Google Flights price history)",
                 x=0.01, ha="left", fontsize=12, color=INK)
    fig.tight_layout()
    fig.savefig(D("reports", "price_history.png"), dpi=150)
    plt.close(fig)


def booking_curve(curve):
    """Median fare at N days before departure, relative to the same flight-date's fare ~45-60 days out."""
    if curve is None or curve.empty:
        return None, None
    base = (curve[curve.days_before.between(45, 60)].groupby(["origin", "dest", "travel_date"])
            .lowest_fare_pp_inr.median().rename("base"))
    c = curve.join(base, on=["origin", "dest", "travel_date"]).dropna(subset=["base"])
    c["ratio"] = c.lowest_fare_pp_inr / c.base
    c["bucket"] = (c.days_before // 5) * 5
    agg = c.groupby(["origin", "dest", "bucket"]).ratio.agg(["median", lambda s: s.quantile(.25),
                                                              lambda s: s.quantile(.75), "count"])
    agg.columns = ["median", "q25", "q75", "n"]
    agg = agg.reset_index()
    fig, ax = plt.subplots(figsize=(9, 4.2), facecolor=SURF)
    style(ax, "Fares as departure approaches, DEL⇄SXR flights departing Nov–Dec 2026")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{(v - 1) * 100:+.0f}%"))
    for col, (o, d) in zip((BLUE, ORANGE), (("DEL", "SXR"), ("SXR", "DEL"))):
        a = agg[(agg.origin == o) & (agg.dest == d) & (agg.n >= 3)].sort_values("bucket")
        if a.empty:
            continue
        ax.fill_between(a.bucket, a.q25, a.q75, color=col, alpha=0.12, lw=0)
        ax.plot(a.bucket, a["median"], color=col, lw=2, label=f"{o} → {d}")
        ax.annotate(f"{o}→{d}", (a.bucket.iloc[0], a["median"].iloc[0]), xytext=(-4, 0),
                    textcoords="offset points", ha="right", fontsize=8, color=INK)
    ax.axhline(1, color=INK2, lw=0.8)
    ax.invert_xaxis()
    ax.set_xlabel("Days before departure", color=INK2, fontsize=9)
    ax.set_ylabel("vs fare 45–60 days out (median, band = middle 50%)", color=INK2, fontsize=9)
    ax.legend(frameon=False, fontsize=8, labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(D("reports", "booking_curve.png"), dpi=150)
    plt.close(fig)
    # deadline: the latest bucket from which the median stays above +10% all the way to departure
    deadline = None
    m = agg.groupby("bucket")["median"].max().sort_index()
    for b in sorted(m.index):
        if m[b] >= 1.10:
            deadline = b + 5
        else:
            break
    return agg, deadline


def main():
    hist = pd.read_csv(D("data", "google_price_history.csv"))
    typ = pd.read_csv(D("data", "google_typical_range.csv"))
    cp = D("data", "booking_curve_samples.csv")
    curve = pd.read_csv(cp) if os.path.exists(cp) else None
    history_chart(hist, typ)
    agg, deadline = booking_curve(curve)
    buy_by = deadline or BUY_BY_DAYS
    today = dt.date.today()
    lines = [f"# Fare status, {today:%d %b %Y}", "",
             f"Trip: DEL→SXR on {OUT_DATE}, return SXR→DEL on {' or '.join(RET_DATES)}, {ADULTS} adults.", ""]
    lines += ["| Leg | Travel date | Days out | Cheapest now (per person) | Google typical | Lowest seen in last 60 days | Signal |",
              "|---|---|---|---|---|---|---|"]
    for o, d, td in [("DEL", "SXR", OUT_DATE)] + [("SXR", "DEL", r) for r in RET_DATES]:
        h = hist[(hist.origin == o) & (hist.dest == d) & (hist.travel_date == td)].sort_values("observed_on")
        t = typ[(typ.origin == o) & (typ.dest == d) & (typ.travel_date == td)].sort_values("checked_on")
        if h.empty or t.empty:
            continue
        now = int(t.current_low_pp_inr.iloc[-1]); lo, hi = int(t.typical_low_pp_inr.iloc[-1]), int(t.typical_high_pp_inr.iloc[-1])
        seen = int(h.lowest_fare_pp_inr.min())
        days = (dt.date.fromisoformat(td) - today).days
        if now <= hi or now * ADULTS <= TARGET_ONE_WAY_TOTAL_INR:
            sig = "**BUY** (at/below typical or target)"
        elif days <= buy_by:
            sig = f"**BUY** (inside the last {buy_by} days, fares tend to rise)"
        elif now <= seen * 1.03:
            sig = "**BUY** (at the 60-day low)"
        else:
            sig = f"WAIT (book by {dt.date.fromisoformat(td) - dt.timedelta(days=buy_by):%d %b} at the latest)"
        lines.append(f"| {o}→{d} | {td} | {days} | ₹{now:,} | ₹{lo:,}–{hi:,} | ₹{seen:,} | {sig} |")
    lines += ["", f"Latest safe booking point from the booking curve: **{buy_by} days before departure**"
              + ("" if deadline else " (default; not enough curve data yet)") + ".", "",
              "![price history](price_history.png)", ""] + (["![booking curve](booking_curve.png)", ""] if agg is not None else [])
    snap = D("data", "snapshots.csv")
    if os.path.exists(snap):
        s = pd.read_csv(snap)
        s = s[s.checked_at_ist == s.checked_at_ist.max()]
        lines += ["## Cheapest flights in the latest snapshot (total for 2)", "",
                  "| Date | Route | Flight | Dep–Arr | Stops | Total ₹ |", "|---|---|---|---|---|---|"]
        for (o, d), g in s.groupby(["origin", "dest"]):
            for _, r in g.sort_values("price_total_inr").head(8).iterrows():
                lines.append(f"| {r.travel_date} | {o}→{d} | {r.airline} {r.flight_no} | {r.dep}–{r.arr} | {r.stops} | {r.price_total_inr:,} |")
    open(D("reports", "STATUS.md"), "w").write("\n".join(lines) + "\n")
    if agg is not None:
        agg.to_csv(D("reports", "booking_curve_summary.csv"), index=False)
    print("\n".join(lines[:12]))


if __name__ == "__main__":
    main()
