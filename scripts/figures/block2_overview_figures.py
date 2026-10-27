#!/usr/bin/env python3
"""
Figures for docs/03-models-optimization/index.md

The bar Block 2 has to beat: what Project 1's tools achieved on the July trips,
recomputed from the data so the overview page and the reference notebooks agree.

    python scripts/figures/block2_overview_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/03-models-optimization/, light and dark versions of:
    b2-bar     the four questions, Project 1's result against the simplest answer
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeRegressor

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "03-models-optimization"
RANDOM_STATE = 42
DPI = 200

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3d5a80", "warm": "#c05d3e", "faint": "#cfc6b7"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#8fb0d4", "warm": "#e0855f", "faint": "#4b5160"},
}

CATEGORICAL = ["hour", "weekday", "pickup_borough", "dropoff_borough", "PULocationID", "DOLocationID"]


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


def prep(numeric, scale):
    steps = [("impute", SimpleImputer(strategy="median"))]
    if scale:
        steps.append(("scale", StandardScaler()))
    return ColumnTransformer([
        ("numeric", Pipeline(steps), numeric),
        ("categories", OneHotEncoder(handle_unknown="ignore", min_frequency=20, sparse_output=scale), CATEGORICAL),
    ])


def compute(taxi):
    df = taxi.block_2()
    booking = taxi.AT_BOOKING_NUMERIC + ["hour", "weekday"]
    results = {}

    for label, question, depth in [("A · fare", taxi.question_a, 12), ("B · duration", taxi.question_b, 16)]:
        train, _, test = taxi.splits(question(df))
        model = Pipeline([("prep", prep(booking, scale=False)),
                          ("model", DecisionTreeRegressor(max_depth=depth, min_samples_leaf=50, random_state=RANDOM_STATE))])
        model.fit(train, train["target"])
        results[label] = {
            "kind": "regression",
            "baseline": float(np.abs(test["target"] - train["target"].median()).mean()),
            "model": float(np.abs(test["target"] - model.predict(test)).mean()),
            "unit": "$" if label.startswith("A") else "min",
        }

    for label, question, numeric in [("C · crawl", taxi.question_c, booking),
                                     ("D · tip", taxi.question_d, taxi.AT_PAYMENT_NUMERIC + ["hour", "weekday"])]:
        train, _, test = taxi.splits(question(df))
        model = Pipeline([("prep", prep(numeric, scale=True)), ("model", LogisticRegression(max_iter=3000))])
        model.fit(train, train["target"])
        scores = model.predict_proba(test)[:, 1]
        results[label] = {
            "kind": "classification",
            "baseline": 1.0,
            "model": float(average_precision_score(test["target"], scores) / test["target"].mean()),
            "unit": "",
        }
    return results


def chart(results, theme):
    c = THEMES[theme]
    regression = {k: v for k, v in results.items() if v["kind"] == "regression"}
    classification = {k: v for k, v in results.items() if v["kind"] == "classification"}

    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.8))

    x = np.arange(len(regression))
    ax = axes[0]
    ax.bar(x - 0.19, [v["baseline"] for v in regression.values()], width=0.38, color=c["faint"], label="the simplest answer")
    ax.bar(x + 0.19, [v["model"] for v in regression.values()], width=0.38, color=c["accent"], label="Project 1's model")
    def money(value, unit):
        return f"${value:.2f}" if unit == "$" else f"{value:.2f} {unit}"

    for i, v in enumerate(regression.values()):
        ax.text(i - 0.19, v["baseline"] + 0.12, money(v["baseline"], v["unit"]), ha="center", fontsize=8.5, color=c["muted"])
        ax.text(i + 0.19, v["model"] + 0.12, money(v["model"], v["unit"]), ha="center", fontsize=9.5, color=c["fg"], weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(regression.keys(), color=c["fg"], fontsize=9)
    ax.set_ylabel("error on July, lower is better", color=c["muted"], fontsize=8)
    ax.set_ylim(0, max(v["baseline"] for v in regression.values()) * 1.25)
    leg = ax.legend(frameon=False, fontsize=8.5)
    for t in leg.get_texts():
        t.set_color(c["fg"])
    style(ax, c)

    ax = axes[1]
    x = np.arange(len(classification))
    ax.bar(x, [v["model"] for v in classification.values()], width=0.45, color=c["accent"])
    ax.axhline(1, color=c["fg"], ls=(0, (4, 3)), lw=1.2)
    ax.text(len(classification) - 0.5, 1.08, "guessing", ha="right", color=c["muted"], fontsize=8.5)
    for i, v in enumerate(classification.values()):
        ax.text(i, v["model"] + 0.08, f"{v['model']:.2f}", ha="center", fontsize=9.5, color=c["fg"], weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(classification.keys(), color=c["fg"], fontsize=9)
    ax.set_ylabel("lift on July, higher is better", color=c["muted"], fontsize=8)
    ax.set_ylim(0, 4.3)
    style(ax, c)

    fig.tight_layout(w_pad=3)
    save(fig, f"b2-bar-{theme}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"))
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "taxi.py").exists():
        print(f"Cannot find taxi.py in {labs}. Pass --labs /path/to/ml-course-labs", file=sys.stderr)
        return 1
    sys.path.insert(0, str(labs))
    import taxi

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    results = compute(taxi)
    for label, row in results.items():
        print(f"  {label:14} baseline {row['baseline']:.2f}{row['unit']}  model {row['model']:.2f}{row['unit']}")
    print("Generating Block 2 overview figures")
    for theme in THEMES:
        chart(results, theme)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
