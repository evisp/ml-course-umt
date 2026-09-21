#!/usr/bin/env python3
"""
Figures for docs/06-reference/metrics.md

Run from the repository root:

    python scripts/figures/metrics_figures.py

Outputs into docs/assets/images/06-reference/:
    mae-vs-rmse-{light,dark}.png
    threshold-tradeoff-{light,dark}.png
    roc-vs-pr-{light,dark}.png

All data is synthetic and seeded. Needs numpy, matplotlib and scikit-learn.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    precision_recall_curve,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import train_test_split

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "06-reference"
OUT.mkdir(parents=True, exist_ok=True)

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3f51b5", "warm": "#e07b39", "faint": "#c9cdd6"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#9fa8da", "warm": "#f0a868", "faint": "#4b5160"},
}

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


# --- Figure 1: one bad miss moves RMSE far more than MAE ---------------------


def mae_vs_rmse(theme: str) -> None:
    c = THEMES[theme]
    errors = np.array([6, 4, 9, 5, 7, 3, 8, 5, 6, 4], dtype=float)   # thousand euros
    with_miss = errors.copy()
    with_miss[6] = 80

    def mae(e):
        return np.mean(np.abs(e))

    def rmse(e):
        return np.sqrt(np.mean(e**2))

    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.6), gridspec_kw={"width_ratios": [1.25, 1]})

    ax = axes[0]
    idx = np.arange(len(errors))
    colours = [c["warm"] if i == 6 else c["accent"] for i in idx]
    ax.bar(idx, with_miss, color=colours, width=0.65)
    ax.set_xticks(idx)
    ax.set_xticklabels([str(i + 1) for i in idx])
    ax.set_xlabel("prediction", color=c["muted"], fontsize=8)
    ax.set_ylabel("absolute error (thousand €)", color=c["muted"], fontsize=8)
    ax.text(6, 83, "one bad miss", color=c["warm"], fontsize=9, ha="center", weight="bold")
    ax.set_ylim(0, 95)
    ax.set_title("Ten predictions, nine of them close", color=c["fg"], fontsize=10, pad=8)
    style_axes(ax, c)

    ax = axes[1]
    groups = ["MAE", "RMSE"]
    before = [mae(errors), rmse(errors)]
    after = [mae(with_miss), rmse(with_miss)]
    x = np.arange(2)
    w = 0.34
    ax.bar(x - w / 2, before, width=w, color=c["faint"], label="without the miss")
    ax.bar(x + w / 2, after, width=w, color=c["warm"], label="with the miss")
    for xi, b, a in zip(x, before, after):
        ax.text(xi - w / 2, b + 0.8, f"{b:.1f}", ha="center", color=c["muted"], fontsize=8.5)
        ax.text(xi + w / 2, a + 0.8, f"{a:.1f}", ha="center", color=c["fg"], fontsize=8.5, weight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(groups, color=c["fg"], fontsize=10)
    ax.set_ylim(0, max(after) * 1.25)
    ax.set_title(
        f"MAE grows ×{after[0] / before[0]:.1f}, RMSE grows ×{after[1] / before[1]:.1f}",
        color=c["fg"],
        fontsize=10,
        pad=8,
    )
    leg = ax.legend(frameon=False, fontsize=8.5, loc="upper left")
    for t in leg.get_texts():
        t.set_color(c["fg"])
    style_axes(ax, c)
    ax.set_yticks([])
    ax.spines["left"].set_visible(False)

    fig.tight_layout(w_pad=3)
    save(fig, f"mae-vs-rmse-{theme}.png")


# --- Shared classifier for the two classification figures -------------------


def fitted_scores(positive_rate: float, gap: float, seed: int):
    """Two Gaussian classes whose centres sit `gap` apart, then a logistic
    regression fitted on half and scored on the other half. The gap controls
    how separable the classes are; the rate controls how rare positives are."""
    rng = np.random.default_rng(seed)
    n, d = 40000, 5
    y = (rng.random(n) < positive_rate).astype(int)
    shift = np.full(d, gap / np.sqrt(d))
    X = rng.normal(size=(n, d)) + np.outer(y, shift)

    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.5, stratify=y, random_state=seed)
    model = LogisticRegression(max_iter=2000).fit(X_tr, y_tr)
    return y_te, model.predict_proba(X_te)[:, 1]


# --- Figure 2: precision and recall against the threshold --------------------


def threshold_tradeoff(theme: str) -> None:
    c = THEMES[theme]
    y, scores = fitted_scores(positive_rate=0.2, gap=1.8, seed=1)
    precision, recall, thresholds = precision_recall_curve(y, scores)

    fig, ax = plt.subplots(figsize=(7.2, 3.8))
    ax.plot(thresholds, precision[:-1], color=c["accent"], lw=2.3, label="precision")
    ax.plot(thresholds, recall[:-1], color=c["warm"], lw=2.3, label="recall")

    ax.axvline(0.5, color=c["muted"], lw=1.2, ls=(0, (4, 3)))
    ax.text(0.51, 0.06, "default 0.5", color=c["muted"], fontsize=8.5)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1.03)
    ax.set_xlabel("decision threshold", color=c["muted"], fontsize=8)
    ax.set_title(
        "Raise the threshold: fewer flags, more of them right, more cases missed",
        color=c["fg"],
        fontsize=10,
        pad=8,
    )
    leg = ax.legend(frameon=False, fontsize=9, loc="center right")
    for t in leg.get_texts():
        t.set_color(c["fg"])
    style_axes(ax, c)
    save(fig, f"threshold-tradeoff-{theme}.png")


# --- Figure 3: ROC flatters on imbalanced data, PR does not ------------------


def roc_vs_pr(theme: str) -> None:
    c = THEMES[theme]
    rate = 0.02
    y, scores = fitted_scores(positive_rate=rate, gap=2.2, seed=4)
    prevalence = y.mean()

    fpr, tpr, _ = roc_curve(y, scores)
    precision, recall, _ = precision_recall_curve(y, scores)
    roc_auc = roc_auc_score(y, scores)
    ap = average_precision_score(y, scores)

    fig, axes = plt.subplots(1, 2, figsize=(8.8, 4.2))

    ax = axes[0]
    ax.plot([0, 1], [0, 1], color=c["faint"], lw=1.3, ls=(0, (4, 3)))
    ax.plot(fpr, tpr, color=c["accent"], lw=2.4)
    ax.text(0.55, 0.08, "random guessing", color=c["muted"], fontsize=8.5, rotation=38)
    ax.set_xlabel("false positive rate", color=c["muted"], fontsize=8)
    ax.set_ylabel("true positive rate (recall)", color=c["muted"], fontsize=8)
    ax.set_title(f"ROC curve\nAUC {roc_auc:.2f}, looks excellent", color=c["fg"], fontsize=10, pad=8)

    ax = axes[1]
    ax.axhline(prevalence, color=c["faint"], lw=1.3, ls=(0, (4, 3)))
    ax.plot(recall, precision, color=c["warm"], lw=2.4)
    ax.text(0.02, prevalence + 0.03, f"random guessing ({prevalence:.0%})", color=c["muted"], fontsize=8.5)
    ax.set_xlabel("recall", color=c["muted"], fontsize=8)
    ax.set_ylabel("precision", color=c["muted"], fontsize=8)
    ax.set_title(
        f"Precision-recall curve\naverage precision {ap:.2f}, the honest picture",
        color=c["fg"],
        fontsize=10,
        pad=8,
    )

    for ax in axes:
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1.02)
        ax.set_aspect("equal")
        style_axes(ax, c)

    fig.suptitle(
        f"The same model, on data where {rate:.0%} of cases are positive",
        color=c["fg"],
        fontsize=11,
        y=1.03,
    )
    fig.tight_layout(w_pad=2.5)
    save(fig, f"roc-vs-pr-{theme}.png")


if __name__ == "__main__":
    print("Generating metrics figures")
    for theme in THEMES:
        mae_vs_rmse(theme)
        threshold_tradeoff(theme)
        roc_vs_pr(theme)
    print("Done.")
