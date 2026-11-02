"""Week 4 lecture graphic: "A score is not a decision".

Builds two SVGs with identical geometry:

    lab4-questions.svg   the questions, to show at the start of the session
    lab4-answers.svg     the same frame filled in, to show at the end

Usage:
    python scripts/figures/lab4_path_svg.py                 # writes both SVGs
    python scripts/figures/lab4_path_svg.py --png           # also writes PNGs

The seam from Week 2 comes back, because everything here is chosen on
validation and test is looked at once. The scoreboard is costs rather than
scores, so lower is better, and the reference line differs per column: it is
what doing nothing costs in that period.

Numbers: all but two are printed on the Week 4 page. Flagging everything means
no misses and a false alarm for every on-time order, so it costs 1 minus the
late rate: 0.88 on validation at 11.8% late, which matches the page, and 0.96
on test at 4.4%. Both rates come from Week 2's split table.
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
OUT = ROOT / "docs" / "assets" / "images" / "lecture" / "week-04"

# ---------------------------------------------------------------------------
# this week's scoreboard geometry
# ---------------------------------------------------------------------------

VAL_X, VAL_W = 500, 360
TEST_X, TEST_W = 1010, 360
COST_MAX = 1.25  # one scale for both columns, so the periods are comparable

# the dead end branches from stop 3, left of centre
SPUR_BOX = (480, 310, 420, 86)

# ---------------------------------------------------------------------------
# content
# ---------------------------------------------------------------------------

KICKER = "MACHINE LEARNING @ UMT  ·  WEEK 4  ·  EVALUATION & ERROR ANALYSIS"

HEAD = {
    "questions": [
        ("The model ranks well. So we can act on it, right?", 46, "slate", "bold"),
        ("A score is a summary, and every summary hides something.", 26, "muted", "regular"),
    ],
    "answers": [
        ("A threshold chosen from the costs saved 43% on validation,", 42, "ink", "bold"),
        ("and cost more than doing nothing on test.", 42, "ink", "bold"),
    ],
}

CHIPS = [
    ("THRESHOLD", "0.48", "?"),
    ("COSTS", "10 to 1", "?"),
    ("JUDGED ON", "validation", "?"),
    ("WRITTEN IN", "the model card", "?"),
]

HALVES = [
    (0, "CHOOSE IT ALL ON VALIDATION"),
    (4, "THEN LOOK AT TEST, ONCE"),
]

# title, question (version A), payload (version B), caption (version B)
STOPS = [
    (
        "Threshold",
        ["What turns a score", "into a decision?"],
        ("0.48", None),
        ["chosen on validation,", "where cost is lowest"],
    ),
    (
        "Cost",
        ["Which mistake can", "we least afford?"],
        ("1.18", "0.67"),
        ["cost per order, doing", "nothing then acting"],
    ),
    (
        "Calibrate",
        ["Is a score of 0.8", "really 80%?"],
        ("0.47 vs 12%", None),
        ["average score against", "orders actually late"],
    ),
    (
        "Slice",
        ["Who does", "it fail?"],
        ("68% vs 15%", None),
        ["late orders caught overall,", "and within one state"],
    ),
    (
        "Interval",
        ["Is the gain", "real?"],
        ("1.73 – 2.06", None),
        ["95% interval on test lift ·", "the gain clears zero"],
    ),
    (
        "Decide",
        ["Does the decision", "survive?"],
        ("0.55 vs 0.44", None),
        ["cost on test against", "doing nothing"],
    ),
]

BRACKET = {
    "questions": "Will the saving still be there on test?",
    "answers": "the 43% saving on validation became a loss on test",
}

SPUR = {
    "questions": ("A DEAD END", "Why not read a score of",
                  "0.8 as an 80% chance?", "?"),
    "answers": ("A DEAD END", "orders scored above 0.8 are",
                "late 36% of the time", "80%"),
}

# label (A), label (B), cost on validation, cost on test
BARS = [
    ("Flag nobody", "Flag nobody", 1.18, 0.44),
    ("Flag everybody", "Flag everybody", 0.88, 0.96),
    ("The model, at some threshold", "The model at 0.48", 0.67, 0.55),
]
DOING_NOTHING = (BARS[0][2], BARS[0][3])

VERDICT = {
    "questions": "Three policies, two periods. Which one would you ship?",
    "answers": "The same threshold, chosen carefully. It beat doing nothing on validation and lost to it on test.",
}

FOOTER_LEFT = (
    "Olist Brazilian e-commerce · 96,204 orders · a miss costs 10, "
    "a false alarm costs 1 — business assumptions, not facts"
)
FOOTER_RIGHT = "ml-course-umt · Week 4 · Evaluation & error analysis"


# ---------------------------------------------------------------------------
# the scoreboard: what the decision costs, on validation and on test
# ---------------------------------------------------------------------------


def band_score(version: str) -> list[str]:
    known = version == "answers"
    p: list[str] = []
    top = BAR_ROWS[0] - 64
    p.append(rect(M, top, W - 2 * M, BAR_ROWS[-1] + 36 - top, L.PLATE, None, r=14))

    p.append(text(M + 26, Y_BAND3_LABEL, "THE SAME DECISION, TWICE", 16, L.FAINT,
                  "bold", tracking=2.4))
    p.append(text(VAL_X, Y_BAND3_LABEL, "COST ON VALIDATION", 15, L.MUTED, "bold",
                  tracking=1.8))
    p.append(text(TEST_X, Y_BAND3_LABEL, "COST ON TEST", 15, L.MUTED, "bold",
                  tracking=1.8))
    p.append(text(TEST_X + TEST_W + 12, Y_BAND3_LABEL, "both 0 to 1.25", 14, L.FAINT))

    y_note = BAR_ROWS[0] - BAR_H / 2 - 12
    # these are costs, not scores: say so where nobody can miss it
    p.append(text(M + 26, y_note, "LOWER IS BETTER", 14, L.ACCENT, "bold", tracking=1.6))

    if known:
        # doing nothing costs a different amount in each period
        for (x, w), value in zip(((VAL_X, VAL_W), (TEST_X, TEST_W)), DOING_NOTHING):
            gx = x + w * (value / COST_MAX)
            p.append(line(gx, BAR_ROWS[0] - BAR_H / 2 - 8, gx,
                          BAR_ROWS[-1] + BAR_H / 2 + 8, L.ACCENT, 2, dash="5 5"))
            p.append(text(gx, y_note, "doing nothing", 14, L.ACCENT, "bold",
                          anchor="middle"))

    for i, (asked, told, val, test_cost) in enumerate(BARS):
        y = BAR_ROWS[i]
        p.append(text(M + 26, y + 9, told if known else asked, 21, L.INK, "bold"))
        for x, w, value in ((VAL_X, VAL_W, val), (TEST_X, TEST_W, test_cost)):
            p.append(rect(x, y - BAR_H / 2, w, BAR_H, L.SURFACE, L.LINE, r=5, sw=1.2))
            if known:
                p.append(rect(x, y - BAR_H / 2, w * value / COST_MAX, BAR_H, L.SLATE,
                              None, r=5))
                p.append(text(x + w + 12, y + 8, f"{value:.2f}", 21, L.INK, "bold"))
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
    body += band_path(version, STOPS, SPUR, bracket_text=BRACKET,
                      bracket_span=(1, 5), spur_at=2, spur_box=SPUR_BOX,
                      halves=HALVES, last_size=34)
    body += band_score(version)
    body += footer(FOOTER_LEFT, FOOTER_RIGHT)
    title = "Week 4: the questions" if version == "questions" else "Week 4: the answers"
    return document(body, title)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true", help="also write PNGs at 2x")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    write_pair(Path(args.out), "lab4", build, png=args.png)


if __name__ == "__main__":
    main()
