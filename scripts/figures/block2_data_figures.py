#!/usr/bin/env python3
"""
Figures for docs/03-models-optimization/dataset.md

Everything is computed through hotels.py, so the page, the data notebook and
every Block 2 lab agree on the same numbers.

    python scripts/figures/block2_data_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/03-models-optimization/, light and dark versions of:
    b2d-over-time     cancellation rate by booking month, with the split boundaries
    b2d-adr           the nightly rate, as recorded and inside a sane range
    b2d-leadtime      how far ahead a booking is made, against how often it is cancelled
    b2d-segments      cancellation rate by deposit type and by market segment
    b2d-cardinality   how much of the data the commonest categories cover
    b2d-splits        the three periods, their size and their cancellation rate
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "03-models-optimization"
DPI = 200

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3d5a80", "warm": "#c05d3e",
              "faint": "#cfc6b7", "soft": "#e8eaf6"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#8fb0d4", "warm": "#e0855f",
             "faint": "#4b5160", "soft": "#2a2f3c"},
}


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=DPI, transparent=True, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def style(ax, c):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["faint"])
    ax.tick_params(colors=c["muted"], labelsize=8)


def legend(ax, c, **kw):
    leg = ax.legend(frameon=False, fontsize=8.5, **kw)
    for t in leg.get_texts():
        t.set_color(c["fg"])


def pct(ax, axis="y"):
    getattr(ax, f"{axis}axis").set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"{v:.0%}"))


# ---------------------------------------------------------------------------


def compute(hotels):
    raw = hotels.load_bookings()
    clean, log = hotels.clean_bookings(raw, log=True)
    df = hotels.split_by_booking_date(clean)

    monthly = (df.set_index("booking_date")
                 .resample("ME")["is_canceled"].agg(["mean", "size"])
                 .rename(columns={"mean": "rate", "size": "n"}))
    monthly = monthly[monthly["n"] >= 100]

    buckets = pd.cut(df["lead_time"], [-1, 7, 30, 90, 180, 365, 10_000],
                     labels=["0-7", "8-30", "31-90", "91-180", "181-365", "365+"])
    lead = df.groupby(buckets, observed=True)["is_canceled"].agg(["mean", "size"])

    deposit = df.groupby("deposit_type")["is_canceled"].agg(["mean", "size"]).sort_values("mean")
    segment = (df.groupby("market_segment")["is_canceled"].agg(["mean", "size"])
                 .query("size >= 200").sort_values("mean"))

    cardinality = {}
    for column in ("country", "agent", "company"):
        counts = df[column].value_counts(normalize=True)
        cardinality[column] = (counts.cumsum().to_numpy(), int(df[column].nunique()))

    splits = (df.groupby("split", observed=True)
                .agg(n=("is_canceled", "size"), rate=("is_canceled", "mean"),
                     start=("booking_date", "min"), end=("booking_date", "max"))
                .reindex(["train", "valid", "test"]))

    return {"raw": raw, "df": df, "log": log, "monthly": monthly, "lead": lead,
            "deposit": deposit, "segment": segment, "cardinality": cardinality,
            "splits": splits, "adr": df["adr"], "range": hotels.ADR_RANGE,
            "dates": hotels.SPLIT_DATES}


# ---------------------------------------------------------------------------


def over_time(r, theme):
    c = THEMES[theme]
    m = r["monthly"]
    fig, ax = plt.subplots(figsize=(8.4, 3.4))
    ax.plot(m.index, m["rate"], color=c["accent"], lw=2)
    ax.fill_between(m.index, 0, m["rate"], color=c["accent"], alpha=0.10)
    # Before the first arrival in the file, only very-long-lead bookings can
    # exist, and those cancel far more often. Left-censoring, not a trend.
    first_arrival = r["df"]["arrival_date"].min()
    ax.axvspan(m.index.min(), first_arrival, color=c["faint"], alpha=0.25, lw=0)
    ax.text(m.index.min(), 1.02, " long-lead bookings only", fontsize=8,
            color=c["muted"], va="bottom")

    for d in r["dates"]:
        ax.axvline(pd.Timestamp(d), color=c["warm"], ls=(0, (4, 3)), lw=1.3)
    for d, label, dy in zip(r["dates"], ("validation", "test"), (1.02, 0.90)):
        ax.text(pd.Timestamp(d), dy, f" {label}", fontsize=8, color=c["warm"],
                va="bottom")
    ax.set_ylim(0, 1.16)
    ax.set_ylabel("cancelled", fontsize=9, color=c["muted"])
    ax.set_xlabel("month the booking was made", fontsize=9, color=c["muted"])
    pct(ax)
    style(ax, c)
    save(fig, f"b2d-over-time-{theme}.png")


def adr_shape(r, theme):
    c = THEMES[theme]
    adr, (lo, hi) = r["adr"], r["range"]
    fig, axes = plt.subplots(1, 2, figsize=(8.4, 3.0))

    ax = axes[0]
    ax.hist(adr, bins=120, color=c["faint"])
    ax.set_yscale("log")
    ax.set_title("as recorded", fontsize=9.5, color=c["fg"])
    ax.set_xlabel(f"euros per night   (min {adr.min():.2f}, max {adr.max():.0f})",
                  fontsize=8.5, color=c["muted"])
    ax.set_ylabel("bookings, log scale", fontsize=8.5, color=c["muted"])
    style(ax, c)

    ax = axes[1]
    inside = adr[adr.between(lo, hi)]
    ax.hist(inside, bins=80, color=c["accent"])
    ax.axvline(inside.mean(), color=c["warm"], ls=(0, (4, 3)), lw=1.3)
    ax.text(inside.mean(), ax.get_ylim()[1] * 0.92, f"  mean {inside.mean():.0f}",
            fontsize=8.5, color=c["warm"])
    outside = int((~adr.between(lo, hi)).sum())
    ax.set_title(f"inside {lo:.0f} to {hi:.0f}   ({outside:,} left out)",
                 fontsize=9.5, color=c["fg"])
    ax.set_xlabel("euros per night", fontsize=8.5, color=c["muted"])
    style(ax, c)

    fig.tight_layout()
    save(fig, f"b2d-adr-{theme}.png")


def leadtime(r, theme):
    c = THEMES[theme]
    lead = r["lead"]
    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    bars = ax.bar(range(len(lead)), lead["mean"], color=c["accent"], width=0.6)
    for i, (rate, n) in enumerate(zip(lead["mean"], lead["size"])):
        ax.text(i, rate + 0.015, f"{rate:.0%}", ha="center", fontsize=9,
                weight="bold", color=c["fg"])
        ax.text(i, 0.02, f"{n:,}", ha="center", fontsize=7.5, color=c["soft"])
    ax.set_xticks(range(len(lead)))
    ax.set_xticklabels(lead.index, fontsize=9, color=c["fg"])
    ax.set_xlabel("days between booking and arrival", fontsize=9, color=c["muted"])
    ax.set_ylabel("cancelled", fontsize=9, color=c["muted"])
    ax.set_ylim(0, lead["mean"].max() * 1.22)
    pct(ax)
    style(ax, c)
    save(fig, f"b2d-leadtime-{theme}.png")


def segments(r, theme):
    c = THEMES[theme]
    fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.2),
                             gridspec_kw={"width_ratios": [1, 1.4]})
    for ax, (table, title) in zip(axes, ((r["deposit"], "by deposit type"),
                                         (r["segment"], "by market segment"))):
        colours = [c["warm"] if v > 0.8 else c["accent"] for v in table["mean"]]
        ax.barh(range(len(table)), table["mean"], color=colours, height=0.6)
        for i, (rate, n) in enumerate(zip(table["mean"], table["size"])):
            ax.text(rate + 0.015, i, f"{rate:.0%}  ({n:,})", va="center",
                    fontsize=8, color=c["fg"])
        ax.set_yticks(range(len(table)))
        ax.set_yticklabels(table.index, fontsize=9, color=c["fg"])
        ax.set_xlim(0, 1.25)
        ax.set_title(title, fontsize=9.5, color=c["fg"], loc="left")
        pct(ax, "x")
        style(ax, c)
    fig.tight_layout()
    save(fig, f"b2d-segments-{theme}.png")


def cardinality(r, theme):
    c = THEMES[theme]
    fig, ax = plt.subplots(figsize=(8.4, 3.2))
    colours = {"country": c["accent"], "agent": c["warm"], "company": c["muted"]}
    for name, (cum, total) in r["cardinality"].items():
        ax.plot(range(1, len(cum) + 1), cum, color=colours[name], lw=2,
                label=f"{name}  ({total} values)")
    ax.axhline(0.95, color=c["faint"], ls=(0, (4, 3)), lw=1)
    ax.text(len(max(r["cardinality"].values(), key=lambda v: len(v[0]))[0]), 0.955,
            "95% ", fontsize=8, color=c["muted"], ha="right")
    ax.set_xscale("log")
    ax.set_xlabel("number of categories kept, commonest first", fontsize=9, color=c["muted"])
    ax.set_ylabel("share of bookings covered", fontsize=9, color=c["muted"])
    ax.set_ylim(0, 1.03)
    pct(ax)
    style(ax, c)
    legend(ax, c, loc="lower right")
    save(fig, f"b2d-cardinality-{theme}.png")


def splits_figure(r, theme):
    c = THEMES[theme]
    s = r["splits"]
    fig, ax = plt.subplots(figsize=(8.4, 2.6))
    colours = [c["accent"], c["muted"], c["warm"]]
    for i, (name, row) in enumerate(s.iterrows()):
        start, end = row["start"], row["end"]
        ax.barh(0, (end - start).days, left=start, height=0.5, color=colours[i],
                alpha=0.85)
        mid = start + (end - start) / 2
        ax.text(mid, 0, f"{name}\n{row['n']:,}  ·  {row['rate']:.1%} cancelled",
                ha="center", va="center", fontsize=8.5, color="#ffffff", weight="bold")
    ax.set_yticks([])
    ax.set_xlabel("when the booking was made", fontsize=9, color=c["muted"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(c["faint"])
    ax.tick_params(colors=c["muted"], labelsize=8)
    save(fig, f"b2d-splits-{theme}.png")


# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"))
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "hotels.py").exists():
        print(f"Cannot find hotels.py in {labs}. Pass --labs /path/to/ml-course-labs",
              file=sys.stderr)
        return 1
    sys.path.insert(0, str(labs))
    import hotels

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    r = compute(hotels)

    print(f"  rows after cleaning: {len(r['df']):,}")
    print(r["log"].to_string())
    print(f"  cancelled overall:   {r['df']['is_canceled'].mean():.1%}")
    print(r["splits"][["n", "rate"]].to_string())
    print(f"  deposit type:\n{r['deposit'].to_string()}")
    print(f"  lead time:\n{r['lead'].to_string()}")
    for name, (cum, total) in r["cardinality"].items():
        at95 = int(np.searchsorted(cum, 0.95) + 1)
        print(f"  {name}: {total} values, {at95} cover 95%")

    for theme in ("light", "dark"):
        over_time(r, theme)
        adr_shape(r, theme)
        leadtime(r, theme)
        segments(r, theme)
        cardinality(r, theme)
        splits_figure(r, theme)
    return 0


if __name__ == "__main__":
    sys.exit(main())
