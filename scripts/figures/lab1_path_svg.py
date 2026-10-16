"""Week 1 lecture graphic: "One question, six moves".

Builds two SVGs with identical geometry:

    lab1-questions.svg   the questions, to show at the start of the session
    lab1-answers.svg     the same frame filled in, to show at the end

Usage:
    python scripts/figures/lab1_path_svg.py                 # writes both SVGs
    python scripts/figures/lab1_path_svg.py --png           # also writes PNGs

The shell -- palette, canvas, header, path, footer -- lives in lecture_svg.py
and is shared with the other weeks. Everything below is Week 1's own content,
and every number in it comes from checkpoints.week_01 and the Week 1 notebook.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import lecture_svg as L
from lecture_svg import (
    BAR_H, BAR_ROWS, M, W, H, Y_BAND3_LABEL,
    band_header, band_path, document, footer, line, rect, text, verdict,
    write_pair,
)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "docs" / "assets" / "images" / "lecture" / "week-01"

# ---------------------------------------------------------------------------
# this week's scoreboard geometry
# ---------------------------------------------------------------------------

ACC_X, ACC_W = 436, 400
PR_X, PR_W = 1022, 400
PR_MAX = 0.15

# ---------------------------------------------------------------------------
# content
# ---------------------------------------------------------------------------

KICKER = "MACHINE LEARNING @ UMT  ·  WEEK 1  ·  PROBLEM FRAMING"

HEAD = {
    "questions": [
        ("Can we use AI to reduce late deliveries?", 46, "slate", "bold"),
        ("A wish. Not yet a question a model can answer.", 26, "muted", "regular"),
    ],
    "answers": [
        ("At the moment an order is placed, predict whether it", 42, "ink", "bold"),
        ("will arrive after the date promised to the customer.", 42, "ink", "bold"),
    ],
}

CHIPS = [
    ("MOMENT", "at purchase", "?"),
    ("TARGET", "later than promised", "?"),
    ("UNIT", "one order", "?"),
    ("ACTION", "flag the riskiest", "?"),
]

# title, question (version A), payload (version B), caption (version B)
STOPS = [
    (
        "Load",
        ["What's missing?"],
        ("2,965", None),
        ["orders with no", "delivery date at all"],
    ),
    (
        "Define",
        ["When is an", "order late?"],
        ("1,291", None),
        ["orders change label", "on one comparison"],
    ),
    (
        "Settle",
        ["Which orders", "can we label?"],
        ("96,204", None),
        ["usable orders,", "6.8% of them late"],
    ),
    (
        "Look",
        ["Where does lateness", "concentrate?"],
        ("3%", "19%"),
        ["by month · and the", "far north is best"],
    ),
    (
        "Ladder",
        ["What does a model", "have to beat?"],
        ("0.068", "0.102"),
        ["PR AUC, chance to", "the best baseline"],
    ),
    (
        "Write it down",
        ["Can you write", "all of it down?"],
        ("PROBLEM.md", None),
        ["the one artefact", "Week 2 starts from"],
    ),
]

BRACKET = {
    "questions": "Does the wording change the answer?",
    "answers": "one wording choice moved the rate from 8.1% to 6.8% late",
}

SPUR = {
    "questions": ("A DEAD END", "What if we just use", "the delivery time?", "?"),
    "answers": ("A DEAD END", "knows the delivery time ·", "impossible at purchase", "0.896"),
}

BARS = [
    ("Always say “on time”", 0.932, 0.068),
    ("Rule: high-risk states", 0.758, 0.102),
    ("Depth-2 decision tree", 0.753, 0.102),
]

VERDICT = {
    "questions": "Which of these three is the best model?",
    "answers": "The one with the best accuracy has no skill at all. Accuracy ranks them upside down.",
}

FOOTER_LEFT = (
    "Olist Brazilian e-commerce · 96,204 delivered orders · "
    "January 2017 to August 2018"
)
FOOTER_RIGHT = "ml-course-umt · Week 1 · Problem framing"


# ---------------------------------------------------------------------------
# the scoreboard: accuracy against PR AUC, on the same three baselines
# ---------------------------------------------------------------------------


def band_score(version: str) -> list[str]:
    known = version == "answers"
    p: list[str] = []
    top = BAR_ROWS[0] - 64
    p.append(rect(M, top, W - 2 * M, BAR_ROWS[-1] + 36 - top, L.PLATE, None, r=14))

    p.append(text(M + 26, Y_BAND3_LABEL, "THE SCOREBOARD", 16, L.FAINT, "bold", tracking=2.4))
    p.append(text(ACC_X, Y_BAND3_LABEL, "ACCURACY", 15, L.MUTED, "bold", tracking=1.8))
    p.append(text(ACC_X + ACC_W + 12, Y_BAND3_LABEL, "scale 0 to 1", 14, L.FAINT))
    p.append(text(PR_X, Y_BAND3_LABEL, "PR AUC", 15, L.MUTED, "bold", tracking=1.8))
    p.append(text(PR_X + PR_W + 12, Y_BAND3_LABEL, "scale 0 to 0.15", 14, L.FAINT))

    cx = PR_X + PR_W * (0.068 / PR_MAX)
    if known:
        # everything left of this line is what you get by guessing
        p.append(rect(PR_X, BAR_ROWS[0] - BAR_H / 2 - 6, cx - PR_X,
                      BAR_ROWS[-1] - BAR_ROWS[0] + BAR_H + 12, L.ACCENT_TINT, None, r=6))
        p.append(line(cx, BAR_ROWS[0] - BAR_H / 2 - 10, cx, BAR_ROWS[-1] + BAR_H / 2 + 10,
                      L.ACCENT, 2, dash="5 5"))
        p.append(text(cx, BAR_ROWS[0] - BAR_H / 2 - 20, "no skill", 15, L.ACCENT, "bold",
                      anchor="middle"))

    for i, (name, acc, pr) in enumerate(BARS):
        y = BAR_ROWS[i]
        p.append(text(M + 26, y + 9, name, 21, L.INK, "bold"))
        for x, w, value, vmax, fill in (
            (ACC_X, ACC_W, acc, 1.0, L.BAR_MUTED),
            (PR_X, PR_W, pr, PR_MAX, L.SLATE),
        ):
            p.append(rect(x, y - BAR_H / 2, w, BAR_H, L.SURFACE, L.LINE, r=5, sw=1.2))
            if known:
                p.append(rect(x, y - BAR_H / 2, w * value / vmax, BAR_H, fill, None, r=5))
                p.append(text(x + w + 12, y + 8, f"{value:.3f}", 21, L.INK, "bold"))
            else:
                p.append(text(x + w + 12, y + 8, "?", 21, L.FAINT, "bold"))

    p += verdict(version, VERDICT)
    return p


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def build(version: str) -> str:
    body = [rect(0, 0, W, H, L.PAPER)]
    body += band_header(version, KICKER, HEAD, CHIPS)
    body += band_path(version, STOPS, SPUR, bracket_text=BRACKET)
    body += band_score(version)
    body += footer(FOOTER_LEFT, FOOTER_RIGHT)
    title = "Week 1: the questions" if version == "questions" else "Week 1: the answers"
    return document(body, title)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true", help="also write PNGs at 2x")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    write_pair(Path(args.out), "lab1", build, png=args.png)


if __name__ == "__main__":
    main()
