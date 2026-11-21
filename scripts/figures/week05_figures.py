#!/usr/bin/env python3
"""
Figures for docs/03-models-optimization/week-05-linear-models.md

Everything is computed through hotels.py on the full training split, so the
page and the Week 5 lab agree (the lab samples 20,000 bookings a split and
lands within a euro or two).

    python scripts/figures/week05_figures.py --labs ../ml-course-labs

Outputs into docs/assets/images/03-models-optimization/, light and dark versions of:
    w05-surface       the loss as a landscape, with the best line at its lowest point
    w05-guests        the simplest shape there is, fitted
    w05-losses        squared against absolute error, and what one outlier does
    w05-coefficients  what the readable model says each thing is worth, in euros
    w05-season        why one month coefficient is wrong for both hotels
    w05-odds          the cancellation model's coefficients, as odds multipliers
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
from sklearn.metrics import average_precision_score, mean_absolute_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "03-models-optimization"
RANDOM_STATE = 42
DPI = 200
OUTLIER = 5400.0          # the one booking daily_rate() leaves out

NUM = ["lead_time", "total_nights", "adults", "children", "total_of_special_requests"]
CAT = ["hotel", "arrival_month", "market_segment", "reserved_room_type"]
CNUM = ["lead_time", "total_nights", "previous_cancellations",
        "total_of_special_requests", "is_repeated_guest"]
CCAT = ["hotel", "deposit_type", "market_segment", "customer_type"]

THEMES = {
    "light": {"fg": "#21252e", "muted": "#6b7280", "accent": "#3d5a80", "warm": "#c05d3e",
              "faint": "#cfc6b7", "soft": "#e8eaf6", "cmap": "Blues_r"},
    "dark": {"fg": "#e5e7ef", "muted": "#9aa1b1", "accent": "#8fb0d4", "warm": "#e0855f",
             "faint": "#4b5160", "soft": "#2a2f3c", "cmap": "Blues"},
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


def euros(ax, axis="y"):
    getattr(ax, f"{axis}axis").set_major_formatter(
        plt.FuncFormatter(lambda v, _: f"€{v:,.0f}"))


# ---------------------------------------------------------------------------


def compute(hotels):
    df = hotels.block_2()
    rate, cancel = hotels.daily_rate(df), hotels.cancellation(df)
    rtr, rva, _ = hotels.splits(rate)
    ctr, cva, _ = hotels.splits(cancel)
    r = {"rtr": rtr, "rva": rva, "ctr": ctr, "cva": cva}

    simple = LinearRegression().fit(rtr[["total_guests"]], rtr["target"])
    r["simple"] = (float(simple.intercept_), float(simple.coef_[0]))
    p = simple.predict(rva[["total_guests"]])
    r["simple_scores"] = (r2_score(rva["target"], p),
                          mean_absolute_error(rva["target"], p))

    readable = Pipeline([
        ("p", ColumnTransformer([
            ("num", SimpleImputer(strategy="median"), NUM),
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CAT)])),
        ("m", LinearRegression())]).fit(rtr[NUM + CAT], rtr["target"])
    names = [n.split("__", 1)[1] for n in readable[:-1].get_feature_names_out()]
    r["coefs"] = pd.Series(readable[-1].coef_, index=names)
    r["intercept"] = float(readable[-1].intercept_)
    p = readable.predict(rva[NUM + CAT])
    r["readable_scores"] = (r2_score(rva["target"], p),
                            mean_absolute_error(rva["target"], p))

    r["season"] = rtr.pivot_table(index="arrival_month", columns="hotel",
                                  values="target", aggfunc="mean")

    logistic = Pipeline([
        ("p", ColumnTransformer([
            ("num", Pipeline([("i", SimpleImputer(strategy="median")),
                              ("s", StandardScaler())]), CNUM),
            ("cat", OneHotEncoder(handle_unknown="ignore", drop="first"), CCAT)])),
        ("m", LogisticRegression(max_iter=3000))]).fit(ctr[CNUM + CCAT], ctr["target"])
    cnames = [n.split("__", 1)[1] for n in logistic[:-1].get_feature_names_out()]
    r["odds"] = pd.Series(np.exp(logistic[-1].coef_[0]), index=cnames)
    r["sd"] = ctr[CNUM].std()
    s = logistic.predict_proba(cva[CNUM + CCAT])[:, 1]
    ap = average_precision_score(cva["target"], s)
    r["logistic_scores"] = (ap, ap / cva["target"].mean())

    alone = Pipeline([
        ("p", ColumnTransformer([("c", OneHotEncoder(drop="first"), ["deposit_type"])])),
        ("m", LogisticRegression(max_iter=1000))]).fit(ctr[["deposit_type"]], ctr["target"])
    an = [n.split("__", 1)[1] for n in alone[:-1].get_feature_names_out()]
    r["alone"] = dict(zip(an, np.exp(alone[-1].coef_[0])))
    return r


# ---------------------------------------------------------------------------


def surface(r, theme):
    """The loss as a landscape over the two numbers in the simplest model."""
    c = THEMES[theme]
    sub = r["rtr"].sample(6000, random_state=RANDOM_STATE)
    x = sub["total_guests"].to_numpy(float)
    y = sub["target"].to_numpy(float)
    b0, b1 = r["simple"]

    w0 = np.linspace(b0 - 45, b0 + 45, 90)
    w1 = np.linspace(b1 - 22, b1 + 22, 90)
    W0, W1 = np.meshgrid(w0, w1)
    loss = np.empty_like(W0)
    for i in range(W0.shape[0]):
        pred = W0[i][:, None] + W1[i][:, None] * x[None, :]
        loss[i] = ((pred - y[None, :]) ** 2).mean(axis=1)

    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    levels = np.percentile(loss, np.linspace(0, 85, 18))
    ax.contourf(W0, W1, loss, levels=levels, cmap=c["cmap"], alpha=0.9)
    ax.contour(W0, W1, loss, levels=levels, colors=c["faint"], linewidths=0.4)
    ax.plot([b0], [b1], marker="o", ms=9, color=c["warm"], zorder=5)
    ax.annotate(f"  the fit:  €{b0:.0f} + €{b1:.0f} a guest",
                (b0, b1), textcoords="offset points", xytext=(8, -20),
                fontsize=9, color=c["warm"], weight="bold")
    ax.set_xlabel("w₀, the euros every booking starts at", fontsize=9, color=c["muted"])
    ax.set_ylabel("w₁, the euros each guest adds", fontsize=9, color=c["muted"])
    style(ax, c)
    save(fig, f"w05-surface-{theme}.png")


def guests(r, theme):
    c = THEMES[theme]
    sub = r["rtr"].sample(4000, random_state=RANDOM_STATE)
    b0, b1 = r["simple"]
    fig, ax = plt.subplots(figsize=(7.4, 3.6))
    jitter = np.random.default_rng(0).normal(0, 0.06, len(sub))
    ax.scatter(sub["total_guests"] + jitter, sub["target"], s=4, alpha=0.12,
               color=c["accent"], linewidths=0)
    grid = np.linspace(0.6, float(sub["total_guests"].max()) + 0.4, 50)
    ax.plot(grid, b0 + b1 * grid, color=c["warm"], lw=2.4,
            label=f"€{b0:.2f} + €{b1:.2f} a guest")
    ax.set_xlabel("guests in the booking", fontsize=9, color=c["muted"])
    ax.set_ylabel("euros a night", fontsize=9, color=c["muted"])
    ax.set_ylim(0, 320)
    euros(ax)
    style(ax, c)
    legend(ax, c, loc="upper left")
    save(fig, f"w05-guests-{theme}.png")


def losses(r, theme):
    """One booking at EUR 5,400 moves one fit and not the other."""
    c = THEMES[theme]
    sub = r["rtr"].sample(4000, random_state=0)
    x = sub[["total_guests"]].to_numpy(float)
    y = sub["target"].to_numpy(float)
    fits = {}
    for label, (X, Y) in (("clean", (x, y)),
                          ("outlier", (np.vstack([x, [[2.0]]]), np.append(y, OUTLIER)))):
        ls = LinearRegression().fit(X, Y)
        qr = QuantileRegressor(quantile=0.5, alpha=0, solver="highs").fit(X, Y)
        fits[label] = {"squared": (float(ls.intercept_), float(ls.coef_[0])),
                       "absolute": (float(qr.intercept_), float(qr.coef_[0]))}

    grid = np.linspace(0.6, 4.4, 40)
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.5), sharey=True)
    for ax, label, title in zip(axes, ("clean", "outlier"),
                                ("4,000 bookings",
                                 f"the same, plus one at €{OUTLIER:,.0f}")):
        jitter = np.random.default_rng(0).normal(0, 0.06, len(sub))
        ax.scatter(sub["total_guests"] + jitter, y, s=4, alpha=0.10,
                   color=c["faint"], linewidths=0)
        for name, colour, dash in (("squared", c["warm"], None),
                                   ("absolute", c["accent"], (0, (5, 3)))):
            w0, w1 = fits[label][name]
            ax.plot(grid, w0 + w1 * grid, color=colour, lw=2.2, ls=dash or "-",
                    label=f"{name}: €{w0:.0f} + €{w1:.0f}/guest")
        ax.set_title(title, fontsize=9.5, color=c["fg"])
        ax.set_xlabel("guests", fontsize=9, color=c["muted"])
        ax.set_ylim(0, 240)
        style(ax, c)
        legend(ax, c, loc="upper left")
    axes[0].set_ylabel("euros a night", fontsize=9, color=c["muted"])
    euros(axes[0])
    moved = abs(fits["outlier"]["squared"][0] - fits["clean"]["squared"][0])
    axes[1].text(0.62, 10, f"squared moved €{moved:.2f}; absolute did not move at all",
                 fontsize=8.5, color=c["muted"])
    fig.tight_layout()
    save(fig, f"w05-losses-{theme}.png")


def coefficients(r, theme):
    c = THEMES[theme]
    labels = {"adults": "one more adult", "children": "one more child",
              "total_of_special_requests": "one more special request",
              "total_nights": "one more night", "lead_time": "one more day ahead",
              "hotel_Resort Hotel": "the resort, not the city",
              "arrival_month_8": "arriving in August",
              "arrival_month_11": "arriving in November",
              "reserved_room_type_H": "room type H",
              "market_segment_Complementary": "a complimentary booking"}
    values = r["coefs"].reindex(labels).dropna().sort_values()

    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    colours = [c["warm"] if v < 0 else c["accent"] for v in values]
    ax.barh(range(len(values)), values, color=colours, height=0.62)
    for i, v in enumerate(values):
        ax.text(v + (1.8 if v >= 0 else -1.8), i, f"€{v:+.2f}", va="center",
                ha="left" if v >= 0 else "right", fontsize=8.5, color=c["fg"])
    ax.axvline(0, color=c["faint"], lw=1)
    ax.set_yticks(range(len(values)))
    ax.set_yticklabels([labels[i] for i in values.index], fontsize=9, color=c["fg"])
    ax.set_xlabel("euros a night, holding everything else still", fontsize=9, color=c["muted"])
    ax.set_xlim(values.min() - 26, values.max() + 26)
    euros(ax, "x")
    style(ax, c)
    save(fig, f"w05-coefficients-{theme}.png")


def season(r, theme):
    c = THEMES[theme]
    s = r["season"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    offsets = pd.Series(
        [0.0] + [float(r["coefs"].get(f"arrival_month_{m}", 0.0)) for m in range(2, 13)],
        index=s.index)
    pooled = offsets - offsets.mean() + float(s.mean(axis=1).mean())

    fig, ax = plt.subplots(figsize=(7.8, 3.6))
    ax.plot(s.index, s["Resort Hotel"], color=c["warm"], lw=2.4, marker="o", ms=4,
            label="resort, what it actually charges")
    ax.plot(s.index, s["City Hotel"], color=c["accent"], lw=2.4, marker="o", ms=4,
            label="city, what it actually charges")
    ax.plot(s.index, pooled, color=c["muted"], lw=2, ls=(0, (5, 3)),
            label="one month coefficient, used for both")
    for month, dy in ((8, 6), (11, -17)):
        ax.annotate(f"€{s.loc[month, 'Resort Hotel']:.0f}",
                    (month, s.loc[month, "Resort Hotel"]), textcoords="offset points",
                    xytext=(5, dy), fontsize=9, color=c["warm"], weight="bold")
    ax.set_xticks(range(1, 13))
    ax.set_xticklabels(months, fontsize=8.5, color=c["fg"])
    ax.set_ylabel("euros a night", fontsize=9, color=c["muted"])
    euros(ax)
    style(ax, c)
    legend(ax, c, loc="upper left")
    save(fig, f"w05-season-{theme}.png")


def odds(r, theme):
    c = THEMES[theme]
    labels = {"deposit_type_Non Refund": "non-refundable",
              "previous_cancellations": "one more past cancellation",
              "market_segment_Online TA": "booked through an online agent",
              "customer_type_Transient": "a transient customer",
              "lead_time": f"{r['sd']['lead_time']:.0f} more days ahead",
              "total_nights": f"{r['sd']['total_nights']:.1f} more nights",
              "hotel_Resort Hotel": "the resort, not the city",
              "market_segment_Corporate": "booked by a company",
              "total_of_special_requests": "one more special request",
              "is_repeated_guest": "a returning guest"}
    values = r["odds"].reindex(labels).dropna().sort_values()
    floor = 0.01
    shown = values.clip(lower=floor)

    fig, ax = plt.subplots(figsize=(7.8, 4.0))
    colours = [c["warm"] if v > 1 else c["accent"] for v in values]
    ax.barh(range(len(shown)), shown, color=colours, height=0.62)
    ax.set_xscale("log")
    ax.axvline(1, color=c["faint"], lw=1.2)
    ax.text(1.06, len(shown) - 0.35, "no change", fontsize=8.5, color=c["muted"])
    for i, v in enumerate(values):
        ax.text(max(shown.iloc[i], floor) * 1.3, i,
                f"×{v:,.2f}" if v >= 0.01 else "×0.00",
                va="center", fontsize=8.5, color=c["fg"])
    ax.set_yticks(range(len(shown)))
    ax.set_yticklabels([labels[i] for i in values.index], fontsize=9, color=c["fg"])
    ax.set_xlabel("what it multiplies the odds of cancelling by", fontsize=9, color=c["muted"])
    ax.set_xlim(floor, 1200)
    style(ax, c)
    save(fig, f"w05-odds-{theme}.png")


# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--labs", default=str(ROOT.parent / "ml-course-labs"))
    args = parser.parse_args()
    labs = Path(args.labs).expanduser().resolve()
    if not (labs / "hotels.py").exists():
        print(f"Cannot find hotels.py in {labs}. Pass --labs /path/to/ml-course-labs",
              file=sys.stderr)
        return 1
    sys.path.insert(0, str(labs))
    import hotels

    OUT.mkdir(parents=True, exist_ok=True)
    print("Loading data from", labs)
    r = compute(hotels)

    b0, b1 = r["simple"]
    print(f"  one feature:   EUR {b0:.2f} + EUR {b1:.2f} a guest   "
          f"valid R2 {r['simple_scores'][0]:.3f}  MAE EUR {r['simple_scores'][1]:.2f}")
    print(f"  readable:      intercept EUR {r['intercept']:.2f}   "
          f"valid R2 {r['readable_scores'][0]:.3f}  MAE EUR {r['readable_scores'][1]:.2f}")
    print(f"  logistic:      PR AUC {r['logistic_scores'][0]:.3f}  "
          f"lift {r['logistic_scores'][1]:.2f}")
    print(f"  non-refundable odds: x{r['alone']['deposit_type_Non Refund']:.2f} alone, "
          f"x{r['odds']['deposit_type_Non Refund']:.2f} in the model")
    print(f"  resort August EUR {r['season'].loc[8, 'Resort Hotel']:.0f} vs "
          f"November EUR {r['season'].loc[11, 'Resort Hotel']:.0f}")

    for theme in ("light", "dark"):
        surface(r, theme)
        guests(r, theme)
        losses(r, theme)
        coefficients(r, theme)
        season(r, theme)
        odds(r, theme)
    return 0


if __name__ == "__main__":
    sys.exit(main())
