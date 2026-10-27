#!/usr/bin/env python3
"""
Figures for docs/02-data-pipeline/week-03-feature-engineering.md

Imports week_03() and week_03_pipeline() from the labs repository, so every
number matches the Week 3 notebooks.

    python scripts/figures/week03_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/02-data-pipeline/, light and dark versions of:
    w03-two-kinds     concept: row-wise versus learned features
    w03-cross-fit     concept: how cross-fitted target encoding works
    w03-single        each row-wise feature used alone, on validation
    w03-leak          the seller rate, computed on all data versus on train
    w03-encoding      naive versus cross-fitted encoding, train and validation
    w03-coefs         the chosen model's coefficients
    w03-ablation      which additions earn their place, on validation
    w03-progress      test lift, Week 1 baselines versus the Week 3 model
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, TargetEncoder
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "02-data-pipeline"
RANDOM_STATE = 42
DPI = 200

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3f51b5", "warm": "#e07b39",
              "faint": "#c9cdd6", "soft": "#e8eaf6", "row": "#eef0f4", "white": "#ffffff"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#9fa8da", "warm": "#f0a868",
             "faint": "#4b5160", "soft": "#2d3350", "row": "#2a2e38", "white": "#1e2129"},
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


def lift(y, s):
    return average_precision_score(y, s) / np.mean(y)


# --- The route transformer, exactly as in the notebook ---------------------------


class RouteSlack(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        day = X["order_purchase_timestamp"].dt.normalize()
        taken = (X["order_delivered_customer_date"].dt.normalize() - day).dt.days
        route = X["seller_state"] + " > " + X["customer_state"]
        self.typical_days_ = taken.groupby(route).median()
        self.overall_days_ = taken.median()
        return self

    def transform(self, X):
        route = X["seller_state"] + " > " + X["customer_state"]
        typical = route.map(self.typical_days_).fillna(self.overall_days_)
        promised = (X["order_estimated_delivery_date"] - X["order_purchase_timestamp"].dt.normalize()).dt.days
        return pd.DataFrame({"slack_days": promised - typical}, index=X.index)

    def get_feature_names_out(self, input_features=None):
        return np.array(["slack_days"])


# --- Concept 1: two kinds of feature ---------------------------------------------


def two_kinds(theme):
    c = THEMES[theme]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.6))
    n = 9
    for ax in axes:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")

    def row(ax, y, colour, edge=None, hatch=None, alpha=1):
        ax.add_patch(FancyBboxPatch((0.6, y), 3.4, 0.62, boxstyle="round,pad=0.02,rounding_size=0.12",
                                    fc=colour, ec=edge or colour, lw=1.2, hatch=hatch, alpha=alpha))

    def box(ax, x, y, w, h, text, fc, tc):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.25", fc=fc, ec=fc))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", color=tc, fontsize=10, weight="bold")

    def arrow(ax, start, end, colour, lw=1.4):
        ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=12, color=colour, lw=lw))

    # Left: row-wise
    ax = axes[0]
    ys = [1.0 + i * 0.85 for i in range(n)][::-1]
    for i, y in enumerate(ys):
        row(ax, y, c["accent"] if i == 4 else c["row"])
    box(ax, 5.8, ys[4] - 0.35, 3.6, 1.3, "distance\n453 km", c["accent"], c["white"])
    arrow(ax, (4.1, ys[4] + 0.31), (5.7, ys[4] + 0.31), c["accent"])
    ax.text(0.6, 9.55, "Row-wise", color=c["fg"], fontsize=13, weight="bold")
    ax.text(0.6, 0.25, "One row in, one value out.\nThe same wherever the row ends up.", color=c["muted"], fontsize=9, va="top")

    # Right: learned
    ax = axes[1]
    for i, y in enumerate(ys):
        if i < 6:
            row(ax, y, c["soft"], edge=c["accent"])
        else:
            row(ax, y, c["row"], edge=c["faint"], hatch="///" if theme == "light" else "..", alpha=0.9)
    ax.text(0.7, ys[0] + 0.72, "train", color=c["accent"], fontsize=8.5, weight="bold")
    ax.text(4.3, ys[7] + 0.31, "valid and test:\nnever used", color=c["muted"], fontsize=8.5, va="center")
    box(ax, 5.8, 5.2, 3.6, 1.3, "seller's\nlate rate", c["warm"], c["white"])
    for i in range(6):
        arrow(ax, (4.1, ys[i] + 0.31), (5.7, 5.85), c["faint"], lw=0.9)
    ax.text(0.6, 9.55, "Learned", color=c["fg"], fontsize=13, weight="bold")
    ax.text(0.6, 0.25, "Computed from many rows.\nSafe only if those rows are training rows.", color=c["muted"], fontsize=9, va="top")

    save(fig, f"w03-two-kinds-{theme}.png")


# --- Concept 2: cross-fitting -------------------------------------------------------


def cross_fit(theme):
    c = THEMES[theme]
    k = 5
    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    for r in range(k):
        for col in range(k):
            encoded = r == col
            fc = c["warm"] if encoded else c["soft"]
            ec = c["warm"] if encoded else c["accent"]
            ax.add_patch(FancyBboxPatch((col * 1.15, (k - 1 - r) * 0.8), 1.0, 0.62,
                                        boxstyle="round,pad=0.02,rounding_size=0.1", fc=fc, ec=ec, lw=1))
            ax.text(col * 1.15 + 0.5, (k - 1 - r) * 0.8 + 0.31, "encoded" if encoded else "rates from here",
                    ha="center", va="center", fontsize=7, color=c["white"] if encoded else c["fg"])
        ax.text(-0.2, (k - 1 - r) * 0.8 + 0.31, f"step {r + 1}", ha="right", va="center", fontsize=8.5, color=c["muted"])
    for col in range(k):
        ax.text(col * 1.15 + 0.5, k * 0.8 + 0.05, f"fold {col + 1}", ha="center", fontsize=8.5, color=c["fg"], weight="bold")
    ax.text(0, -0.55, "Each fold of the training data is encoded with rates computed from the other four,\n"
                      "so no row ever sees its own label.", fontsize=9, color=c["muted"], va="top")
    ax.set_xlim(-1.3, k * 1.15)
    ax.set_ylim(-1.5, k * 0.8 + 0.5)
    ax.axis("off")
    save(fig, f"w03-cross-fit-{theme}.png")


# --- Data figures ----------------------------------------------------------------------


def build(features, extra=None, estimator=None):
    parts = [
        ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), features),
        ("states", OneHotEncoder(handle_unknown="ignore"), ["customer_state", "seller_state"]),
    ]
    if extra == "route slack":
        cols = ["order_purchase_timestamp", "order_estimated_delivery_date",
                "order_delivered_customer_date", "seller_state", "customer_state"]
        parts.append(("slack", Pipeline([("slack", RouteSlack()), ("scale", StandardScaler())]), cols))
    elif extra == "category":
        parts.append(("category", TargetEncoder(random_state=RANDOM_STATE), ["category"]))
    elif extra == "seller":
        parts.append(("seller", TargetEncoder(random_state=RANDOM_STATE), ["seller_id"]))
    estimator = estimator or LogisticRegression(max_iter=2000, class_weight="balanced")
    return Pipeline([("prep", ColumnTransformer(parts)), ("model", estimator)])


def compute(df, features, week_03_pipeline):
    train, valid, test = (df[df["split"] == s] for s in ["train", "valid", "test"])
    y_tr, y_va, y_te = train["is_late"], valid["is_late"], test["is_late"]
    res = {}

    single = {}
    for f in features:
        v = valid[f].fillna(train[f].median())
        single[f] = max(lift(y_va, v), lift(y_va, -v))
    res["single"] = pd.Series(single).sort_values()

    overall = y_tr.mean()
    rate_all = df.groupby("seller_id")["is_late"].mean()
    rate_train = train.groupby("seller_id")["is_late"].mean()
    res["leak"] = (lift(y_va, valid["seller_id"].map(rate_train).fillna(overall)),
                   lift(y_va, valid["seller_id"].map(rate_all).fillna(overall)))

    def seller_model():
        prep = ColumnTransformer([
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]), features + ["seller_rate"]),
            ("states", OneHotEncoder(handle_unknown="ignore"), ["customer_state", "seller_state"]),
        ])
        return Pipeline([("prep", prep), ("model", LogisticRegression(max_iter=2000, class_weight="balanced"))])

    ntr = train.assign(seller_rate=train["seller_id"].map(rate_train).fillna(overall))
    nva = valid.assign(seller_rate=valid["seller_id"].map(rate_train).fillna(overall))
    naive = seller_model().fit(ntr, y_tr)
    enc = TargetEncoder(random_state=RANDOM_STATE)
    ftr = train.assign(seller_rate=enc.fit_transform(train[["seller_id"]], y_tr).ravel())
    fva = valid.assign(seller_rate=enc.transform(valid[["seller_id"]]).ravel())
    fair = seller_model().fit(ftr, y_tr)
    res["encoding"] = pd.DataFrame({
        "train": [lift(y_tr, naive.predict_proba(ntr)[:, 1]), lift(y_tr, fair.predict_proba(ftr)[:, 1])],
        "validation": [lift(y_va, naive.predict_proba(nva)[:, 1]), lift(y_va, fair.predict_proba(fva)[:, 1])],
    }, index=["naive", "cross-fitted"])

    chosen = week_03_pipeline().fit(train, y_tr)
    names = chosen.named_steps["prep"].get_feature_names_out()
    coefs = pd.Series(chosen.named_steps["model"].coef_[0], index=names)
    res["coefs"] = coefs[[f"numeric__{f}" for f in features]].rename(lambda n: n.replace("numeric__", "")).sort_values()

    candidates = {
        "row-wise only": build(features),
        "+ route slack": build(features, "route slack"),
        "+ category": build(features, "category"),
        "+ seller": build(features, "seller"),
        "row-wise, as a tree": build(features, estimator=DecisionTreeClassifier(
            max_depth=6, min_samples_leaf=200, class_weight="balanced", random_state=RANDOM_STATE)),
    }
    res["ablation"] = pd.Series({n: lift(y_va, p.fit(train, y_tr).predict_proba(valid)[:, 1]) for n, p in candidates.items()})
    res["valid_lift"] = lift(y_va, chosen.predict_proba(valid)[:, 1])
    res["test_lift"] = lift(y_te, chosen.predict_proba(test)[:, 1])
    return res


def single_chart(res, theme):
    c = THEMES[theme]
    s = res["single"]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.barh(s.index, s.values, color=[c["accent"] if v > 1.15 else c["faint"] for v in s.values], height=0.6)
    ax.axvline(1, color=c["fg"], ls=(0, (4, 3)), lw=1)
    for i, v in enumerate(s.values):
        ax.text(v + 0.02, i, f"{v:.2f}", va="center", fontsize=8, color=c["fg"])
    ax.set_xlabel("lift on validation, each feature used alone", color=c["muted"], fontsize=8)
    ax.tick_params(axis="y", colors=c["fg"], labelsize=8)
    ax.set_xlim(0, 1.9)
    style_axes(ax, c)
    save(fig, f"w03-single-{theme}.png")


def leak_chart(res, theme):
    c = THEMES[theme]
    honest, leaky = res["leak"]
    fig, ax = plt.subplots(figsize=(6.4, 2.6))
    ax.barh(["computed on\ntraining orders only", "computed on\nall orders"], [honest, leaky],
            color=[c["accent"], c["warm"]], height=0.55)
    for i, v in enumerate([honest, leaky]):
        ax.text(v + 0.03, i, f"{v:.2f}", va="center", fontsize=10, color=c["fg"], weight="bold")
    ax.axvline(1, color=c["fg"], ls=(0, (4, 3)), lw=1)
    ax.set_xlim(0, 2.2)
    ax.set_xlabel("validation lift of the seller's late rate", color=c["muted"], fontsize=8)
    ax.tick_params(axis="y", colors=c["fg"], labelsize=9)
    style_axes(ax, c)
    save(fig, f"w03-leak-{theme}.png")


def encoding_chart(res, theme):
    c = THEMES[theme]
    e = res["encoding"]
    x = np.arange(2)
    w = 0.34
    fig, ax = plt.subplots(figsize=(6.4, 3.6))
    ax.bar(x - w / 2, e["train"], width=w, color=c["faint"], label="train")
    ax.bar(x + w / 2, e["validation"], width=w, color=c["accent"], label="validation")
    for xi in x:
        ax.text(xi - w / 2, e["train"].iloc[xi] + 0.06, f"{e['train'].iloc[xi]:.2f}", ha="center", fontsize=9, color=c["fg"])
        ax.text(xi + w / 2, e["validation"].iloc[xi] + 0.06, f"{e['validation'].iloc[xi]:.2f}", ha="center", fontsize=9, color=c["fg"], weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(["naive encoding", "cross-fitted encoding"], color=c["fg"], fontsize=9)
    ax.set_ylim(0, 4.6)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)
    leg = ax.legend(frameon=False, fontsize=9)
    for t in leg.get_texts():
        t.set_color(c["fg"])
    style_axes(ax, c)
    ax.spines["left"].set_visible(False)
    save(fig, f"w03-encoding-{theme}.png")


def coef_chart(res, theme):
    c = THEMES[theme]
    s = res["coefs"]
    fig, ax = plt.subplots(figsize=(7, 3.6))
    ax.barh(s.index, s.values, color=[c["warm"] if v > 0 else c["accent"] for v in s.values], height=0.6)
    ax.axvline(0, color=c["fg"], lw=1)
    ax.text(0.01, -1.15, "more likely late  →", color=c["warm"], fontsize=8.5)
    ax.text(-0.01, -1.15, "←  more likely on time", color=c["accent"], fontsize=8.5, ha="right")
    ax.set_ylim(-1.5, len(s) - 0.4)
    ax.set_xlabel("coefficient on the scaled feature", color=c["muted"], fontsize=8)
    ax.tick_params(axis="y", colors=c["fg"], labelsize=8)
    style_axes(ax, c)
    save(fig, f"w03-coefs-{theme}.png")


def ablation_chart(res, theme):
    c = THEMES[theme]
    s = res["ablation"].sort_values()
    best = s.idxmax()
    fig, ax = plt.subplots(figsize=(7, 3.2))
    ax.barh(s.index, s.values, color=[c["accent"] if n == best else c["faint"] for n in s.index], height=0.6)
    for i, v in enumerate(s.values):
        ax.text(v + 0.01, i, f"{v:.2f}", va="center", fontsize=8.5, color=c["fg"])
    ax.set_xlim(1, 2.55)
    ax.set_xlabel("validation lift", color=c["muted"], fontsize=8)
    ax.tick_params(axis="y", colors=c["fg"], labelsize=9)
    style_axes(ax, c)
    save(fig, f"w03-ablation-{theme}.png")


def progress_chart(res, theme):
    c = THEMES[theme]
    values = [1.10, 1.18, res["test_lift"]]
    labels = ["Week 1\nrule", "Week 1\ntree", "Week 3\nmodel"]
    fig, ax = plt.subplots(figsize=(6, 3.5))
    ax.bar(labels, values, color=[c["faint"], c["faint"], c["accent"]], width=0.55)
    for i, v in enumerate(values):
        ax.text(i, v + 0.04, f"{v:.2f}", ha="center", fontsize=11, color=c["fg"], weight="bold")
    ax.axhline(1, color=c["fg"], ls=(0, (4, 3)), lw=1)
    ax.text(-0.42, 1.04, "guessing", color=c["muted"], fontsize=8.5, ha="left")
    ax.set_ylim(0, 2.2)
    ax.set_yticks([])
    ax.tick_params(axis="x", colors=c["fg"], labelsize=9)
    style_axes(ax, c)
    ax.spines["left"].set_visible(False)
    save(fig, f"w03-progress-{theme}.png")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"))
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "checkpoints.py").exists():
        print(f"Cannot find checkpoints.py in {labs}. Pass --labs /path/to/ml-course-labs", file=sys.stderr)
        return 1
    sys.path.insert(0, str(labs))
    from checkpoints import ROW_WISE_FEATURES, week_03, week_03_pipeline

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    df = week_03()
    res = compute(df, ROW_WISE_FEATURES, week_03_pipeline)
    print(f"  leak: {res['leak'][0]:.2f} honest, {res['leak'][1]:.2f} leaky")
    print(res["encoding"].round(2).to_string())
    print(res["ablation"].round(2).to_string())
    print(f"  chosen model: validation {res['valid_lift']:.2f}, test {res['test_lift']:.2f}")

    print("Generating Week 3 figures")
    for theme in THEMES:
        two_kinds(theme)
        cross_fit(theme)
        single_chart(res, theme)
        leak_chart(res, theme)
        encoding_chart(res, theme)
        coef_chart(res, theme)
        ablation_chart(res, theme)
        progress_chart(res, theme)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
