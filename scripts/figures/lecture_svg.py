"""Shared shell for the weekly lecture graphics.

Every week is a pair of SVGs with identical geometry: the questions, shown at
the start of the session, and the same frame filled in, shown at the end. Only
the contents of the slots change between them, never the layout, so the second
image reads as the first one answered.

This module holds everything the pairs have in common -- palette, type,
canvas, the measurement helpers that stop text overflowing its column, and the
header, path and footer bands. Each week's own script supplies the content and
whatever band is particular to it.

Fonts: Space Grotesk is embedded in every SVG as base64 woff2, so the files are
self-contained and render the same anywhere. PNG export needs the same font
where the renderer (cairosvg) can find it; see fonts/README.md.
"""

from __future__ import annotations

import base64
import os
from pathlib import Path

from PIL import ImageFont

# ---------------------------------------------------------------------------
# fonts
# ---------------------------------------------------------------------------

HERE = Path(__file__).resolve().parent

# Space Grotesk lives next to this script (see fonts/README.md). Fall back to a
# locally installed copy, then to whatever the renderer has, so the script still
# runs on a machine without it -- only the typeface changes, never the layout.
FONT_DIR = HERE / "fonts"
_FALLBACK = Path(os.path.expanduser("~/.fonts"))


def _font_file(name: str) -> Path | None:
    for base in (FONT_DIR, _FALLBACK):
        path = base / name
        if path.exists():
            return path
    return None


FONT_REGULAR = _font_file("SpaceGrotesk-Regular.ttf")
FONT_BOLD = _font_file("SpaceGrotesk-Bold.ttf")
WOFF_DIR = FONT_DIR

# ---------------------------------------------------------------------------
# palette — the site stylesheet's two schemes, as drawing roles
# ---------------------------------------------------------------------------

THEMES = {
    "light": dict(
        PAPER="#faf8f5", SURFACE="#ffffff", PLATE="#f2eee7",
        LINE="#e4ded3", LINE_STRONG="#cfc6b7", BAR_MUTED="#cfc6b7",
        INK="#23252b", MUTED="#5f636d", FAINT="#9a9ca4",
        SLATE="#3d5a80", ACCENT="#c05d3e", ACCENT_TINT="#f8ece6",
    ),
    "dark": dict(
        PAPER="#16181d", SURFACE="#2a2f38", PLATE="#1e2127",
        LINE="#2e333c", LINE_STRONG="#3f4651", BAR_MUTED="#5b6472",
        INK="#e8e6e3", MUTED="#a8abb4", FAINT="#767a85",
        SLATE="#8fb0d4", ACCENT="#e0855f", ACCENT_TINT="#2d241f",
    ),
}


def set_theme(name: str) -> str:
    """Rebind the colour roles. Drawing reads them live, so call this first."""
    globals().update(THEMES[name])
    return name


set_theme("light")

# Named so a week's content can say "slate" without importing a colour value.
ROLES = ("PAPER", "SURFACE", "PLATE", "LINE", "LINE_STRONG", "BAR_MUTED",
         "INK", "MUTED", "FAINT", "SLATE", "ACCENT", "ACCENT_TINT")


def role(name: str) -> str:
    """Resolve a role name such as "slate" to the current theme's colour."""
    return globals()[name.upper()]


DISPLAY = "'Space Grotesk', 'Inter', -apple-system, sans-serif"

W, H = 1600, 1000
M = 64  # side margin

# ---------------------------------------------------------------------------
# geometry — shared by both versions of a pair, so nothing shifts between them
# ---------------------------------------------------------------------------

Y_KICKER = 58
Y_HEAD_1 = 122
Y_HEAD_2 = 170
CHIP_Y, CHIP_H = 202, 88
Y_BAND_LABEL = 348
SPUR_BOX = (1046, 310, 420, 86)  # x, y, w, h
Y_HALF_LABEL = 432
SPINE_Y = 470
DISC_R = 20
Y_STOP_TITLE = 524
Y_PAYLOAD = 574
Y_CAPTION = 604
Y_QUESTION = 566  # version A, first line
BRACKET_Y = 658
Y_BAND3_LABEL = 734
BAR_ROWS = (778, 824, 870)
BAR_H = 26
Y_VERDICT = 936
Y_FOOTER = 974

STOP_COUNT = 6
COL_W = (W - 2 * M) / STOP_COUNT
STOP_X = [M + COL_W * (i + 0.5) for i in range(STOP_COUNT)]

# ---------------------------------------------------------------------------
# text measurement, so nothing can overflow its column
# ---------------------------------------------------------------------------

_cache: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def _font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    key = (weight, size)
    if key not in _cache:
        path = FONT_BOLD if weight == "bold" else FONT_REGULAR
        if path is None:  # no Space Grotesk: measure with something close enough
            _cache[key] = ImageFont.truetype(
                "DejaVuSans-Bold.ttf" if weight == "bold" else "DejaVuSans.ttf", size
            )
        else:
            _cache[key] = ImageFont.truetype(str(path), size)
    return _cache[key]


def text_width(s: str, size: int, weight: str = "regular", tracking: float = 0.0) -> float:
    """Advance width of a string, including letter-spacing."""
    w = _font(weight, size).getlength(s)
    return w + tracking * max(len(s) - 1, 0)


def fit_size(s: str, max_w: float, size: int, weight: str = "regular", floor: int = 12) -> int:
    """Largest size no bigger than `size` at which `s` fits inside `max_w`."""
    while size > floor and text_width(s, size, weight) > max_w:
        size -= 1
    return size


# ---------------------------------------------------------------------------
# svg primitives
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def text(
    x: float,
    y: float,
    s: str,
    size: int,
    fill: str | None = None,
    weight: str = "regular",
    anchor: str = "start",
    tracking: float = 0.0,
    opacity: float | None = None,
) -> str:
    attrs = [
        f'x="{x:.1f}"',
        f'y="{y:.1f}"',
        f'font-family="{DISPLAY}"',
        f'font-size="{size}"',
        f'fill="{fill or INK}"',
    ]
    if weight == "bold":
        attrs.append('font-weight="700"')
    if anchor != "start":
        attrs.append(f'text-anchor="{anchor}"')
    if tracking:
        attrs.append(f'letter-spacing="{tracking}"')
    if opacity is not None:
        attrs.append(f'opacity="{opacity}"')
    return f"<text {' '.join(attrs)}>{esc(s)}</text>"


def rect(
    x: float,
    y: float,
    w: float,
    h: float,
    fill: str = "none",
    stroke: str | None = None,
    r: float = 0,
    sw: float = 1.5,
    dash: str | None = None,
) -> str:
    attrs = [f'x="{x:.1f}"', f'y="{y:.1f}"', f'width="{w:.1f}"', f'height="{h:.1f}"', f'fill="{fill}"']
    if r:
        attrs.append(f'rx="{r}"')
    if stroke:
        attrs += [f'stroke="{stroke}"', f'stroke-width="{sw}"']
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f"<rect {' '.join(attrs)} />"


def line(x1: float, y1: float, x2: float, y2: float, stroke: str, sw: float = 1.5,
         dash: str | None = None, cap: str = "round") -> str:
    attrs = [
        f'x1="{x1:.1f}"', f'y1="{y1:.1f}"', f'x2="{x2:.1f}"', f'y2="{y2:.1f}"',
        f'stroke="{stroke}"', f'stroke-width="{sw}"', f'stroke-linecap="{cap}"',
    ]
    if dash:
        attrs.append(f'stroke-dasharray="{dash}"')
    return f"<line {' '.join(attrs)} />"


def arrow_right(x: float, y: float, size: float, fill: str) -> str:
    """A small solid arrow, drawn as a path because the font subset has no U+2192."""
    h = size * 0.5
    stem = size * 0.62
    return (
        f'<path d="M {x:.1f} {y:.1f} h {stem:.1f} M {x + size:.1f} {y:.1f} '
        f'l {-h * 0.75:.1f} {-h * 0.55:.1f} v {h * 1.1:.1f} Z" '
        f'stroke="{fill}" stroke-width="{max(size * 0.13, 1.6):.1f}" fill="{fill}" '
        f'stroke-linecap="round" stroke-linejoin="round" />'
    )


def pair_with_arrow(cx: float, y: float, left: str, right: str, size: int,
                    fill: str, weight: str = "bold") -> str:
    """Render 'left -> right' centred on cx, with a drawn arrow between."""
    gap = size * 0.34
    arrow_w = size * 0.56
    lw = text_width(left, size, weight)
    rw = text_width(right, size, weight)
    total = lw + gap + arrow_w + gap + rw
    x = cx - total / 2
    parts = [text(x, y, left, size, fill, weight)]
    parts.append(arrow_right(x + lw + gap, y - size * 0.3, arrow_w, fill))
    parts.append(text(x + lw + gap + arrow_w + gap, y, right, size, fill, weight))
    return "".join(parts)


def pair_size(left: str, right: str, max_w: float, size: int, weight: str = "bold") -> int:
    """Largest size at which 'left -> right' fits inside max_w."""
    while size > 14:
        gap, aw = size * 0.34, size * 0.56
        total = (text_width(left, size, weight) + text_width(right, size, weight)
                 + 2 * gap + aw)
        if total <= max_w:
            break
        size -= 1
    return size


def font_face() -> str:
    """Embed Space Grotesk so the SVG renders identically wherever it is opened."""
    faces = []
    for weight, fname in ((500, "space-grotesk-latin-500-normal.woff2"),
                          (700, "space-grotesk-latin-700-normal.woff2")):
        path = WOFF_DIR / fname
        if not path.exists():
            continue
        b64 = base64.b64encode(path.read_bytes()).decode("ascii")
        faces.append(
            "@font-face{font-family:'Space Grotesk';font-style:normal;"
            f"font-weight:{weight};font-display:block;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}"
        )
    return "".join(faces)


# ---------------------------------------------------------------------------
# bands shared by every week
# ---------------------------------------------------------------------------


def band_header(version: str, kicker: str, head: dict, chips: list) -> list[str]:
    """Kicker rule, the headline, and the four-chip contract beneath it."""
    p: list[str] = []
    p.append(text(M, Y_KICKER, kicker, 16, FAINT, "bold", tracking=2.4))
    p.append(line(M, Y_KICKER + 20, W - M, Y_KICKER + 20, LINE, 1.5))

    for i, (line_text, size, fill, weight) in enumerate(head[version]):
        y = Y_HEAD_1 if i == 0 else Y_HEAD_2
        size = fit_size(line_text, W - 2 * M, size, weight)
        p.append(text(M, y, line_text, size, role(fill), weight))

    gap = 32
    cw = (W - 2 * M - gap * 3) / 4
    for i, (label, value, blank) in enumerate(chips):
        x = M + i * (cw + gap)
        shown = value if version == "answers" else blank
        fill = SURFACE if version == "answers" else PLATE
        p.append(rect(x, CHIP_Y, cw, CHIP_H, fill, LINE, r=10))
        p.append(rect(x, CHIP_Y, 4, CHIP_H, SLATE if version == "answers" else LINE_STRONG,
                      r=2))
        p.append(text(x + 22, CHIP_Y + 32, label, 14, FAINT, "bold", tracking=2.0))
        size = fit_size(shown, cw - 44, 25 if version == "answers" else 30, "bold")
        p.append(text(x + 22, CHIP_Y + 65, shown, size,
                      INK if version == "answers" else FAINT, "bold"))
    return p


def band_path(
    version: str,
    stops: list,
    spur_text: dict,
    band_label: str = "THE PATH · SIX MOVES",
    bracket_text: dict | None = None,
    bracket_span: tuple[int, int] = (1, 2),
    spur_at: int = 4,
    halves: list | None = None,
    last_size: int = 28,
) -> list[str]:
    """The spine: six numbered stops, one dead-end branch, an optional bracket.

    `halves` draws a seam in the spine: a list of (first_stop_index, label).
    """
    p: list[str] = []
    p.append(text(M, Y_BAND_LABEL, band_label, 16, FAINT, "bold", tracking=2.4))

    x0, x1 = STOP_X[0], STOP_X[-1]
    p.append(line(x0, SPINE_Y, x1, SPINE_Y, LINE_STRONG, 3))

    if halves:
        for n, (first, label) in enumerate(halves):
            left = M if first == 0 else (STOP_X[first - 1] + STOP_X[first]) / 2
            p.append(text(left + 8, Y_HALF_LABEL, label, 14, MUTED, "bold", tracking=1.8))
            if n:  # the seam itself, drawn once, between the two halves
                p.append(line(left, SPINE_Y - 16, left, SPINE_Y + 16, LINE_STRONG, 2,
                              dash="4 5"))

    p += spur(version, spur_text, spur_at)

    for i, (title, question, payload, caption) in enumerate(stops):
        cx = STOP_X[i]
        col = COL_W - 26
        last = i == STOP_COUNT - 1
        ring = SLATE if version == "answers" else LINE_STRONG
        p.append(f'<circle cx="{cx:.1f}" cy="{SPINE_Y}" r="{DISC_R}" fill="{SURFACE}" '
                 f'stroke="{ring}" stroke-width="3" />')
        p.append(text(cx, SPINE_Y + 7, str(i + 1), 18,
                      SLATE if version == "answers" else MUTED, "bold", anchor="middle"))

        size = fit_size(title, col, 26, "bold")
        p.append(text(cx, Y_STOP_TITLE, title, size, INK, "bold", anchor="middle"))

        if version == "answers":
            left, right = payload
            if right is None:
                size = fit_size(left, col, 34 if not last else last_size, "bold")
                p.append(text(cx, Y_PAYLOAD, left, size, SLATE, "bold", anchor="middle"))
            else:
                size = pair_size(left, right, col, 30)
                p.append(pair_with_arrow(cx, Y_PAYLOAD, left, right, size, SLATE))
            for j, cl in enumerate(caption):
                size = fit_size(cl, col, 18)
                p.append(text(cx, Y_CAPTION + j * 23, cl, size, MUTED, anchor="middle"))
        else:
            for j, ql in enumerate(question):
                size = fit_size(ql, col, 24, "bold")
                p.append(text(cx, Y_QUESTION + j * 29, ql, size, SLATE, "bold",
                              anchor="middle"))

    if bracket_text:
        p += bracket(version, bracket_text, bracket_span)
    return p


def spur(version: str, spur_text: dict, at: int = 4) -> list[str]:
    """The tempting wrong turn: a dashed branch rising off one stop to a dead end."""
    bx, by, bw, bh = SPUR_BOX
    jx = STOP_X[at]
    top, bottom = by + bh, SPINE_Y - DISC_R - 3
    cap, l1, l2, value = spur_text[version]
    known = version == "answers"

    p = [
        line(jx, bottom, jx, top + 10, ACCENT, 2.5, dash="7 6", cap="butt"),
        f'<path d="M {jx:.1f} {top:.1f} l -7 11 h 14 Z" fill="{ACCENT}" />',
        f'<circle cx="{jx:.1f}" cy="{SPINE_Y}" r="7" fill="{PAPER}" stroke="{ACCENT}" '
        f'stroke-width="2.5" />',
        rect(bx, by, bw, bh, ACCENT_TINT, ACCENT, r=10, sw=2),
        text(bx + 22, by + 28, cap, 14, ACCENT, "bold", tracking=2.0),
        text(bx + 22, by + 54, l1, 17, MUTED),
        text(bx + 22, by + 75, l2, 17, MUTED),
    ]

    vx = bx + bw - 24
    vsize = 34 if known else 42
    p.append(text(vx, by + 68, value, vsize, ACCENT, "bold", anchor="end"))
    if known:
        vw = text_width(value, vsize, "bold")
        p.append(line(vx - vw - 7, by + 56, vx + 5, by + 56, ACCENT, 3))
    return p


def bracket(version: str, bracket_text: dict, span: tuple[int, int]) -> list[str]:
    """A tie under two neighbouring stops, for a consequence that links them."""
    x1, x2 = STOP_X[span[0]], STOP_X[span[1]]
    y = BRACKET_Y
    label = bracket_text[version]
    known = version == "answers"
    fill = MUTED if known else SLATE
    weight = "regular" if known else "bold"
    size = fit_size(label, W - 2 * M, 19, weight)
    # centre the label under the bracket, but never let it run past a margin
    half = text_width(label, size, weight) / 2
    cx = min(max((x1 + x2) / 2, M + half), W - M - half)
    return [
        f'<path d="M {x1:.1f} {y - 14} V {y} H {x2:.1f} V {y - 14}" fill="none" '
        f'stroke="{LINE_STRONG}" stroke-width="2" />',
        text(cx, y + 26, label, size, fill, weight, anchor="middle"),
    ]


def verdict(version: str, lines: dict) -> list[str]:
    known = version == "answers"
    s = lines[version]
    size = fit_size(s, W - 2 * M, 25, "bold")
    return [text(M, Y_VERDICT, s, size, SLATE if not known else INK, "bold")]


def footer(left: str, right: str) -> list[str]:
    return [
        text(M, Y_FOOTER, left, 15, FAINT),
        text(W - M, Y_FOOTER, right, 15, FAINT, anchor="end"),
    ]


# ---------------------------------------------------------------------------
# assembly
# ---------------------------------------------------------------------------


def document(body: list[str], title: str) -> str:
    inner = "\n  ".join(body)
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="{title}">\n'
        f"  <title>{title}</title>\n"
        f"  <defs><style>{font_face()}</style></defs>\n"
        f"  {inner}\n"
        f"</svg>\n"
    )


def _png_writer():
    """cairosvg if it is installed, else None. PNGs are a convenience: the SVGs
    are what the site uses, so a missing renderer is a note, not a failure."""
    try:
        import cairosvg
    except (ImportError, OSError) as exc:  # OSError: cairo itself is missing
        print(
            f"note: PNG export skipped ({exc.__class__.__name__}). The SVGs are "
            "written and are all the site needs.\n"
            "      To enable PNGs: sudo apt-get install -y libcairo2 "
            "&& pip install cairosvg"
        )
        return None
    return cairosvg.svg2png


def write_pair(out_dir: Path, prefix: str, build, png: bool = False,
               themes: tuple[str, ...] = ("light", "dark")) -> None:
    """Write <prefix>-<version>-<theme>.svg for both versions, optionally as PNGs."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    svg2png = _png_writer() if png else None
    for theme in themes:
        set_theme(theme)
        for version in ("questions", "answers"):
            svg = build(version)
            stem = f"{prefix}-{version}-{theme}"
            path = out_dir / f"{stem}.svg"
            path.write_text(svg, encoding="utf-8")
            print(f"wrote {path}  ({len(svg) / 1024:.0f} KB)")
            if svg2png is not None:
                target = out_dir / f"{stem}.png"
                svg2png(bytestring=svg.encode("utf-8"), write_to=str(target),
                        output_width=W * 2, output_height=H * 2)
                print(f"wrote {target}")
    set_theme("light")
