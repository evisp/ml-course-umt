#!/usr/bin/env python3
"""
Figures for docs/06-reference/probability-statistics.md

Run from the repository root:

    python scripts/figures/probability_figures.py

Outputs into docs/assets/images/06-reference/:
    skewed-prices-{light,dark}.png
    score-variability-{light,dark}.png
    fold-comparison-{light,dark}.png
    calibration-{light,dark}.png

All data is synthetic and seeded, so the figures are identical on every run.
Needs numpy, matplotlib and scikit-learn.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from sklearn.calibration import calibration_curve
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
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


def style_axes(ax, c, hide_y: bool = False) -> None:
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["faint"])
    ax.tick_params(colors=c["muted"], labelsize=8)
    if hide_y:
        ax.set_yticks([])
        ax.spines["left"].set_visible(False)


# --- Figure 1: a skewed target, before and after a log transform -------------


def skewed_prices(theme: str) -> None:
    c = THEMES[theme]
    rng = np.random.default_rng(3)
    prices = rng.lognormal(mean=np.log(95), sigma=0.55, size=4000)  # thousands of euros

    fig, axes = plt.subplots(1, 2, figsize=(10.0, 3.4))

    ax = axes[0]
    ax.hist(prices, bins=70, color=c["warm"], alpha=0.85)
    mean, median = prices.mean(), np.median(prices)
    ax.axvline(median, color=c["fg"], lw=1.4)
    ax.axvline(mean, color=c["fg"], lw=1.4, ls=(0, (4, 3)))
    top = ax.get_ylim()[1]
    ax.text(median - 6, top * 0.92, "median", color=c["fg"], fontsize=8, ha="right")
    ax.text(mean + 6, top * 0.80, "mean", color=c["fg"], fontsize=8, ha="left")
    ax.set_title("Price as collected\nlong right tail, mean pulled above median", color=c["fg"], fontsize=10, pad=8)
    ax.set_xlabel("price (thousand €)", color=c["muted"], fontsize=8)
    style_axes(ax, c, hide_y=True)

    ax = axes[1]
    ax.hist(np.log(prices), bins=70, color=c["accent"], alpha=0.85)
    ax.set_title("log(price)\nroughly symmetric", color=c["fg"], fontsize=10, pad=8)
    ax.set_xlabel("log of price", color=c["muted"], fontsize=8)
    style_axes(ax, c, hide_y=True)

    fig.tight_layout(w_pad=3)
    save(fig, f"skewed-prices-{theme}.png")


# --- Figure 2: one model, many random splits ---------------------------------


def score_variability(theme: str) -> None:
    c = THEMES[theme]
    X, y = make_classification(
        n_samples=600, n_features=12, n_informative=5, flip_y=0.08, class_sep=0.8, random_state=0
    )

    scores = []
    for seed in range(200):
        X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=seed, stratify=y)
        model = LogisticRegression(max_iter=1000).fit(X_tr, y_tr)
        scores.append(model.score(X_te, y_te))
    scores = np.array(scores)

    fig, ax = plt.subplots(figsize=(7.2, 3.6))
    counts, _, _ = ax.hist(scores, bins=22, color=c["accent"], alpha=0.8)
    peak = counts.max()
    ax.set_ylim(0, peak * 1.55)

    low, high = np.percentile(scores, [5, 95])
    band_y = peak * 1.18
    ax.annotate(
        "",
        xy=(high, band_y),
        xytext=(low, band_y),
        arrowprops=dict(arrowstyle="<->", color=c["fg"], lw=1.2),
    )
    ax.text(
        (low + high) / 2,
        band_y + peak * 0.07,
        f"90% of splits land between {low:.2f} and {high:.2f}",
        color=c["fg"],
        fontsize=8.5,
        ha="center",
    )

    yours = scores[17]
    ax.axvline(yours, ymax=0.68, color=c["warm"], lw=2)
    ax.text(
        yours - 0.004,
        peak * 0.98,
        "your one split",
        color=c["warm"],
        fontsize=9,
        weight="bold",
        ha="right",
    )

    ax.set_title("Same model, same data, 200 different random splits", color=c["fg"], fontsize=10, pad=8)
    ax.set_xlabel("test accuracy", color=c["muted"], fontsize=8)
    style_axes(ax, c, hide_y=True)
    save(fig, f"score-variability-{theme}.png")


# --- Figure 3: paired fold scores, noise versus a real difference ------------


def fold_comparison(theme: str) -> None:
    c = THEMES[theme]
    k = 10

    # Some folds are simply harder than others, and that affects both models.
    # This shared term is why comparing on the same folds (paired) works.
    fold_difficulty = np.random.default_rng(11).normal(0, 0.018, size=k)

    # Left panel: a tiny true gap swamped by noise. The seed is picked so the
    # draw is typical of that situation (winners split roughly evenly), since
    # the figure is meant to illustrate the case, not to be a lucky extreme.
    for seed in range(1000):
        rng = np.random.default_rng(seed)
        noisy_a = 0.810 + fold_difficulty + rng.normal(0, 0.012, size=k)
        noisy_b = 0.813 + fold_difficulty + rng.normal(0, 0.012, size=k)
        d = noisy_b - noisy_a
        if 4 <= np.sum(d > 0) <= 6 and abs(d.mean()) < 0.004:
            break

    # Right panel: a real gap, larger than the fold-to-fold noise.
    rng = np.random.default_rng(23)
    real_a = 0.800 + fold_difficulty + rng.normal(0, 0.004, size=k)
    real_b = 0.826 + fold_difficulty + rng.normal(0, 0.004, size=k)

    panels = [
        ("Not a real difference", noisy_a, noisy_b),
        ("A real difference", real_a, real_b),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9), sharey=True)

    for ax, (title, a, b) in zip(axes, panels):
        diff = b - a
        wins = int(np.sum(diff > 0))

        for ai, bi in zip(a, b):
            colour = c["accent"] if bi > ai else c["warm"]
            ax.plot([0, 1], [ai, bi], color=colour, lw=1.2, alpha=0.75, zorder=1)
        ax.scatter(np.zeros(k), a, color=c["muted"], s=18, zorder=2)
        ax.scatter(np.ones(k), b, color=c["muted"], s=18, zorder=2)

        for x, vals in ((0, a), (1, b)):
            m, s = vals.mean(), vals.std()
            ax.errorbar(
                x + (-0.14 if x == 0 else 0.14),
                m,
                yerr=s,
                fmt="o",
                color=c["fg"],
                ms=6,
                capsize=4,
                lw=1.4,
                zorder=3,
            )

        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Model A", "Model B"], color=c["fg"], fontsize=9)
        ax.set_xlim(-0.45, 1.45)
        ax.set_title(
            f"{title}\nB wins on {wins} of {k} folds, mean gain {diff.mean():+.3f}",
            color=c["fg"],
            fontsize=10,
            pad=8,
        )
        style_axes(ax, c)

    axes[0].set_ylabel("score on each fold", color=c["muted"], fontsize=8)
    fig.tight_layout(w_pad=3)
    save(fig, f"fold-comparison-{theme}.png")


# --- Figure 4: calibration ---------------------------------------------------


def calibration(theme: str) -> None:
    c = THEMES[theme]
    rng = np.random.default_rng(5)
    n = 40000

    true_p = rng.beta(1.2, 1.2, size=n)
    y = rng.binomial(1, true_p)

    logit = np.log(true_p / (1 - true_p))
    overconfident = 1 / (1 + np.exp(-2.6 * logit))

    fig, ax = plt.subplots(figsize=(5.2, 4.6))
    ax.plot([0, 1], [0, 1], color=c["faint"], lw=1.4, ls=(0, (4, 3)), zorder=1, label="perfect calibration")

    for probs, colour, label in (
        (true_p, c["accent"], "well calibrated"),
        (overconfident, c["warm"], "overconfident"),
    ):
        frac, mean_pred = calibration_curve(y, probs, n_bins=10)
        ax.plot(mean_pred, frac, color=colour, lw=2.2, marker="o", ms=5, label=label, zorder=2)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_aspect("equal")
    ax.set_xlabel("predicted probability", color=c["muted"], fontsize=8)
    ax.set_ylabel("fraction that were actually positive", color=c["muted"], fontsize=8)
    ax.set_title("When the model says 0.8, is it right 80% of the time?", color=c["fg"], fontsize=10, pad=8)
    leg = ax.legend(frameon=False, fontsize=9, loc="upper left")
    for text in leg.get_texts():
        text.set_color(c["fg"])
    style_axes(ax, c)
    save(fig, f"calibration-{theme}.png")


if __name__ == "__main__":
    print("Generating probability and statistics figures")
    for theme in THEMES:
        skewed_prices(theme)
        score_variability(theme)
        fold_comparison(theme)
        calibration(theme)
    print("Done.")
