#!/usr/bin/env python3
"""
Figures for docs/02-data-pipeline/week-02-data-quality.md

Imports week_02() from the labs repository, so every figure matches the notebooks.

    python scripts/figures/week02_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/02-data-pipeline/, light and dark versions of:
    w02-flow-map       every order as a line from seller to customer (the showpiece)
    w02-split          the monthly late rate, with train, validation and test shaded
    w02-brazil         the late rate across Brazil, from the training period
    w02-promised       promised versus actual delivery time
    w02-same-state     late rate for orders within one state versus across states
    w02-lift           Week 1's baselines judged on a random split and on time
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.collections import LineCollection
from matplotlib.colors import LinearSegmentedColormap, LogNorm
from matplotlib.ticker import PercentFormatter
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "02-data-pipeline"
RANDOM_STATE = 42
DPI = 200

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3f51b5", "warm": "#e07b39",
              "green": "#2e7d32", "faint": "#c9cdd6", "dots": "#8a90a0", "line": "#3f51b5",
              "cmap_seq": "Blues", "cmap_rate": "magma_r"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#9fa8da", "warm": "#f0a868",
             "green": "#81c784", "faint": "#4b5160", "dots": "#6b7280", "line": "#9fa8da",
             "cmap_seq": "Blues_r",
             "cmap_rate": LinearSegmentedColormap.from_list("inferno_lit", plt.cm.inferno(np.linspace(0.25, 1, 256)))},
}


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=DPI, transparent=True, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def style_axes(ax, c):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["faint"])
    ax.tick_params(colors=c["muted"], labelsize=8)


# --- Figure 1: the flow map -----------------------------------------------------


def flow_map(df, theme):
    c = THEMES[theme]
    train = df[df["split"] == "train"].dropna(subset=["customer_lat", "customer_lng", "seller_lat", "seller_lng"])
    sample = train.sample(12000, random_state=RANDOM_STATE)

    segments = np.stack([
        sample[["seller_lng", "seller_lat"]].to_numpy(),
        sample[["customer_lng", "customer_lat"]].to_numpy(),
    ], axis=1)

    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(train["customer_lng"], train["customer_lat"], s=2, color=c["dots"], alpha=0.15, linewidths=0, zorder=1)
    ax.add_collection(LineCollection(segments, colors=c["line"], linewidths=0.35, alpha=0.06, zorder=2))
    sellers = sample.drop_duplicates("seller_id")
    ax.scatter(sellers["seller_lng"], sellers["seller_lat"], s=5, color=c["warm"], alpha=0.8, linewidths=0, zorder=3)

    ax.set_xlim(-74, -34)
    ax.set_ylim(-34, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.text(-73, 4.5, "Every order is a journey", color=c["fg"], fontsize=13, weight="bold")
    ax.text(-73, 2.6, "12,000 orders, each a line from seller to customer.\nOrange dots are sellers.",
            color=c["muted"], fontsize=9, va="top")
    save(fig, f"w02-flow-map-{theme}.png")


# --- Figure 2: the split on the monthly late rate -------------------------------


def split_chart(df, theme):
    c = THEMES[theme]
    monthly = df.groupby(df["order_purchase_timestamp"].dt.to_period("M"))["is_late"].mean()
    periods = monthly.index
    parts = {
        "train": ("2017-01", "2018-02", c["accent"]),
        "validation": ("2018-03", "2018-04", c["warm"]),
        "test": ("2018-05", "2018-08", c["green"]),
    }
    rates = df.groupby("split")["is_late"].mean()

    fig, ax = plt.subplots(figsize=(10, 3.8))
    for (label, (start, end, colour)), key in zip(parts.items(), ["train", "valid", "test"]):
        a, b = periods.get_loc(pd.Period(start)), periods.get_loc(pd.Period(end))
        ax.axvspan(a - 0.5, b + 0.5, color=colour, alpha=0.1, lw=0)
        ax.text((a + b) / 2, 0.215, f"{label}\n{rates[key]:.1%} late", ha="center", va="top",
                color=colour, fontsize=9, weight="bold")

    ax.plot(range(len(monthly)), monthly.values, color=c["fg"], marker="o", ms=4, lw=1.8)
    ticks = [i for i, p in enumerate(periods) if p.month in (1, 4, 7, 10)]
    ax.set_xticks(ticks)
    ax.set_xticklabels([periods[i].strftime("%b %Y") for i in ticks])
    ax.set_ylim(0, 0.22)
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylabel("share delivered late", color=c["muted"], fontsize=8)
    style_axes(ax, c)
    save(fig, f"w02-split-{theme}.png")


# --- Figure 3: late rate across Brazil ------------------------------------------


def brazil(df, theme):
    c = THEMES[theme]
    train = df[df["split"] == "train"].dropna(subset=["customer_lat", "customer_lng"])

    fig, ax = plt.subplots(figsize=(7.5, 7.5))
    ax.scatter(train["customer_lng"], train["customer_lat"], s=3, color=c["dots"], alpha=0.18, linewidths=0, zorder=1)
    cells = ax.hexbin(train["customer_lng"], train["customer_lat"], C=train["is_late"],
                      reduce_C_function=np.mean, gridsize=60, mincnt=15, cmap=c["cmap_rate"],
                      vmin=0, vmax=0.2, linewidths=0.2, edgecolors="none", zorder=2)
    bar = fig.colorbar(cells, ax=ax, shrink=0.45, format=PercentFormatter(1, decimals=0))
    bar.set_label("share delivered late", color=c["muted"], fontsize=8)
    bar.ax.tick_params(colors=c["muted"], labelsize=8)
    bar.outline.set_visible(False)
    ax.set_xlim(-74, -34)
    ax.set_ylim(-34, 6)
    ax.set_aspect("equal")
    ax.axis("off")
    save(fig, f"w02-brazil-{theme}.png")


# --- Figure 4: promised versus actual -------------------------------------------


def promised(df, theme):
    c = THEMES[theme]
    train = df[df["split"] == "train"]
    day = train["order_purchase_timestamp"].dt.normalize()
    prom = (train["order_estimated_delivery_date"] - day).dt.days
    act = (train["order_delivered_customer_date"].dt.normalize() - day).dt.days

    bins = np.arange(0, 61) - 0.5
    fig, ax = plt.subplots(figsize=(7, 5.6))
    *_, image = ax.hist2d(prom, act, bins=[bins, bins], cmap=c["cmap_seq"],
                          norm=LogNorm(), cmin=1)
    bar = fig.colorbar(image, ax=ax, shrink=0.7)
    bar.set_label("orders", color=c["muted"], fontsize=8)
    bar.ax.tick_params(colors=c["muted"], labelsize=8)
    bar.outline.set_visible(False)
    ax.plot([0, 60], [0, 60], color=c["warm"], lw=2)
    ax.text(44, 49, "on the promised day", color=c["warm"], rotation=38, fontsize=9)
    ax.text(34, 3, "early", color=c["fg"], fontsize=11)
    ax.text(3, 50, "late", color=c["warm"], fontsize=11)
    ax.set_xlabel("days promised", color=c["muted"], fontsize=9)
    ax.set_ylabel("days it actually took", color=c["muted"], fontsize=9)
    style_axes(ax, c)
    save(fig, f"w02-promised-{theme}.png")


# --- Figure 5: same state or not ------------------------------------------------


def same_state(df, theme):
    c = THEMES[theme]
    train = df[df["split"] == "train"]
    same = train["customer_state"] == train["seller_state"]
    by = train.groupby(same)["is_late"].agg(["mean", "size"])
    labels = ["across states", "within one state"]
    values = [by.loc[False, "mean"], by.loc[True, "mean"]]
    counts = [by.loc[False, "size"], by.loc[True, "size"]]

    fig, ax = plt.subplots(figsize=(5.4, 3.8))
    ax.bar(labels, values, color=[c["warm"], c["accent"]], width=0.55)
    for i, (v, n) in enumerate(zip(values, counts)):
        ax.text(i, v + 0.003, f"{v:.1%}", ha="center", color=c["fg"], fontsize=11, weight="bold")
        ax.text(i, v / 2, f"{n:,}\norders", ha="center", va="center", color="white", fontsize=8)
    ax.set_ylim(0, 0.1)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    ax.tick_params(axis="x", colors=c["fg"], labelsize=9)
    style_axes(ax, c)
    ax.spines["left"].set_visible(False)
    save(fig, f"w02-same-state-{theme}.png")


# --- Figure 6: lift, random versus time ------------------------------------------


def ladder(train_part, test_part):
    y = test_part["is_late"]
    rate = train_part.groupby("customer_state")["is_late"].mean()
    average = train_part["is_late"].mean()

    def features(frame):
        frame = frame.assign(state_rate=frame["customer_state"].map(rate).fillna(average))
        frame["window_days"] = (frame["order_estimated_delivery_date"] - frame["order_purchase_timestamp"].dt.normalize()).dt.days
        frame["weekday"] = frame["order_purchase_timestamp"].dt.dayofweek
        frame["hour"] = frame["order_purchase_timestamp"].dt.hour
        return frame[["window_days", "weekday", "hour", "state_rate"]]

    tree = DecisionTreeClassifier(max_depth=2, class_weight="balanced", random_state=RANDOM_STATE)
    tree.fit(features(train_part), train_part["is_late"])
    rule = average_precision_score(y, test_part["customer_state"].map(rate).fillna(average))
    tr = average_precision_score(y, tree.predict_proba(features(test_part))[:, 1])
    return pd.Series({"rule": rule / y.mean(), "tree": tr / y.mean()})


def lift(df, theme):
    c = THEMES[theme]
    rtrain, rtest = train_test_split(df, test_size=0.2, stratify=df["is_late"], random_state=RANDOM_STATE)
    past, valid, future = (df[df["split"] == s] for s in ["train", "valid", "test"])
    res = pd.DataFrame({
        "random split": ladder(rtrain, rtest),
        "time: validation": ladder(past, valid),
        "time: test": ladder(past, future),
    }).T
    print(res.round(2).to_string())

    x = np.arange(len(res))
    w = 0.34
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    ax.bar(x - w / 2, res["rule"], width=w, color=c["faint"], label="rule")
    ax.bar(x + w / 2, res["tree"], width=w, color=c["accent"], label="depth-2 tree")
    for xi, (r, t) in enumerate(zip(res["rule"], res["tree"])):
        ax.text(xi - w / 2, r + 0.03, f"{r:.2f}", ha="center", color=c["fg"], fontsize=8.5)
        ax.text(xi + w / 2, t + 0.03, f"{t:.2f}", ha="center", color=c["fg"], fontsize=8.5)
    ax.axhline(1, color=c["fg"], lw=1.1, ls=(0, (4, 3)), label="no better than guessing")
    ax.set_xticks(x)
    ax.set_xticklabels(res.index, color=c["fg"], fontsize=9)
    ax.set_ylim(0, 2)
    ax.set_ylabel("lift over guessing", color=c["muted"], fontsize=8)
    leg = ax.legend(frameon=False, fontsize=8.5, loc="upper right")
    for t in leg.get_texts():
        t.set_color(c["fg"])
    style_axes(ax, c)
    save(fig, f"w02-lift-{theme}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"), help="path to your ml-course-labs folder")
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "checkpoints.py").exists():
        print(f"Cannot find checkpoints.py in {labs}. Pass --labs /path/to/ml-course-labs", file=sys.stderr)
        return 1
    sys.path.insert(0, str(labs))
    from checkpoints import week_02

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    df = week_02()
    print("Generating Week 2 figures")
    for theme in THEMES:
        flow_map(df, theme)
        split_chart(df, theme)
        brazil(df, theme)
        promised(df, theme)
        same_state(df, theme)
        lift(df, theme)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
