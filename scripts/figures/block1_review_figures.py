#!/usr/bin/env python3
"""
Figures for docs/02-data-pipeline/review.md

The journey chart is computed from the data, through the labs repository's
checkpoints, so it matches the notebooks. The progression graphic is a drawing.

    python scripts/figures/block1_review_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/02-data-pipeline/, light and dark versions of:
    b1-progression   the four weeks at a glance, into Project 1
    b1-journey       the lift as it changed across the block
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Circle, FancyBboxPatch
from sklearn.metrics import average_precision_score
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "02-data-pipeline"
RANDOM_STATE = 42
DPI = 200

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3f51b5", "warm": "#e07b39",
              "faint": "#c9cdd6", "card": "#f4f5fb", "on": "#ffffff", "bg": "#ffffff"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#9fa8da", "warm": "#f0a868",
             "faint": "#4b5160", "card": "#272b36", "on": "#1e2129", "bg": "#1e2129"},
}


def mix(colour, background, amount):
    """A solid colour `amount` of the way from background to colour."""
    from matplotlib.colors import to_rgb
    a, b = np.array(to_rgb(colour)), np.array(to_rgb(background))
    return tuple(b + (a - b) * amount)


def save(fig, name):
    path = OUT / name
    fig.savefig(path, dpi=DPI, transparent=True, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


def lift(y, s):
    return average_precision_score(y, s) / np.mean(y)


# --- The progression graphic --------------------------------------------------------

STATIONS = [
    ("01", "Frame", "“It beats nothing”", "PROBLEM.md", "1,291 labels\nfixed by one decision"),
    ("02", "Split", "“The test set\nwas unseen”", "one clean row\nper order, split by time", "lift 1.5 fell to 1.1\non the honest split"),
    ("03", "Build", "“The features\nare fair”", "a pipeline\nthat cannot leak", "lift 1.87 on test"),
    ("04", "Evaluate", "“The average\nis fine”", "MODEL_CARD.md", "15% recall\nwithin one state"),
    ("P1", "Project 1", "your data,\nyour decisions", "a repository\nsomeone else can run", "all four stages,\nwithout the notebook"),
]


def progression(theme):
    c = THEMES[theme]
    fig, ax = plt.subplots(figsize=(12, 4.6))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 4.6)
    ax.axis("off")

    xs = [1.2 + i * 2.4 for i in range(5)]
    line_y = 3.0
    ax.plot([xs[0], xs[3]], [line_y, line_y], color=c["accent"], lw=3, solid_capstyle="round", zorder=1)
    ax.plot([xs[3], xs[4]], [line_y, line_y], color=c["warm"], lw=3, ls=(0, (2, 2)), zorder=1)

    shades = [0.55, 0.7, 0.85, 1.0]
    for i, (x, (num, title, lie, built, number)) in enumerate(zip(xs, STATIONS)):
        project = num == "P1"
        colour = c["warm"] if project else c["accent"]
        alpha = 1.0 if project else shades[i]

        ax.add_patch(Circle((x, line_y), 0.36, color=mix(colour, c["bg"], alpha), zorder=2))
        ax.text(x, line_y, num, ha="center", va="center", fontsize=11, weight="bold", color=c["on"], zorder=3)
        ax.text(x, line_y + 0.62, title, ha="center", va="bottom", fontsize=12, weight="bold", color=c["fg"])
        ax.text(x, line_y + 1.08, "the lie caught" if not project else "next", ha="center", va="bottom",
                fontsize=7.5, color=c["muted"])

        ax.add_patch(FancyBboxPatch((x - 1.08, 0.18), 2.16, 2.2, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=c["card"], ec=colour if project else c["faint"], lw=1, zorder=1))
        ax.text(x, 2.2, lie, ha="center", va="top", fontsize=9, color=colour, style="italic", weight="bold")
        ax.text(x, 1.45, "built", ha="center", va="top", fontsize=7, color=c["muted"])
        ax.text(x, 1.3, built, ha="center", va="top", fontsize=8.5, color=c["fg"])
        ax.text(x, 0.72, number, ha="center", va="top", fontsize=8, color=c["muted"])

    for x in xs:
        ax.plot([x, x], [line_y - 0.36, 2.38], color=c["faint"], lw=1, zorder=0)
    save(fig, f"b1-progression-{theme}.png")


# --- The journey of one number -------------------------------------------------------


def journey_numbers(labs):
    sys.path.insert(0, str(labs))
    from checkpoints import week_02, week_03, week_03_pipeline

    df = week_02()

    def ladder(train_part, test_part):
        y = test_part["is_late"]
        rate = train_part.groupby("customer_state")["is_late"].mean()
        average = train_part["is_late"].mean()

        def feats(frame):
            frame = frame.assign(state_rate=frame["customer_state"].map(rate).fillna(average))
            frame["window_days"] = (frame["order_estimated_delivery_date"] - frame["order_purchase_timestamp"].dt.normalize()).dt.days
            frame["weekday"] = frame["order_purchase_timestamp"].dt.dayofweek
            frame["hour"] = frame["order_purchase_timestamp"].dt.hour
            return frame[["window_days", "weekday", "hour", "state_rate"]]

        tree = DecisionTreeClassifier(max_depth=2, class_weight="balanced", random_state=RANDOM_STATE)
        tree.fit(feats(train_part), train_part["is_late"])
        return {"rule": lift(y, test_part["customer_state"].map(rate).fillna(average)),
                "tree": lift(y, tree.predict_proba(feats(test_part))[:, 1])}

    rtrain, rtest = train_test_split(df, test_size=0.2, stratify=df["is_late"], random_state=RANDOM_STATE)
    week1 = ladder(rtrain, rtest)
    week2 = ladder(df[df["split"] == "train"], df[df["split"] == "test"])

    d3 = week_03()
    train, test = d3[d3["split"] == "train"], d3[d3["split"] == "test"].copy()
    model = week_03_pipeline().fit(train, train["is_late"])
    y = test["is_late"].to_numpy()
    s = model.predict_proba(test)[:, 1]
    rng = np.random.default_rng(RANDOM_STATE)
    boots = []
    for _ in range(1000):
        i = rng.integers(0, len(y), len(y))
        boots.append(lift(y[i], s[i]))
    lo, hi = np.percentile(boots, [2.5, 97.5])
    return week1, week2, lift(y, s), lo, hi


def journey(numbers, theme):
    c = THEMES[theme]
    week1, week2, final, lo, hi = numbers
    labels = ["Week 1\nrandom split", "Week 2\nsplit by time", "Weeks 3 and 4\nnew features, test"]
    values = [max(week1.values()), max(week2.values()), final]
    colours = [c["faint"], c["faint"], c["accent"]]

    fig, ax = plt.subplots(figsize=(8, 3.9))
    ax.bar(range(3), values, color=colours, width=0.55)
    ax.errorbar(2, final, yerr=[[final - lo], [hi - final]], color=c["fg"], capsize=7, lw=1.5)
    notes = ["looked good,\nbut flattered", "the honest\nstarting point", f"interval {lo:.2f} to {hi:.2f}"]
    for i, (v, note) in enumerate(zip(values, notes)):
        ax.text(i - 0.33, v + 0.05, f"{v:.2f}", ha="left", fontsize=12, weight="bold", color=c["fg"])
        ax.text(i, 0.12, note, ha="center", va="bottom", fontsize=8, color=c["on"] if i == 2 else c["fg"])
    ax.axhline(1, color=c["fg"], ls=(0, (4, 3)), lw=1)
    ax.text(0.5, 1.04, "guessing", ha="center", fontsize=8.5, color=c["muted"])
    ax.set_xticks(range(3))
    ax.set_xticklabels(labels, fontsize=9, color=c["fg"])
    ax.set_ylim(0, 2.45)
    ax.set_yticks([])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(c["faint"])
    ax.tick_params(axis="x", colors=c["fg"], length=0)
    save(fig, f"b1-journey-{theme}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"))
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "checkpoints.py").exists():
        print(f"Cannot find checkpoints.py in {labs}. Pass --labs /path/to/ml-course-labs", file=sys.stderr)
        return 1

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    numbers = journey_numbers(labs)
    week1, week2, final, lo, hi = numbers
    print(f"  Week 1 random split: rule {week1['rule']:.2f}, tree {week1['tree']:.2f}")
    print(f"  Week 2 time split, test: rule {week2['rule']:.2f}, tree {week2['tree']:.2f}")
    print(f"  Week 3 model on test: {final:.2f}, interval {lo:.2f} to {hi:.2f}")

    print("Generating Block 1 review figures")
    for theme in THEMES:
        progression(theme)
        journey(numbers, theme)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
