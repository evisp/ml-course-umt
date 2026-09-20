#!/usr/bin/env python3
"""
Figures for docs/06-reference/linear-algebra.md

Generates light and dark variants of each figure so the page works with the
Material theme's colour scheme toggle (via the #only-light / #only-dark hints).

Run from the repository root:

    python scripts/figures/linear_algebra_figures.py

Outputs into docs/assets/images/06-reference/:
    projection-light.png   projection-dark.png
    pca-axes-light.png     pca-axes-dark.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

# --- Where the images go -----------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "06-reference"
OUT.mkdir(parents=True, exist_ok=True)

# --- Theme palettes ----------------------------------------------------------

THEMES = {
    "light": {
        "fg": "#21252e",
        "muted": "#6b7280",
        "accent": "#3f51b5",
        "warm": "#e07b39",
        "faint": "#c9cdd6",
    },
    "dark": {
        "fg": "#e5e7ef",
        "muted": "#9aa1b1",
        "accent": "#9fa8da",
        "warm": "#f0a868",
        "faint": "#4b5160",
    },
}

DPI = 200


def save(fig, name: str) -> None:
    path = OUT / name
    fig.savefig(path, dpi=DPI, transparent=True, bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"  wrote {path.relative_to(ROOT)}")


# --- Figure 1: least squares as a projection ---------------------------------


def projection(theme: str) -> None:
    c = THEMES[theme]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))

    # The subspace the model can reach: a line through the origin.
    direction = np.array([1.0, 0.35])
    direction = direction / np.linalg.norm(direction)
    t = np.linspace(-0.6, 4.6, 2)
    line = np.outer(t, direction)
    ax.plot(line[:, 0], line[:, 1], color=c["faint"], lw=2.2, zorder=1)

    # The target vector y, and its projection onto that line.
    y = np.array([3.1, 2.9])
    y_hat = np.dot(y, direction) * direction

    arrow = dict(lw=2.2, length_includes_head=True, head_width=0.13, head_length=0.2)

    ax.arrow(0, 0, y[0], y[1], color=c["warm"], zorder=3, **arrow)
    ax.arrow(0, 0, y_hat[0], y_hat[1], color=c["accent"], zorder=3, **arrow)
    ax.plot(
        [y_hat[0], y[0]],
        [y_hat[1], y[1]],
        color=c["muted"],
        lw=1.6,
        ls=(0, (4, 3)),
        zorder=2,
    )

    # Right-angle marker where the residual meets the subspace.
    perp = np.array([-direction[1], direction[0]])
    size = 0.22
    corner = y_hat
    square = np.array(
        [corner, corner + direction * size, corner + direction * size + perp * size, corner + perp * size]
    )
    ax.plot(square[:, 0], square[:, 1], color=c["muted"], lw=1.2, zorder=2)

    ax.text(y[0] + 0.14, y[1] + 0.02, r"$\mathbf{y}$", color=c["warm"], fontsize=14, weight="bold")
    ax.text(
        y_hat[0] * 0.55,
        y_hat[1] * 0.55 - 0.42,
        r"$\hat{\mathbf{y}} = X\mathbf{w}$",
        color=c["accent"],
        fontsize=13,
        weight="bold",
        ha="center",
    )
    ax.text(
        (y_hat[0] + y[0]) / 2 + 0.18,
        (y_hat[1] + y[1]) / 2,
        "residual",
        color=c["muted"],
        fontsize=11,
        style="italic",
    )
    ax.text(
        4.55,
        1.42,
        "column space of $X$\n(every prediction\nthe model can make)",
        color=c["muted"],
        fontsize=10,
        ha="left",
        va="center",
    )

    ax.set_xlim(-0.7, 7.6)
    ax.set_ylim(-1.1, 3.6)
    ax.set_aspect("equal")
    ax.axis("off")

    save(fig, f"projection-{theme}.png")


# --- Figure 2: principal directions from the SVD -----------------------------


def pca_axes(theme: str) -> None:
    c = THEMES[theme]
    rng = np.random.default_rng(7)

    n = 320
    base = rng.normal(size=(n, 2)) @ np.array([[2.3, 0.0], [0.0, 0.6]])
    angle = np.deg2rad(30)
    rot = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
    X = base @ rot.T

    X_centred = X - X.mean(axis=0)
    _, S, Vt = np.linalg.svd(X_centred, full_matrices=False)

    # Singular vector signs are arbitrary. Orient both to point right, so the
    # arrows agree with the visible trend of the data.
    components = np.array([v if v[0] >= 0 else -v for v in Vt])
    spread = S / np.sqrt(n)

    fig, ax = plt.subplots(figsize=(6.0, 4.2))
    ax.scatter(X_centred[:, 0], X_centred[:, 1], s=13, color=c["faint"], alpha=0.9, zorder=1)

    pct = S**2 / np.sum(S**2) * 100
    labels = [f"PC1  ({pct[0]:.0f}% of variance)", f"PC2  ({pct[1]:.0f}%)"]
    colors = [c["accent"], c["warm"]]
    offsets = [(0.35, -0.45), (0.25, 0.4)]

    for i in range(2):
        length = max(spread[i] * 2.3, 0.9)   # keep PC2 visible even when short
        v = components[i] * length
        ax.annotate(
            "",
            xy=(v[0], v[1]),
            xytext=(0, 0),
            arrowprops=dict(arrowstyle="-|>", color=colors[i], lw=2.6, mutation_scale=20),
            zorder=3,
        )
        ax.text(
            v[0] + offsets[i][0],
            v[1] + offsets[i][1],
            labels[i],
            color=colors[i],
            fontsize=11,
            weight="bold",
            ha="left",
            va="center",
        )

    x_pad, y_pad = 1.0, 0.9
    ax.set_xlim(X_centred[:, 0].min() - x_pad, X_centred[:, 0].max() + x_pad * 3.4)
    ax.set_ylim(X_centred[:, 1].min() - y_pad, X_centred[:, 1].max() + y_pad)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")

    save(fig, f"pca-axes-{theme}.png")


# --- Run ---------------------------------------------------------------------

if __name__ == "__main__":
    print("Generating linear algebra figures")
    for theme in THEMES:
        projection(theme)
        pca_axes(theme)
    print("Done.")
