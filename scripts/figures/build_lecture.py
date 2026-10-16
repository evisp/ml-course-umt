#!/usr/bin/env python3
"""Rebuild every week's lecture pair.

Each week is two images with identical geometry -- the questions, shown at the
start of the session, and the same frame filled in, shown at the end -- in both
the light and the dark scheme.

Run from the repository root:

    python scripts/figures/build_lecture.py            # SVGs only
    python scripts/figures/build_lecture.py --png      # also PNGs, at 3200x2000

Outputs into docs/assets/images/lecture/week-NN/:
    labN-questions-{light,dark}.svg
    labN-answers-{light,dark}.svg

To add a week: write scripts/figures/labN_path_svg.py beside this file, then
add one line to WEEKS below.
"""

from __future__ import annotations

import argparse
import importlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

from lecture_svg import write_pair  # noqa: E402  (needs HERE on the path first)

# folder under docs/assets/images/lecture/, file prefix, module
WEEKS = [
    ("week-01", "lab1", "lab1_path_svg"),
    ("week-02", "lab2", "lab2_path_svg"),
]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--png", action="store_true", help="also write PNGs at 2x")
    ap.add_argument("--only", help="build one week only, e.g. week-02")
    args = ap.parse_args()

    base = ROOT / "docs" / "assets" / "images" / "lecture"
    for folder, prefix, module_name in WEEKS:
        if args.only and args.only != folder:
            continue
        module = importlib.import_module(module_name)
        write_pair(base / folder, prefix, module.build, png=args.png)


if __name__ == "__main__":
    main()
