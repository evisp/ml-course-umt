#!/usr/bin/env python3
"""
Figures for docs/03-models-optimization/week-05-linear-models.md

Everything is computed on the full training month, through taxi.py, so the page
and the Week 5 lab agree (the lab samples 50,000 trips and lands within a few cents).

    python scripts/figures/week05_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/03-models-optimization/, light and dark versions of:
    w05-surface      the loss as a landscape, with the best line at its lowest point
    w05-meter        what each fit says the meter charges, against the published rate
    w05-losses       squared against absolute error, two lines on the same data
    w05-hours        what each hour adds to the fare
    w05-odds         the crawl model's coefficients, as odds multipliers
    w05-conditional  Manhattan, raw and conditioned on distance
"""

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, LogisticRegression, QuantileRegressor
from sklearn.metrics import mean_absolute_error, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "03-models-optimization"
RANDOM_STATE = 42
DPI = 200
METER = {"start": 3.00, "per_mile": 3.50, "per_minute": 0.70}

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3d5a80", "warm": "#c05d3e",
              "faint": "#cfc6b7", "soft": "#e8eaf6", "cmap": "Blues"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#8fb0d4", "warm": "#e0855f",
             "faint": "#4b5160", "soft": "#2a2f3c", "cmap": "Blues_r"},
}


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


def legend(ax, c, **kw):
    leg = ax.legend(frameon=False, fontsize=8.5, **kw)
    for t in leg.get_texts():
        t.set_color(c["fg"])


def compute(taxi):
    trips = taxi.block_2()
    train, valid, _ = taxi.splits(taxi.question_a(trips))
    r = {"train": train, "valid": valid}

    simple = LinearRegression().fit(train[["trip_distance"]], train["target"])
    r["simple"] = (simple.intercept_, simple.coef_[0])

    fast = train[train["mph"] > 12]
    fast_fit = LinearRegression().fit(fast[["trip_distance"]], fast["target"])
    r["fast"] = (fast_fit.intercept_, fast_fit.coef_[0], len(fast))

    slow = train[train["mph"] <= 12]
    slow_fit = LinearRegression().fit(slow[["trip_distance"]], slow["target"])
    r["slow"] = (slow_fit.intercept_, slow_fit.coef_[0], len(slow))

    both = LinearRegression().fit(train[["trip_distance", "minutes"]], train["target"])
    r["with_minutes"] = (both.intercept_, both.coef_[0], both.coef_[1])

    small = train.sample(8_000, random_state=RANDOM_STATE)
    squared = LinearRegression().fit(small[["trip_distance"]], small["target"])
    absolute = QuantileRegressor(quantile=0.5, alpha=0, solver="highs").fit(small[["trip_distance"]], small["target"])
    r["small"] = small
    r["squared"] = squared
    r["absolute"] = absolute
    r["loss_table"] = {
        name: {"intercept": m.intercept_, "per_mile": float(np.ravel(m.coef_)[0]),
               "mae": mean_absolute_error(valid["target"], m.predict(valid[["trip_distance"]])),
               "rmse": float(np.sqrt(np.mean((valid["target"] - m.predict(valid[["trip_distance"]])) ** 2)))}
        for name, m in [("squared", squared), ("absolute", absolute)]
    }

    full = Pipeline([
        ("prep", ColumnTransformer([
            ("numeric", Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())]),
             ["trip_distance", "airport"]),
            ("categories", OneHotEncoder(handle_unknown="ignore"), ["hour", "weekday"]),
        ])),
        ("model", LinearRegression()),
    ]).fit(train, train["target"])
    names = full.named_steps["prep"].get_feature_names_out()
    coefs = pd.Series(full.named_steps["model"].coef_, index=names)
    hourly = coefs[[c for c in names if c.startswith("categories__hour_")]]
    hourly.index = [int(c.split("_")[-1]) for c in hourly.index]
    r["hourly"] = (hourly - hourly.mean()).sort_index()
    r["full_mae"] = mean_absolute_error(valid["target"], full.predict(valid))
    r["simple_mae"] = mean_absolute_error(valid["target"], simple.predict(valid[["trip_distance"]]))
    r["n_features"] = len(names)

    crawl = taxi.question_c(trips)
    c_train, c_valid, _ = taxi.splits(crawl)
    classifier = Pipeline([
        ("prep", ColumnTransformer([
            ("numeric", StandardScaler(), ["trip_distance", "airport"]),
            ("categories", OneHotEncoder(handle_unknown="ignore"), ["hour", "pickup_borough"]),
        ])),
        ("model", LogisticRegression(max_iter=2000)),
    ]).fit(c_train, c_train["target"])
    cnames = classifier.named_steps["prep"].get_feature_names_out()
    ccoefs = pd.Series(classifier.named_steps["model"].coef_[0], index=cnames)
    wanted = {
        "picked up at 2pm": "categories__hour_14",
        "picked up at 8am": "categories__hour_8",
        "an airport trip": "numeric__airport",
        "picked up in Manhattan": "categories__pickup_borough_Manhattan",
        "picked up at 4am": "categories__hour_4",
        "one more SD of distance": "numeric__trip_distance",
    }
    r["odds"] = pd.Series({label: float(np.exp(ccoefs[key])) for label, key in wanted.items() if key in ccoefs.index})
    r["auc"] = roc_auc_score(c_valid["target"], classifier.predict_proba(c_valid)[:, 1])
    by_borough = c_train.groupby("pickup_borough").agg(trips=("target", "size"), rate=("target", "mean"))
    r["borough_raw"] = by_borough[by_borough["trips"] > 500]["rate"].sort_values()
    r["borough_coef"] = pd.Series({
        b.replace("categories__pickup_borough_", ""): float(np.exp(ccoefs[b]))
        for b in cnames if b.startswith("categories__pickup_borough_")
    })
    return r


def surface(r, theme):
    c = THEMES[theme]
    train = r["train"].sample(20_000, random_state=RANDOM_STATE)
    miles, y = train["trip_distance"].to_numpy(), train["target"].to_numpy()
    w0 = np.linspace(0, 14, 90)
    w1 = np.linspace(1.5, 6.5, 90)
    W0, W1 = np.meshgrid(w0, w1)
    loss = np.empty_like(W0)
    for i in range(W0.shape[0]):
        for j in range(W0.shape[1]):
            loss[i, j] = np.mean((y - (W0[i, j] + W1[i, j] * miles)) ** 2)

    fig, ax = plt.subplots(figsize=(7, 4.6))
    levels = np.percentile(loss, np.linspace(0.5, 80, 14))
    ax.contour(W0, W1, loss, levels=levels, colors=c["faint"], linewidths=1)
    ax.contourf(W0, W1, loss, levels=levels, cmap=c["cmap"], alpha=0.35)
    best = r["simple"]
    ax.scatter([best[0]], [best[1]], color=c["warm"], s=70, zorder=3)
    ax.annotate(f"the best line\n${best[0]:.2f} + ${best[1]:.2f}/mile", (best[0], best[1]),
                xytext=(best[0] + 1.4, best[1] + 1.1), color=c["fg"], fontsize=9,
                arrowprops=dict(arrowstyle="->", color=c["fg"], lw=1))
    ax.scatter([METER["start"]], [METER["per_mile"]], color=c["accent"], s=50, marker="s", zorder=3)
    ax.annotate("the published meter\n$3.00 + $3.50/mile", (METER["start"], METER["per_mile"]),
                xytext=(METER["start"] - 0.4, METER["per_mile"] - 1.5), color=c["muted"], fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=c["muted"], lw=1))
    ax.set_xlabel("$w_0$, the starting charge", color=c["muted"], fontsize=9)
    ax.set_ylabel("$w_1$, dollars per mile", color=c["muted"], fontsize=9)
    ax.set_title("Every point is a line. The loss says which one.", color=c["fg"], fontsize=11.5, weight="bold", loc="left")
    style(ax, c)
    save(fig, f"w05-surface-{theme}.png")


def meter(r, theme):
    c = THEMES[theme]
    rows = {
        "the published meter": (METER["start"], METER["per_mile"]),
        "fitted on all trips": r["simple"],
        "fitted on free-flowing trips": r["fast"][:2],
        "fitted on slow trips": r["slow"][:2],
    }
    labels = list(rows)
    x = np.arange(len(labels))
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 3.6), sharey=False)
    for ax, idx, title, unit in [(axes[0], 0, "The starting charge", "$"), (axes[1], 1, "Dollars per mile", "$")]:
        values = [rows[k][idx] for k in labels]
        colours = [c["accent"]] + [c["warm"] if "slow" in k else c["faint"] for k in labels[1:]]
        ax.bar(x, values, color=colours, width=0.6)
        for i, v in enumerate(values):
            ax.text(i, v + 0.08, f"{unit}{v:.2f}", ha="center", fontsize=9, color=c["fg"],
                    weight="bold" if i == 0 else "normal")
        ax.set_xticks(x)
        ax.set_xticklabels([l.replace("fitted on ", "") for l in labels], fontsize=8.5, color=c["fg"], rotation=12)
        ax.set_title(title, color=c["fg"], fontsize=11, weight="bold", loc="left")
        style(ax, c)
    fig.tight_layout(w_pad=3)
    save(fig, f"w05-meter-{theme}.png")


def losses(r, theme):
    c = THEMES[theme]
    small = r["small"]
    view = small[small["trip_distance"] < 12]
    grid = pd.DataFrame({"trip_distance": np.linspace(0, 12, 60)})
    fig, ax = plt.subplots(figsize=(7.5, 4.2))
    ax.scatter(view["trip_distance"], view["target"], s=5, alpha=0.18, color=c["faint"], linewidths=0)
    ax.plot(grid["trip_distance"], r["squared"].predict(grid), color=c["accent"], lw=2.4, label="squared error")
    ax.plot(grid["trip_distance"], r["absolute"].predict(grid), color=c["warm"], lw=2.4, label="absolute error")
    ax.set_xlabel("miles", color=c["muted"], fontsize=9)
    ax.set_ylabel("fare ($)", color=c["muted"], fontsize=9)
    ax.set_ylim(0, 60)
    ax.annotate(f"${r['loss_table']['squared']['intercept']:.2f}", (0.15, r["loss_table"]["squared"]["intercept"] + 2.2),
                color=c["accent"], fontsize=8.5)
    ax.annotate(f"${r['loss_table']['absolute']['intercept']:.2f}", (0.15, r["loss_table"]["absolute"]["intercept"] - 4.4),
                color=c["warm"], fontsize=8.5)
    legend(ax, c, loc="upper left")
    style(ax, c)
    save(fig, f"w05-losses-{theme}.png")


def hours(r, theme):
    c = THEMES[theme]
    hourly = r["hourly"]
    fig, ax = plt.subplots(figsize=(8.5, 3.2))
    ax.bar(hourly.index, hourly.values, color=[c["warm"] if v > 0 else c["accent"] for v in hourly.values])
    ax.axhline(0, color=c["fg"], lw=1)
    ax.set_xlabel("hour of pickup", color=c["muted"], fontsize=9)
    ax.set_ylabel("dollars added", color=c["muted"], fontsize=9)
    ax.set_xticks(range(0, 24, 2))
    style(ax, c)
    save(fig, f"w05-hours-{theme}.png")


def odds(r, theme):
    c = THEMES[theme]
    s = r["odds"].sort_values()
    fig, ax = plt.subplots(figsize=(7.5, 3.4))
    ax.barh(s.index, s.values, color=[c["warm"] if v > 1 else c["accent"] for v in s.values], height=0.6)
    ax.axvline(1, color=c["fg"], ls=(0, (4, 3)), lw=1.2)
    for i, v in enumerate(s.values):
        ax.text(v + 0.05, i, f"×{v:.2f}", va="center", fontsize=8.5, color=c["fg"])
    ax.set_xlabel("multiplier on the odds of crawling", color=c["muted"], fontsize=9)
    ax.set_xlim(0, max(s.values) * 1.25)
    ax.tick_params(axis="y", colors=c["fg"], labelsize=9)
    style(ax, c)
    save(fig, f"w05-odds-{theme}.png")


def conditional(r, theme):
    c = THEMES[theme]
    raw, coef = r["borough_raw"], r["borough_coef"]
    shared = [b for b in raw.index if b in coef.index]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4))
    axes[0].barh(shared, [raw[b] for b in shared], color=c["warm"], height=0.6)
    for i, b in enumerate(shared):
        axes[0].text(raw[b] + 0.004, i, f"{raw[b]:.1%}", va="center", fontsize=8.5, color=c["fg"])
    axes[0].set_xlabel("share of trips that crawl", color=c["muted"], fontsize=9)
    axes[0].set_title("On its own", color=c["fg"], fontsize=11, weight="bold", loc="left")
    axes[0].set_xlim(0, max(raw[b] for b in shared) * 1.3)

    axes[1].barh(shared, [coef[b] for b in shared], color=[c["warm"] if coef[b] > 1 else c["accent"] for b in shared], height=0.6)
    axes[1].axvline(1, color=c["fg"], ls=(0, (4, 3)), lw=1.2)
    for i, b in enumerate(shared):
        axes[1].text(coef[b] + 0.02, i, f"×{coef[b]:.2f}", va="center", fontsize=8.5, color=c["fg"])
    axes[1].set_xlabel("odds multiplier, with distance in the model", color=c["muted"], fontsize=9)
    axes[1].set_title("Inside the model", color=c["fg"], fontsize=11, weight="bold", loc="left")
    for ax in axes:
        ax.tick_params(axis="y", colors=c["fg"], labelsize=9)
        style(ax, c)
    fig.tight_layout(w_pad=3)
    save(fig, f"w05-conditional-{theme}.png")


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
    r = compute(taxi)
    print(f"  all trips:      ${r['simple'][0]:.2f} + ${r['simple'][1]:.2f}/mile")
    print(f"  free-flowing:   ${r['fast'][0]:.2f} + ${r['fast'][1]:.2f}/mile   (n={r['fast'][2]:,})")
    print(f"  slow:           ${r['slow'][0]:.2f} + ${r['slow'][1]:.2f}/mile   (n={r['slow'][2]:,})")
    print(f"  with minutes:   ${r['with_minutes'][0]:.2f} + ${r['with_minutes'][1]:.2f}/mile + ${r['with_minutes'][2]:.2f}/min")
    print(f"  losses: {pd.DataFrame(r['loss_table']).T.round(2).to_dict('index')}")
    print(f"  full model: {r['n_features']} features, valid MAE {r['simple_mae']:.2f} -> {r['full_mae']:.2f}")
    print(f"  crawl model: AUC {r['auc']:.3f}")
    print(f"  odds: {r['odds'].round(2).to_dict()}")
    print(f"  borough raw: {r['borough_raw'].round(3).to_dict()}")
    print(f"  borough coef: {r['borough_coef'].round(2).to_dict()}")

    print("Generating Week 5 figures")
    for theme in THEMES:
        surface(r, theme)
        meter(r, theme)
        losses(r, theme)
        hours(r, theme)
        odds(r, theme)
        conditional(r, theme)
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
