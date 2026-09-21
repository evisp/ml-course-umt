#!/usr/bin/env python3
"""
Figures for docs/06-reference/calculus.md

Run from the repository root:

    python scripts/figures/calculus_figures.py

Outputs into docs/assets/images/06-reference/:
    learning-rate-{light,dark}.png
    scaling-contours-{light,dark}.png
    convexity-{light,dark}.png

Every descent path is produced by actually running gradient descent,
not drawn by hand.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

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


# --- Figure 1: three learning rates on one parabola --------------------------


def learning_rate(theme: str) -> None:
    c = THEMES[theme]

    def f(w):
        return w**2

    def grad(w):
        return 2 * w

    runs = [
        ("Too small", 0.05, 10),
        ("About right", 0.3, 6),
        ("Too large", 1.05, 7),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.3))

    for ax, (title, lr, steps) in zip(axes, runs):
        w = 4.0
        path = [w]
        for _ in range(steps):
            w = w - lr * grad(w)
            path.append(w)
        path = np.array(path)

        span = max(5.0, np.abs(path).max() * 1.1)
        grid = np.linspace(-span, span, 300)
        ax.plot(grid, f(grid), color=c["faint"], lw=2, zorder=1)

        colour = c["warm"] if title == "Too large" else c["accent"]
        ax.plot(path, f(path), color=colour, lw=1.3, alpha=0.7, zorder=2)
        ax.scatter(path, f(path), color=colour, s=26, zorder=3)
        ax.scatter([path[0]], [f(path[0])], color=c["fg"], s=40, zorder=4, marker="o")

        ax.set_title(f"{title}\nlearning rate {lr}", color=c["fg"], fontsize=10, pad=8)
        ax.set_xlim(-span, span)
        ax.set_ylim(-0.05 * span**2, span**2 * 1.05)
        ax.set_xlabel("weight", color=c["muted"], fontsize=8)
        style_axes(ax, c)

    axes[0].set_ylabel("loss", color=c["muted"], fontsize=8)
    fig.tight_layout(w_pad=2.5)
    save(fig, f"learning-rate-{theme}.png")


# --- Figure 2: well scaled versus badly scaled loss surfaces -----------------


def scaling_contours(theme: str) -> None:
    c = THEMES[theme]

    def descend(a, b, lr, start, steps):
        w = np.array(start, dtype=float)
        path = [w.copy()]
        for _ in range(steps):
            g = np.array([2 * a * w[0], 2 * b * w[1]])
            w = w - lr * g
            path.append(w.copy())
        return np.array(path)

    cases = [
        ("Features on similar scales", 1.0, 1.0, 0.2, 12),
        ("One feature 20× larger", 1.0, 20.0, 0.9 / 20.0, 30),
    ]
    start = (-4.0, 2.4)

    fig, axes = plt.subplots(1, 2, figsize=(10.0, 4.0))
    g1, g2 = np.meshgrid(np.linspace(-5, 5, 300), np.linspace(-3.2, 3.2, 300))

    for ax, (title, a, b, lr, steps) in zip(axes, cases):
        Z = a * g1**2 + b * g2**2
        levels = np.quantile(Z, np.linspace(0.02, 0.9, 9))
        ax.contour(g1, g2, Z, levels=levels, colors=c["faint"], linewidths=1.1)

        path = descend(a, b, lr, start, steps)
        colour = c["accent"] if b == 1.0 else c["warm"]
        ax.plot(path[:, 0], path[:, 1], color=colour, lw=1.6, zorder=2)
        ax.scatter(path[:, 0], path[:, 1], color=colour, s=14, zorder=3)
        ax.scatter([0], [0], color=c["fg"], marker="*", s=120, zorder=4)

        ax.set_title(f"{title}\n{steps} steps", color=c["fg"], fontsize=10, pad=8)
        ax.set_xlim(-5, 5)
        ax.set_ylim(-3.2, 3.2)
        ax.set_aspect("equal")
        ax.set_xticks([])
        ax.set_yticks([])
        for side in ax.spines:
            ax.spines[side].set_visible(False)

    fig.tight_layout(w_pad=3)
    save(fig, f"scaling-contours-{theme}.png")


# --- Figure 3: convex versus non-convex --------------------------------------


def convexity(theme: str) -> None:
    c = THEMES[theme]

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4))

    # Convex bowl
    x = np.linspace(-3, 3, 300)
    y = x**2
    ax = axes[0]
    ax.plot(x, y, color=c["accent"], lw=2.2)
    ax.scatter([0], [0], color=c["fg"], marker="*", s=130, zorder=3)
    ax.text(0, 1.1, "one minimum", color=c["muted"], fontsize=9, ha="center")
    ax.set_title("Convex\nlinear and logistic regression", color=c["fg"], fontsize=10, pad=8)

    # Non-convex curve with a local trap
    x = np.linspace(-2.6, 2.4, 400)
    y = 0.5 * x**4 - 2 * x**2 + 0.6 * x + 2.5
    ax = axes[1]
    ax.plot(x, y, color=c["warm"], lw=2.2)

    xs = np.linspace(-2.6, 2.4, 4000)
    ys = 0.5 * xs**4 - 2 * xs**2 + 0.6 * xs + 2.5
    left = xs < 0
    gx = xs[left][np.argmin(ys[left])]
    lx = xs[~left][np.argmin(ys[~left])]
    gy = 0.5 * gx**4 - 2 * gx**2 + 0.6 * gx + 2.5
    ly = 0.5 * lx**4 - 2 * lx**2 + 0.6 * lx + 2.5

    ax.scatter([gx], [gy], color=c["fg"], marker="*", s=130, zorder=3)
    ax.scatter([lx], [ly], color=c["warm"], s=55, zorder=3, edgecolor=c["fg"], linewidth=0.8)
    ax.text(gx + 0.28, gy + 0.05, "global minimum", color=c["muted"], fontsize=9, ha="left", va="center")
    ax.text(lx, ly - 0.75, "local trap", color=c["muted"], fontsize=9, ha="center")
    ax.set_title("Not convex\nneural networks", color=c["fg"], fontsize=10, pad=8)

    for ax in axes:
        ax.set_xticks([])
        ax.set_yticks([])
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(c["faint"])
        ax.set_xlabel("weight", color=c["muted"], fontsize=8)
        ax.set_ylabel("loss", color=c["muted"], fontsize=8)

    fig.tight_layout(w_pad=3)
    save(fig, f"convexity-{theme}.png")


if __name__ == "__main__":
    print("Generating calculus figures")
    for theme in THEMES:
        learning_rate(theme)
        scaling_contours(theme)
        convexity(theme)
    print("Done.")
