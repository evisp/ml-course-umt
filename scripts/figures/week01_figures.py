#!/usr/bin/env python3
"""
Figures for docs/02-data-pipeline/week-01-problem-framing.md

The data lives in the labs repository, not here. This script imports the
same checkpoints module the notebooks use, so the figures always match them.

Run from the repository root, pointing at your copy of ml-course-labs:

    python scripts/figures/week01_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/02-data-pipeline/:
    w01-late-by-month-{light,dark}.png
    w01-late-by-state-{light,dark}.png
    w01-baseline-ladder-{light,dark}.png
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, average_precision_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "02-data-pipeline"

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3f51b5", "warm": "#e07b39", "faint": "#c9cdd6"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#9fa8da", "warm": "#f0a868", "faint": "#4b5160"},
}
NORTH = {"AC", "AM", "AP", "PA", "RO", "RR", "TO"}
RANDOM_STATE = 42
DPI = 200


def save(fig, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=DPI, transparent=True, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def style_axes(ax, c) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["faint"])
    ax.tick_params(colors=c["muted"], labelsize=8)


# --- Data, exactly as the Week 1 solution builds it ---------------------------


def load(labs: Path) -> pd.DataFrame:
    sys.path.insert(0, str(labs))
    from checkpoints import week_01

    df = week_01()

    # The checkpoint is sorted by date; the notebook keeps the file's original
    # order. Restore that order so the same random split gives the same numbers.
    file_order = pd.read_csv(labs / "data" / "raw" / "olist" / "olist_orders_dataset.csv", usecols=["order_id"])
    position = pd.Series(range(len(file_order)), index=file_order["order_id"])
    df = df.assign(_pos=df["order_id"].map(position)).sort_values("_pos").drop(columns="_pos").reset_index(drop=True)

    purchase_day = df["order_purchase_timestamp"].dt.normalize()
    df["window_days"] = (df["order_estimated_delivery_date"] - purchase_day).dt.days
    df["weekday"] = df["order_purchase_timestamp"].dt.dayofweek
    df["hour"] = df["order_purchase_timestamp"].dt.hour
    return df


def ladder(df: pd.DataFrame) -> pd.DataFrame:
    train, test = train_test_split(df, test_size=0.2, stratify=df["is_late"], random_state=RANDOM_STATE)
    y = test["is_late"]
    rows = []

    dummy = DummyClassifier(strategy="most_frequent").fit(train[["window_days"]], train["is_late"])
    rows.append(("Always\non time", accuracy_score(y, dummy.predict(test[["window_days"]])),
                 average_precision_score(y, dummy.predict_proba(test[["window_days"]])[:, 1])))

    state_rate = train.groupby("customer_state")["is_late"].mean()
    average = train["is_late"].mean()
    high_risk = state_rate[state_rate >= 1.5 * average].index
    rule_pred = test["customer_state"].isin(high_risk).astype(int)
    rule_score = test["customer_state"].map(state_rate).fillna(average)
    rows.append(("Rule:\nhigh-risk states", accuracy_score(y, rule_pred), average_precision_score(y, rule_score)))

    features = ["window_days", "weekday", "hour", "state_rate"]

    def add_state_rate(frame):
        return frame.assign(state_rate=frame["customer_state"].map(state_rate).fillna(average))

    tree = DecisionTreeClassifier(max_depth=2, class_weight="balanced", random_state=RANDOM_STATE)
    tree.fit(add_state_rate(train)[features], train["is_late"])
    Xte = add_state_rate(test)[features]
    rows.append(("Depth-2\ntree", accuracy_score(y, tree.predict(Xte)), average_precision_score(y, tree.predict_proba(Xte)[:, 1])))

    def add_leak(frame):
        took = frame["order_delivered_customer_date"] - frame["order_purchase_timestamp"]
        return add_state_rate(frame).assign(days_to_deliver=took.dt.days)

    leaky = features + ["days_to_deliver"]
    lt = DecisionTreeClassifier(max_depth=4, random_state=RANDOM_STATE).fit(add_leak(train)[leaky], train["is_late"])
    Xl = add_leak(test)[leaky]
    rows.append(("Leak: actual\ndelivery days", accuracy_score(y, lt.predict(Xl)), average_precision_score(y, lt.predict_proba(Xl)[:, 1])))

    out = pd.DataFrame(rows, columns=["model", "accuracy", "pr_auc"])
    out.attrs["prevalence"] = y.mean()
    return out


# --- Figure 1: late rate by month --------------------------------------------


def late_by_month(df: pd.DataFrame, theme: str) -> None:
    c = THEMES[theme]
    monthly = df.groupby(df["order_purchase_timestamp"].dt.to_period("M"))["is_late"].mean()
    x = np.arange(len(monthly))

    fig, ax = plt.subplots(figsize=(9.5, 3.6))
    ax.plot(x, monthly.values, color=c["accent"], lw=2.2, marker="o", ms=4.5, zorder=2)
    ax.axhline(df["is_late"].mean(), color=c["faint"], lw=1.2, ls=(0, (4, 3)), zorder=1)
    ax.text(0.2, df["is_late"].mean() + 0.006, "average 6.8%", color=c["muted"], fontsize=8.5)

    labels = {"2017-11": "Nov 2017\nBlack Friday month", "2018-03": "Mar 2018", "2018-06": "Jun 2018"}
    for i, period in enumerate(monthly.index):
        key = str(period)
        if key in labels:
            v = monthly.iloc[i]
            above = key != "2018-06"
            ax.annotate(
                labels[key],
                xy=(i, v),
                xytext=(i, v + (0.025 if above else -0.028)),
                ha="center",
                va="bottom" if above else "top",
                color=c["fg"],
                fontsize=8.5,
            )

    ticks = [i for i, p in enumerate(monthly.index) if p.month in (1, 4, 7, 10)]
    ax.set_xticks(ticks)
    ax.set_xticklabels([monthly.index[i].strftime("%b %Y") for i in ticks])
    ax.set_ylim(-0.055, 0.25)
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylabel("share delivered late", color=c["muted"], fontsize=8)
    style_axes(ax, c)
    save(fig, f"w01-late-by-month-{theme}.png")


# --- Figure 2: late rate by state, with the northern states marked ----------


def late_by_state(df: pd.DataFrame, theme: str) -> None:
    c = THEMES[theme]
    by_state = df.groupby("customer_state")["is_late"].mean().sort_values()
    colours = [c["accent"] if s in NORTH else c["faint"] for s in by_state.index]

    fig, ax = plt.subplots(figsize=(7.0, 6.8))
    ax.barh(by_state.index, by_state.values, color=colours, height=0.7)
    ax.axvline(df["is_late"].mean(), color=c["fg"], lw=1.1, ls=(0, (4, 3)))
    ax.text(df["is_late"].mean() + 0.003, len(by_state) - 0.6, "average", color=c["fg"], fontsize=8.5)

    for state in ("SP", "RJ", "AL"):
        i = list(by_state.index).index(state)
        ax.text(by_state[state] + 0.003, i, f"{by_state[state]:.1%}", va="center", color=c["fg"], fontsize=8)

    ax.xaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_xlabel("share delivered late", color=c["muted"], fontsize=8)
    ax.tick_params(axis="y", labelsize=8, colors=c["fg"])

    handles = [
        plt.Rectangle((0, 0), 1, 1, color=c["accent"]),
        plt.Rectangle((0, 0), 1, 1, color=c["faint"]),
    ]
    leg = ax.legend(handles, ["northern states", "other states"], frameon=False, fontsize=8.5, loc="lower right")
    for t in leg.get_texts():
        t.set_color(c["fg"])
    style_axes(ax, c)
    save(fig, f"w01-late-by-state-{theme}.png")


# --- Figure 3: what accuracy says versus what PR AUC says --------------------


def baseline_ladder(results: pd.DataFrame, theme: str) -> None:
    c = THEMES[theme]
    x = np.arange(len(results))
    colours = [c["faint"], c["accent"], c["accent"], c["warm"]]

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.8))
    panels = [
        ("accuracy", "What accuracy says", "Doing nothing looks almost as good as the leak"),
        ("pr_auc", "What PR AUC says", "Honest rungs barely clear random guessing"),
    ]
    for ax, (col, title, subtitle) in zip(axes, panels):
        vals = results[col].values
        ax.bar(x, vals, color=colours, width=0.62)
        for xi, v in zip(x, vals):
            ax.text(xi, v + 0.02, f"{v:.3f}", ha="center", color=c["fg"], fontsize=8.5)
        if col == "pr_auc":
            p = results.attrs["prevalence"]
            ax.axhline(p, color=c["fg"], lw=1.1, ls=(0, (4, 3)))
            ax.text(0.02, 0.9, f"dashed line: random guessing ({p:.3f})", color=c["muted"], fontsize=8.5,
                    transform=ax.transAxes)
        ax.set_xticks(x)
        ax.set_xticklabels(results["model"], fontsize=8, color=c["fg"])
        ax.set_ylim(0, 1.1)
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)
        ax.set_title(f"{title}\n{subtitle}", color=c["fg"], fontsize=10, pad=8)
        style_axes(ax, c)
        ax.spines["left"].set_visible(False)

    fig.tight_layout(w_pad=3)
    save(fig, f"w01-baseline-ladder-{theme}.png")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"), help="path to your ml-course-labs folder")
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "checkpoints.py").exists():
        print(f"Cannot find checkpoints.py in {labs}. Pass --labs /path/to/ml-course-labs", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    df = load(labs)
    results = ladder(df)
    print(results.round(3).to_string(index=False))

    print("Generating Week 1 figures")
    for theme in THEMES:
        late_by_month(df, theme)
        late_by_state(df, theme)
        baseline_ladder(results, theme)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
