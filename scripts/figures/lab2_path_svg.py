"""Week 2 lecture graphic: "Nine tables, one table, one honest score".

Builds two SVGs with identical geometry:

    lab2-questions.svg   the questions, to show at the start of the session
    lab2-answers.svg     the same frame filled in, to show at the end

Usage:
    python scripts/figures/lab2_path_svg.py                 # writes both SVGs
    python scripts/figures/lab2_path_svg.py --png           # also writes PNGs

The shell is shared with Week 1 through lecture_svg.py, so the two pairs read
as one series. What is new here is the seam in the spine -- Week 2 has two
halves -- and a scoreboard that judges one model three ways instead of three
models one way. Every number comes from the Week 2 page and notebook.
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
OUT = ROOT / "docs" / "assets" / "images" / "lecture" / "week-02"

# ---------------------------------------------------------------------------
# this week's scoreboard geometry
# ---------------------------------------------------------------------------

PR_X, PR_W = 500, 360
LIFT_X, LIFT_W = 1010, 360
PR_MAX = 0.25
LIFT_MAX = 2.0

# ---------------------------------------------------------------------------
# content
# ---------------------------------------------------------------------------

KICKER = "MACHINE LEARNING @ UMT  ·  WEEK 2  ·  DATA QUALITY & SPLITTING"

HEAD = {
    "questions": [
        ("Nine tables, one order id. Just join them, right?", 46, "slate", "bold"),
        ("Nine files. Nobody wrote down what one row means.", 26, "muted", "regular"),
    ],
    "answers": [
        ("Nine tables became one table of 96,204 rows.", 42, "ink", "bold"),
        ("The split decides what the model may learn from.", 42, "ink", "bold"),
    ],
}

CHIPS = [
    ("GRAIN", "one order", "?"),
    ("ROWS", "96,204", "?"),
    ("SPLIT", "by time", "?"),
    ("EXPLORE", "training only", "?"),
]

HALVES = [
    (0, "MAKE ONE TRUSTWORTHY TABLE"),
    (3, "DECIDE WHAT IT MAY LEARN FROM"),
]

# title, question (version A), payload (version B), caption (version B)
STOPS = [
    (
        "Grain",
        ["What does one", "row mean?"],
        ("2 of 4", None),
        ["join keys that look", "unique and are not"],
    ),
    (
        "Join",
        ["What does a careless", "join cost?"],
        ("96,204", "114,521"),
        ["rows after a naive join,", "with no warning at all"],
    ),
    (
        "Audit",
        ["What is actually", "wrong in here?"],
        ("7 findings", None),
        ["from 6 checks · and one", "whole table dropped"],
    ),
    (
        "Split",
        ["Who will the model", "be used on?"],
        ("3 periods", None),
        ["986 shared buyers at random,", "420 by time, 0 grouped"],
    ),
    (
        "Lift",
        ["Did the baselines", "survive?"],
        ("1.50", "1.18"),
        ["the tree's lift, random", "split versus the future"],
    ),
    (
        "Explore",
        ["What should", "Week 3 build?"],
        ("5 charts", None),
        ["training data only ·", "four features, one ruled out"],
    ),
]

BRACKET = {
    "questions": "Why would a join change the row count?",
    "answers": "joining two grains multiplies rows, silently",
}

SPUR = {
    "questions": ("A DEAD END", "Why not just split at",
                  "random? The lift is higher.", "?"),
    "answers": ("A DEAD END", "says the pattern exists ·",
                "not that it will hold", "1.50"),
}

# label (A), label (B), PR AUC, lift, the no-skill floor for that period.
# Version A leaves the late rates off: they are what stop 4 is still asking.
BARS = [
    ("Random split", "Random split · 6.8% late", 0.102, 1.50, 0.068),
    ("Time: validation", "Time: validation · 11.8%", 0.195, 1.65, 0.118),
    ("Time: test", "Time: test · 4.4%", 0.052, 1.18, 0.044),
]

VERDICT = {
    "questions": "Same model, three splits. Which of these scores is the honest one?",
    "answers": "PR AUC moves with the floor. Lift is comparable, and on the future it is barely above 1.",
}

FOOTER_LEFT = (
    "Olist Brazilian e-commerce · nine raw tables · "
    "96,204 orders after joining at the grain"
)
FOOTER_RIGHT = "ml-course-umt · Week 2 · Data quality & splitting"


# ---------------------------------------------------------------------------
# the scoreboard: one depth-2 tree, judged on three different splits
# ---------------------------------------------------------------------------


def band_score(version: str) -> list[str]:
    known = version == "answers"
    p: list[str] = []
    top = BAR_ROWS[0] - 64
    p.append(rect(M, top, W - 2 * M, BAR_ROWS[-1] + 36 - top, L.PLATE, None, r=14))

    p.append(text(M + 26, Y_BAND3_LABEL, "THE SAME TREE, THREE SPLITS", 16, L.FAINT,
                  "bold", tracking=2.4))
    p.append(text(PR_X, Y_BAND3_LABEL, "PR AUC", 15, L.MUTED, "bold", tracking=1.8))
    p.append(text(PR_X + PR_W + 12, Y_BAND3_LABEL, "scale 0 to 0.25", 14, L.FAINT))
    p.append(text(LIFT_X, Y_BAND3_LABEL, "LIFT", 15, L.MUTED, "bold", tracking=1.8))
    p.append(text(LIFT_X + LIFT_W + 12, Y_BAND3_LABEL, "scale 0 to 2", 14, L.FAINT))

    y_note = BAR_ROWS[0] - BAR_H / 2 - 12

    if known:
        # lift has one floor for every period: 1.0 is guessing
        gx = LIFT_X + LIFT_W * (1.0 / LIFT_MAX)
        p.append(line(gx, BAR_ROWS[0] - BAR_H / 2 - 8, gx, BAR_ROWS[-1] + BAR_H / 2 + 8,
                      L.ACCENT, 2, dash="5 5"))
        p.append(text(gx, y_note, "guessing", 14, L.ACCENT, "bold", anchor="middle"))
        # PR AUC has a different floor in every period, so it is marked per row
        p.append(text(PR_X + PR_W * (BARS[0][4] / PR_MAX), y_note,
                      "its own floor", 14, L.ACCENT, "bold", anchor="middle"))

    for i, (asked, told, pr, lift, floor) in enumerate(BARS):
        y = BAR_ROWS[i]
        p.append(text(M + 26, y + 9, told if known else asked, 21, L.INK, "bold"))
        for x, w, value, vmax, fmt in (
            (PR_X, PR_W, pr, PR_MAX, "{:.3f}"),
            (LIFT_X, LIFT_W, lift, LIFT_MAX, "{:.2f}"),
        ):
            p.append(rect(x, y - BAR_H / 2, w, BAR_H, L.SURFACE, L.LINE, r=5, sw=1.2))
            if known:
                p.append(rect(x, y - BAR_H / 2, w * value / vmax, BAR_H, L.SLATE, None, r=5))
                p.append(text(x + w + 12, y + 8, fmt.format(value), 21, L.INK, "bold"))
            else:
                p.append(text(x + w + 12, y + 8, "?", 21, L.FAINT, "bold"))
        if known:
            # the no-skill floor for this period, drawn inside its own bar
            fx = PR_X + PR_W * (floor / PR_MAX)
            p.append(line(fx, y - BAR_H / 2 - 4, fx, y + BAR_H / 2 + 4, L.ACCENT, 2.5,
                          cap="butt"))

    p += verdict(version, VERDICT)
    return p


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def build(version: str) -> str:
    body = [rect(0, 0, W, H, L.PAPER)]
    body += band_header(version, KICKER, HEAD, CHIPS)
    body += band_path(version, STOPS, SPUR, bracket_text=BRACKET,
                      bracket_span=(0, 1), halves=HALVES, last_size=34)
    body += band_score(version)
    body += footer(FOOTER_LEFT, FOOTER_RIGHT)
    title = "Week 2: the questions" if version == "questions" else "Week 2: the answers"
    return document(body, title)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true", help="also write PNGs at 2x")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    write_pair(Path(args.out), "lab2", build, png=args.png)


if __name__ == "__main__":
    main()
