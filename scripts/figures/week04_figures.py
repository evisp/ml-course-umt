#!/usr/bin/env python3
"""
Figures for docs/02-data-pipeline/week-04-evaluation.md

Imports week_03() and week_03_pipeline() from the labs repository, so every
number matches the Week 4 notebooks.

    python scripts/figures/week04_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/02-data-pipeline/, light and dark versions of:
    w04-threshold     precision, recall and share flagged at every threshold
    w04-cost          the cost of mistakes at every threshold
    w04-reliability   average score against the share actually late
    w04-slices        recall by slice, against the overall recall
    w04-profile       the late orders the model missed, against the ones it caught
    w04-bootstrap     bootstrap distributions of test lift, model against Week 1's rule
    w04-decision      the same decision's cost on validation and on test
    w04-months        precision of the flags month by month, against break-even
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
from sklearn.metrics import average_precision_score, precision_score, recall_score

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "02-data-pipeline"
RANDOM_STATE = 42
DPI = 200
MISS_COST, ALARM_COST = 10, 1

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3f51b5", "warm": "#e07b39",
              "faint": "#c9cdd6", "green": "#2e7d32"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#9fa8da", "warm": "#f0a868",
             "faint": "#4b5160", "green": "#81c784"},
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


def legend(ax, c, **kw):
    leg = ax.legend(frameon=False, fontsize=8.5, **kw)
    for t in leg.get_texts():
        t.set_color(c["fg"])


def lift(y, s):
    return average_precision_score(y, s) / np.mean(y)


def cost_per_order(y, flagged):
    y, flagged = np.asarray(y), np.asarray(flagged)
    return (MISS_COST * ((flagged == 0) & (y == 1)).sum() + ALARM_COST * ((flagged == 1) & (y == 0)).sum()) / len(y)


# --- Compute everything once, exactly as the notebook does ------------------------

REGION_SE = {"SP": "to São Paulo", "RJ": "to Rio de Janeiro"}


def compute(week_03, week_03_pipeline):
    df = week_03()
    train, valid, test = (df[df["split"] == s].copy() for s in ["train", "valid", "test"])
    model = week_03_pipeline().fit(train, train["is_late"])
    valid["score"] = model.predict_proba(valid)[:, 1]
    test["score"] = model.predict_proba(test)[:, 1]
    r = {}

    grid = np.round(np.arange(0.05, 0.96, 0.01), 2)
    r["grid"] = grid
    r["curve"] = pd.DataFrame({
        "precision": [precision_score(valid["is_late"], valid["score"] >= t, zero_division=0) for t in grid],
        "recall": [recall_score(valid["is_late"], valid["score"] >= t) for t in grid],
        "flagged": [(valid["score"] >= t).mean() for t in grid],
    }, index=grid)
    r["costs"] = pd.Series([cost_per_order(valid["is_late"], valid["score"] >= t) for t in grid], index=grid)
    best = r["costs"].idxmin()
    r["best"] = best
    r["nobody_valid"] = cost_per_order(valid["is_late"], np.zeros(len(valid)))

    bins = pd.cut(valid["score"], [0, 0.2, 0.4, 0.6, 0.8, 1.0])
    r["reliability"] = valid.groupby(bins, observed=True).agg(avg=("score", "mean"), late=("is_late", "mean"))

    valid["flag"] = (valid["score"] >= best).astype(int)
    test["flag"] = (test["score"] >= best).astype(int)
    r["overall_recall"] = recall_score(valid["is_late"], valid["flag"])

    def recall_by(frame, key):
        return frame.groupby(key, observed=True).apply(
            lambda g: recall_score(g["is_late"], g["flag"], zero_division=0), include_groups=False)

    valid["route"] = np.where(valid["same_state"] == 1, "within one state", "across states")
    valid["distance"] = pd.cut(valid["distance_km"], [-1, 100, 500, 1000, 5000],
                               labels=["under 100 km", "100 to 500 km", "500 to 1000 km", "over 1000 km"])
    spj = valid[valid["customer_state"].isin(["SP", "RJ"])]
    r["slices"] = pd.concat([
        recall_by(valid, "route"),
        recall_by(valid, "distance"),
        recall_by(spj, "customer_state").rename(index=REGION_SE),
    ]).sort_values()

    late = valid[valid["is_late"] == 1].copy()
    late["days_late"] = (late["order_delivered_customer_date"].dt.normalize() - late["order_estimated_delivery_date"]).dt.days
    late["outcome"] = np.where(late["flag"] == 1, "caught", "missed")
    r["profile"] = late.groupby("outcome").agg(
        within=("same_state", "mean"),
        distance=("distance_km", "median"),
        sp=("customer_state", lambda s: (s == "SP").mean()),
        days=("days_late", "median"),
    )

    rule_rate = train.groupby("customer_state")["is_late"].mean()
    rule = test["customer_state"].map(rule_rate).fillna(train["is_late"].mean()).to_numpy()
    y, s = test["is_late"].to_numpy(), test["score"].to_numpy()
    rng = np.random.default_rng(RANDOM_STATE)
    ml, rl = [], []
    for _ in range(1000):
        i = rng.integers(0, len(y), len(y))
        ml.append(lift(y[i], s[i]))
        rl.append(lift(y[i], rule[i]))
    r["boot_model"], r["boot_rule"] = np.array(ml), np.array(rl)
    r["test_lift"] = lift(y, s)

    r["decision"] = pd.DataFrame({
        "the model": [cost_per_order(valid["is_late"], valid["flag"]), cost_per_order(test["is_late"], test["flag"])],
        "flag nobody": [r["nobody_valid"], cost_per_order(test["is_late"], np.zeros(len(test)))],
        "precision": [precision_score(valid["is_late"], valid["flag"]), precision_score(test["is_late"], test["flag"])],
        "late rate": [valid["is_late"].mean(), test["is_late"].mean()],
    }, index=["validation", "test"])

    both = pd.concat([valid.assign(part="validation"), test.assign(part="test")])
    month = both["order_purchase_timestamp"].dt.to_period("M")
    r["months"] = both.groupby(month).apply(lambda g: pd.Series({
        "precision": precision_score(g["is_late"], g["flag"], zero_division=0),
        "late": g["is_late"].mean(),
        "part": g["part"].iloc[0],
    }), include_groups=False)
    return r


# --- Figures ----------------------------------------------------------------------------


def threshold_fig(r, theme):
    c = THEMES[theme]
    cv = r["curve"]
    fig, ax = plt.subplots(figsize=(8, 3.7))
    ax.plot(cv.index, cv["precision"], color=c["accent"], lw=2.2, label="precision: flags that were right")
    ax.plot(cv.index, cv["recall"], color=c["warm"], lw=2.2, label="recall: late orders caught")
    ax.plot(cv.index, cv["flagged"], color=c["faint"], lw=2.2, label="share of orders flagged")
    ax.axvline(r["best"], color=c["fg"], lw=1, ls=(0, (4, 3)))
    ax.text(r["best"] + 0.01, 0.93, f"chosen: {r['best']:.2f}", color=c["fg"], fontsize=8.5)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel("threshold", color=c["muted"], fontsize=8)
    legend(ax, c, loc="upper right")
    style_axes(ax, c)
    save(fig, f"w04-threshold-{theme}.png")


def cost_fig(r, theme):
    c = THEMES[theme]
    costs = r["costs"]
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.plot(costs.index, costs.values, color=c["accent"], lw=2.2, label="the model, at each threshold")
    ax.axhline(r["nobody_valid"], color=c["muted"], ls=(0, (4, 3)), lw=1.3, label="flag nobody")
    ax.scatter([r["best"]], [costs[r["best"]]], color=c["warm"], s=60, zorder=3)
    ax.annotate(f"cheapest at {r['best']:.2f}\n{costs[r['best']]:.2f} per order", (r["best"], costs[r["best"]]),
                xytext=(r["best"] + 0.08, costs[r["best"]] + 0.02), color=c["fg"], fontsize=8.5)
    ax.set_xlabel("threshold", color=c["muted"], fontsize=8)
    ax.set_ylabel("cost per order", color=c["muted"], fontsize=8)
    legend(ax, c, loc="upper left", bbox_to_anchor=(0.02, 0.9))
    style_axes(ax, c)
    save(fig, f"w04-cost-{theme}.png")


def reliability_fig(r, theme):
    c = THEMES[theme]
    rel = r["reliability"]
    fig, ax = plt.subplots(figsize=(5, 4.6))
    ax.plot([0, 1], [0, 1], color=c["muted"], ls=(0, (4, 3)), lw=1.2, label="if scores were probabilities")
    ax.plot(rel["avg"], rel["late"], color=c["warm"], marker="o", lw=2.4, label="our model")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("average score", color=c["muted"], fontsize=8)
    ax.set_ylabel("share actually late", color=c["muted"], fontsize=8)
    legend(ax, c, loc="upper left")
    style_axes(ax, c)
    save(fig, f"w04-reliability-{theme}.png")


def slices_fig(r, theme):
    c = THEMES[theme]
    s = r["slices"]
    overall = r["overall_recall"]
    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.barh(s.index, s.values, color=[c["warm"] if v < overall else c["accent"] for v in s.values], height=0.6)
    for i, v in enumerate(s.values):
        ax.text(v + 0.01, i, f"{v:.0%}", va="center", fontsize=8, color=c["fg"])
    ax.axvline(overall, color=c["fg"], ls=(0, (4, 3)), lw=1.1)
    ax.text(overall + 0.01, len(s) - 0.4, f"overall {overall:.0%}", color=c["fg"], fontsize=8.5)
    ax.set_xlim(0, 1.1)
    ax.xaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xlabel("recall: share of late orders the model catches", color=c["muted"], fontsize=8)
    ax.tick_params(axis="y", colors=c["fg"], labelsize=8.5)
    style_axes(ax, c)
    save(fig, f"w04-slices-{theme}.png")


def profile_fig(r, theme):
    c = THEMES[theme]
    p = r["profile"]
    panels = [
        ("within", "within one state", lambda v: f"{v:.0%}"),
        ("distance", "median distance", lambda v: f"{v:,.0f} km"),
        ("sp", "going to São Paulo", lambda v: f"{v:.0%}"),
        ("days", "median days late", lambda v: f"{v:.0f} days"),
    ]
    fig, axes = plt.subplots(1, 4, figsize=(10.5, 2.9))
    for ax, (col, title, fmt) in zip(axes, panels):
        vals = [p.loc["caught", col], p.loc["missed", col]]
        ax.bar(["caught", "missed"], vals, color=[c["accent"], c["warm"]], width=0.6)
        for i, v in enumerate(vals):
            ax.text(i, v * 1.03, fmt(v), ha="center", va="bottom", fontsize=8.5, color=c["fg"])
        ax.set_title(title, color=c["fg"], fontsize=9.5, loc="center")
        ax.set_ylim(0, max(vals) * 1.3)
        ax.set_yticks([])
        ax.tick_params(axis="x", colors=c["fg"], labelsize=8.5)
        style_axes(ax, c)
        ax.spines["left"].set_visible(False)
    fig.tight_layout(w_pad=2)
    save(fig, f"w04-profile-{theme}.png")


def bootstrap_fig(r, theme):
    c = THEMES[theme]
    bm, br = r["boot_model"], r["boot_rule"]
    bins = np.linspace(0.8, 2.3, 60)
    fig, ax = plt.subplots(figsize=(8, 3.4))
    ax.hist(br, bins=bins, color=c["faint"], label="Week 1's rule")
    ax.hist(bm, bins=bins, color=c["accent"], alpha=0.9, label="Week 3 model")
    lo, hi = np.percentile(bm, [2.5, 97.5])
    top = ax.get_ylim()[1]
    ax.annotate("", xy=(hi, top * 0.92), xytext=(lo, top * 0.92), arrowprops=dict(arrowstyle="<->", color=c["fg"], lw=1.2))
    ax.text((lo + hi) / 2, top * 0.96, f"95% of resamples: {lo:.2f} to {hi:.2f}", ha="center", color=c["fg"], fontsize=8.5)
    ax.axvline(1, color=c["fg"], ls=(0, (4, 3)), lw=1)
    ax.set_xlabel("test lift, over 1,000 bootstrap resamples", color=c["muted"], fontsize=8)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    legend(ax, c, loc="center left")
    style_axes(ax, c)
    ax.spines["left"].set_visible(False)
    save(fig, f"w04-bootstrap-{theme}.png")


def decision_fig(r, theme):
    c = THEMES[theme]
    d = r["decision"]
    x = np.arange(2)
    w = 0.34
    fig, ax = plt.subplots(figsize=(7, 3.8))
    ax.bar(x - w / 2, d["the model"], width=w, color=c["accent"], label="the model, threshold 0.48")
    ax.bar(x + w / 2, d["flag nobody"], width=w, color=c["faint"], label="flag nobody")
    for xi in x:
        ax.text(xi - w / 2, d["the model"].iloc[xi] + 0.02, f"{d['the model'].iloc[xi]:.2f}", ha="center", fontsize=9, color=c["fg"], weight="bold")
        ax.text(xi + w / 2, d["flag nobody"].iloc[xi] + 0.02, f"{d['flag nobody'].iloc[xi]:.2f}", ha="center", fontsize=9, color=c["fg"])
    labels = [f"validation\n{d['late rate'].iloc[0]:.1%} late, precision {d['precision'].iloc[0]:.0%}",
              f"test\n{d['late rate'].iloc[1]:.1%} late, precision {d['precision'].iloc[1]:.0%}"]
    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=c["fg"], fontsize=8.5)
    ax.set_ylabel("cost per order", color=c["muted"], fontsize=8)
    ax.set_ylim(0, 1.45)
    legend(ax, c, loc="upper right")
    style_axes(ax, c)
    save(fig, f"w04-decision-{theme}.png")


def months_fig(r, theme):
    c = THEMES[theme]
    m = r["months"]
    labels = [p.strftime("%b %Y") for p in m.index]
    colours = [c["warm"] if part == "validation" else c["green"] for part in m["part"]]
    fig, ax = plt.subplots(figsize=(8, 3.6))
    ax.bar(labels, m["precision"].astype(float), color=colours, width=0.6)
    for i, (p, late) in enumerate(zip(m["precision"].astype(float), m["late"].astype(float))):
        ax.text(i, p + 0.008, f"{p:.0%}", ha="center", fontsize=9, color=c["fg"], weight="bold")
        ax.text(i, -0.035, f"{late:.1%} late", ha="center", fontsize=7.5, color=c["muted"])
    ax.axhline(ALARM_COST / MISS_COST, color=c["fg"], ls=(0, (4, 3)), lw=1.2)
    ax.text(len(m) - 0.5, 0.3, "dashed line: break-even, 10%", ha="right", color=c["fg"], fontsize=8.5)
    ax.text(0.5, 0.36, "validation", ha="center", color=c["warm"], fontsize=9, weight="bold")
    ax.text(3.5, 0.36, "test", ha="center", color=c["green"], fontsize=9, weight="bold")
    ax.set_ylim(-0.06, 0.4)
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.set_ylabel("flags that were right", color=c["muted"], fontsize=8)
    ax.tick_params(axis="x", colors=c["fg"], labelsize=8.5, pad=14)
    style_axes(ax, c)
    save(fig, f"w04-months-{theme}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"))
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "checkpoints.py").exists():
        print(f"Cannot find checkpoints.py in {labs}. Pass --labs /path/to/ml-course-labs", file=sys.stderr)
        return 1
    sys.path.insert(0, str(labs))
    from checkpoints import week_03, week_03_pipeline

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    r = compute(week_03, week_03_pipeline)
    lo, hi = np.percentile(r["boot_model"], [2.5, 97.5])
    print(f"  threshold {r['best']:.2f}, validation cost {r['costs'][r['best']]:.3f} vs nobody {r['nobody_valid']:.3f}")
    print(f"  test lift {r['test_lift']:.2f}, interval {lo:.2f} to {hi:.2f}")
    print(r["decision"].round(3).to_string())
    print(r["months"].to_string())

    print("Generating Week 4 figures")
    for theme in THEMES:
        threshold_fig(r, theme)
        cost_fig(r, theme)
        reliability_fig(r, theme)
        slices_fig(r, theme)
        profile_fig(r, theme)
        bootstrap_fig(r, theme)
        decision_fig(r, theme)
        months_fig(r, theme)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
