"""Week 3 lecture graphic: "Two kinds of feature, one pipeline".

Builds two SVGs with identical geometry:

    lab3-questions.svg   the questions, to show at the start of the session
    lab3-answers.svg     the same frame filled in, to show at the end

Usage:
    python scripts/figures/lab3_path_svg.py                 # writes both SVGs
    python scripts/figures/lab3_path_svg.py --png           # also writes PNGs

New this week: the bracket spans three stops rather than two, because encoding,
scaling and fitting all live inside the same pipeline; and the dead end branches
from a stop on the left, so this week passes its own box position. The
scoreboard closes Block 1 -- the same three models, on validation and on test.
Every number comes from the Week 2 and Week 3 pages.
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
OUT = ROOT / "docs" / "assets" / "images" / "lecture" / "week-03"

# ---------------------------------------------------------------------------
# this week's scoreboard geometry
# ---------------------------------------------------------------------------

VAL_X, VAL_W = 460, 380
TEST_X, TEST_W = 980, 380
LIFT_MAX = 2.5

# the dead end branches from stop 4, which sits left of centre
SPUR_BOX = (760, 310, 420, 86)

# ---------------------------------------------------------------------------
# content
# ---------------------------------------------------------------------------

KICKER = "MACHINE LEARNING @ UMT  ·  WEEK 3  ·  FEATURE ENGINEERING"

HEAD = {
    "questions": [
        ("Last week's models barely beat guessing. So add more features?", 42, "slate", "bold"),
        ("Some features can be built anywhere. Some can quietly cheat.", 26, "muted", "regular"),
    ],
    "answers": [
        ("Four features built from one row each, inside one pipeline", 42, "ink", "bold"),
        ("that cannot leak. Test lift 1.87, up from 1.10.", 42, "ink", "bold"),
    ],
}

CHIPS = [
    ("ROW-WISE", "4, safe anywhere", "?"),
    ("LEARNED", "3, train only", "?"),
    ("WHERE", "one pipeline", "?"),
    ("DECIDED BY", "validation", "?"),
]

# title, question (version A), payload (version B), caption (version B)
STOPS = [
    (
        "Sort",
        ["Which features", "can leak?"],
        ("4 vs 3", None),
        ["row-wise features,", "and learned ones"],
    ),
    (
        "Build",
        ["What exists", "at purchase?"],
        ("1 of 4", None),
        ["says much on its own,", "and that one is distance"],
    ),
    (
        "Fit",
        ["Who is allowed", "to learn?"],
        ("train only", None),
        ["every average, median", "and rate per category"],
    ),
    (
        "Encode",
        ["How many values", "does it have?"],
        ("2 encodings", None),
        ["one-hot for 27 states,", "target for 3,000 sellers"],
    ),
    (
        "Scale",
        ["Does the model", "care about units?"],
        ("2.28", "2.34"),
        ["validation lift, unscaled", "then scaled · and readable"],
    ),
    (
        "Judge",
        ["Which features", "earn their place?"],
        ("1.87", None),
        ["test lift, looked at once ·", "the simplest model won"],
    ),
]

BRACKET = {
    "questions": "Where do these three steps actually live?",
    "answers": "fit once, on train: all three live inside one pipeline",
}

SPUR = {
    "questions": ("A DEAD END", "Why not encode each seller",
                  "by their own late rate?", "?"),
    "answers": ("A DEAD END", "scored on the rows it learned",
                "from · 1.74 on new ones", "3.97"),
}

# label (A), label (B), validation lift, test lift
BARS = [
    ("Week 1: high-risk-state rule", "Week 1: high-risk-state rule", 1.57, 1.10),
    ("Week 1: depth-2 tree", "Week 1: depth-2 tree", 1.65, 1.18),
    ("Week 3: four features, scaled", "Week 3: four features, scaled", 2.34, 1.87),
]

VERDICT = {
    "questions": "Three models, two columns. Which of these gaps should worry you?",
    "answers": "Every model drops from validation to test. This one drops and still clears the others.",
}

FOOTER_LEFT = (
    "Olist Brazilian e-commerce · 96,204 orders · trained on 2017, "
    "judged on the months nobody looked at"
)
FOOTER_RIGHT = "ml-course-umt · Week 3 · Feature engineering"


# ---------------------------------------------------------------------------
# the scoreboard: Block 1's three models, on validation and on test
# ---------------------------------------------------------------------------


def band_score(version: str) -> list[str]:
    known = version == "answers"
    p: list[str] = []
    top = BAR_ROWS[0] - 64
    p.append(rect(M, top, W - 2 * M, BAR_ROWS[-1] + 36 - top, L.PLATE, None, r=14))

    p.append(text(M + 26, Y_BAND3_LABEL, "THE ARC OF BLOCK 1", 16, L.FAINT, "bold",
                  tracking=2.4))
    p.append(text(VAL_X, Y_BAND3_LABEL, "VALIDATION LIFT", 15, L.MUTED, "bold",
                  tracking=1.8))
    p.append(text(TEST_X, Y_BAND3_LABEL, "TEST LIFT", 15, L.MUTED, "bold", tracking=1.8))
    p.append(text(TEST_X + TEST_W + 12, Y_BAND3_LABEL, "both 0 to 2.5", 14, L.FAINT))

    y_note = BAR_ROWS[0] - BAR_H / 2 - 12

    if known:
        # 1.0 is guessing, on either column
        for x, w in ((VAL_X, VAL_W), (TEST_X, TEST_W)):
            gx = x + w * (1.0 / LIFT_MAX)
            p.append(line(gx, BAR_ROWS[0] - BAR_H / 2 - 8, gx,
                          BAR_ROWS[-1] + BAR_H / 2 + 8, L.ACCENT, 2, dash="5 5"))
            p.append(text(gx, y_note, "guessing", 14, L.ACCENT, "bold", anchor="middle"))

    for i, (asked, told, val, test_lift) in enumerate(BARS):
        y = BAR_ROWS[i]
        p.append(text(M + 26, y + 9, told if known else asked, 21, L.INK, "bold"))
        # validation is the number you chose on, test is the number that counts
        for x, w, value, fill in (
            (VAL_X, VAL_W, val, L.BAR_MUTED),
            (TEST_X, TEST_W, test_lift, L.SLATE),
        ):
            p.append(rect(x, y - BAR_H / 2, w, BAR_H, L.SURFACE, L.LINE, r=5, sw=1.2))
            if known:
                p.append(rect(x, y - BAR_H / 2, w * value / LIFT_MAX, BAR_H, fill,
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
                      bracket_span=(2, 4), spur_at=3, spur_box=SPUR_BOX,
                      last_size=34)
    body += band_score(version)
    body += footer(FOOTER_LEFT, FOOTER_RIGHT)
    title = "Week 3: the questions" if version == "questions" else "Week 3: the answers"
    return document(body, title)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true", help="also write PNGs at 2x")
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    write_pair(Path(args.out), "lab3", build, png=args.png)


if __name__ == "__main__":
    main()
