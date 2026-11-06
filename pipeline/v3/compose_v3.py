#!/usr/bin/env python3
"""Compose v3 ArchLang spectacle stills from real compiler / archlang3d outputs.

Every drawing and 3D frame is produced by ArchLang. This script only lays them
out and paints flat 2D typography (PIL). No invented geometry, no 3D text.
"""
from __future__ import annotations

import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path("/workspace/archlang-spectacle")
INT = ROOT / "output/v3/intermediates"
OUT = ROOT / "output/v3/stills"
OUT.mkdir(parents=True, exist_ok=True)

VOID = (15, 17, 21, 255)
VOID2 = (24, 27, 34, 255)
VOID3 = (32, 36, 46, 255)
PLUM = (128, 82, 255, 255)
PLUM_SOFT = (168, 140, 255, 255)
SHEET = (245, 242, 234, 255)
INK = (17, 17, 17, 255)
MUTED = (156, 162, 174, 255)
FG = (236, 238, 242, 255)
CODE_KW = (196, 167, 255, 255)
CODE_STR = (232, 196, 140, 255)
CODE_NUM = (125, 211, 252, 255)
CODE_CMT = (110, 118, 132, 255)
CODE_ID = (214, 220, 230, 255)
GREEN = (120, 198, 148, 255)
RED = (232, 98, 98, 255)
AMBER = (232, 176, 92, 255)

INTER = Path("/usr/share/fonts/truetype/sand-box/google/Inter/Inter-VariableFont_opsz,wght.ttf")
MONO = Path("/usr/share/fonts/truetype/sand-box/google/JetBrains Mono/JetBrainsMono-VariableFont_wght.ttf")

KW = re.compile(
    r"\b(plan|units|grid|scale|north|south|east|west|wall|room|door|window|"
    r"furniture|opening|let|for|in|if|theme|title|label|size|width|thickness|"
    r"exterior|partition|uses|hinge|swing|close|at|on|against|offset|"
    r"preview|compile|lint|describe|fix|suggest|review)\b"
)
NUM = re.compile(r"\b\d+(?:\.\d+)?(?:m2|mm|m)?\b|1:\d+")
STR = re.compile(r'"[^"\n]*"')
CMT = re.compile(r"#.*$")
IDENT_EQ = re.compile(r"\bid=([A-Za-z0-9_]+)")


def font(path: Path, size: int, weight: int = 400) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(path), size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        try:
            f.set_variation_by_axes([14, weight])
        except Exception:
            pass
    return f


def sans(size: int, w: int = 400) -> ImageFont.FreeTypeFont:
    return font(INTER, size, w)


def mono(size: int, w: int = 400) -> ImageFont.FreeTypeFont:
    return font(MONO, size, w)


def new_canvas(w: int, h: int) -> Image.Image:
    return Image.new("RGBA", (w, h), VOID)


def text_w(draw: ImageDraw.ImageDraw, text: str, fnt) -> int:
    return int(draw.textlength(text, font=fnt))


def trim_margins(im: Image.Image, pad: int = 18, ink_below: int = 246) -> Image.Image:
    rgb = im.convert("RGB")
    arr = np.asarray(rgb)
    # ink = not near-white (sheet drawings) and not near-void (dark 3D frames)
    mx = arr.max(axis=2)
    mn = arr.min(axis=2)
    near_white = (mn > ink_below) & (mx > ink_below)
    near_void = (mx < 28)
    ink = ~(near_white | near_void)
    if not ink.any():
        return im.convert("RGBA")
    ys, xs = np.where(ink)
    x0, x1 = max(0, xs.min() - pad), min(arr.shape[1], xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(arr.shape[0], ys.max() + pad + 1)
    return im.convert("RGBA").crop((int(x0), int(y0), int(x1), int(y1)))


def crop_main_drawing(im: Image.Image, pad: int = 16) -> Image.Image:
    """Keep the largest ink block plus nearby dimension strings; drop a distant schedule."""
    rgb = im.convert("RGB")
    arr = np.asarray(rgb)
    ink = arr.min(axis=2) < 210
    dens = ink.mean(axis=1)
    k = 9
    smooth = np.convolve(dens, np.ones(k) / k, mode="same")
    active = smooth > 0.008
    if not active.any():
        return trim_margins(im, pad)
    runs = []
    in_run = False
    start = 0
    for i, a in enumerate(active):
        if a and not in_run:
            start = i
            in_run = True
        elif (not a) and in_run:
            runs.append((start, i - 1))
            in_run = False
    if in_run:
        runs.append((start, len(active) - 1))

    def area(r):
        return int(ink[r[0] : r[1] + 1].sum())

    y0, y1 = max(runs, key=area)
    # Absorb only short nearby runs (dimension strings, north arrow, scale bar).
    # Never walk into a tall block such as a room schedule.
    changed = True
    while changed:
        changed = False
        for r0, r1 in runs:
            height = r1 - r0 + 1
            if height >= 80:
                continue
            if r1 < y0 and (y0 - r1) < 50:
                y0 = r0
                changed = True
            elif r0 > y1 and (r0 - y1) < 50:
                y1 = r1
                changed = True
    y0 = max(0, int(y0) - pad)
    y1 = min(arr.shape[0], int(y1) + pad + 1)
    band = ink[y0:y1]
    cols = band.any(axis=0)
    if cols.any():
        xs = np.where(cols)[0]
        x0 = max(0, int(xs[0]) - pad)
        x1 = min(arr.shape[1], int(xs[-1]) + pad + 1)
    else:
        x0, x1 = 0, arr.shape[1]
    return im.convert("RGBA").crop((int(x0), int(y0), int(x1), int(y1)))


def trim_near_bg(im: Image.Image, pad: int = 16, tol: int = 18) -> Image.Image:
    """Crop a replay frame to the model by dropping the near-uniform backdrop."""
    arr = np.asarray(im.convert("RGB"))
    h, w = arr.shape[:2]
    border = np.concatenate([
        arr[:6, :].reshape(-1, 3),
        arr[-6:, :].reshape(-1, 3),
        arr[:, :6].reshape(-1, 3),
        arr[:, -6:].reshape(-1, 3),
    ])
    bg = np.median(border, axis=0).astype(np.int16)
    diff = np.abs(arr.astype(np.int16) - bg).sum(axis=2)
    ink = diff > (tol * 3)
    if not ink.any():
        return im.convert("RGBA")
    ys, xs = np.where(ink)
    x0, x1 = max(0, xs.min() - pad), min(w, xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(h, ys.max() + pad + 1)
    return im.convert("RGBA").crop((int(x0), int(y0), int(x1), int(y1)))


def crop_replay_caption(im: Image.Image, bottom: int = 58) -> Image.Image:
    return im.convert("RGBA").crop((0, 0, im.width, max(1, im.height - bottom)))


def fit_contain(im: Image.Image, box, canvas: Image.Image, pad: int = 10) -> tuple[int, int, int, int]:
    x, y, w, h = box
    im = im.convert("RGBA")
    iw, ih = im.size
    scale = min((w - pad * 2) / max(iw, 1), (h - pad * 2) / max(ih, 1))
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    px = x + (w - nw) // 2
    py = y + (h - nh) // 2
    canvas.alpha_composite(resized, (px, py))
    return px, py, nw, nh


def rounded_rect(draw, box, radius, fill=None, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def sheet_card(canvas: Image.Image, box, title: str) -> tuple[int, int, int, int]:
    """Dark chrome around a sheet. Returns inner box."""
    x, y, w, h = box
    d = ImageDraw.Draw(canvas)
    rounded_rect(d, [x, y, x + w, y + h], 16, fill=VOID2, outline=(48, 52, 64, 255), width=1)
    d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    d.text((x + 18, y + 12), title, font=sans(17, 600), fill=MUTED)
    return (x + 14, y + 42, w - 28, h - 56)


def dark_card(canvas: Image.Image, box, title: str) -> tuple[int, int, int, int]:
    x, y, w, h = box
    d = ImageDraw.Draw(canvas)
    rounded_rect(d, [x, y, x + w, y + h], 16, fill=VOID2, outline=(48, 52, 64, 255), width=1)
    d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    d.text((x + 18, y + 12), title, font=sans(17, 600), fill=MUTED)
    return (x + 16, y + 42, w - 32, h - 56)


def paste_sheet(canvas: Image.Image, im: Image.Image, box, title: str, crop="drawing"):
    inner = sheet_card(canvas, box, title)
    if crop == "drawing":
        im = crop_main_drawing(im)
    elif crop == "trim":
        im = trim_margins(im)
    elif crop == "replay":
        im = crop_replay_caption(im)
        im = trim_near_bg(im)
    x, y, w, h = inner
    pad = 12 if crop != "replay" else 6
    im = im.convert("RGBA")
    iw, ih = im.size
    scale = min((w - pad * 2) / max(iw, 1), (h - pad * 2) / max(ih, 1))
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    px = x + (w - nw) // 2
    py = y + (h - nh) // 2
    if crop != "replay":
        mx0, my0 = px - 10, py - 10
        mx1, my1 = px + nw + 10, py + nh + 10
        ImageDraw.Draw(canvas).rounded_rectangle(
            [mx0, my0, mx1, my1], radius=8, fill=SHEET, outline=(220, 216, 206, 255)
        )
    canvas.alpha_composite(im.resize((nw, nh), Image.Resampling.LANCZOS), (px, py))


def paste_dark(canvas: Image.Image, im: Image.Image, box, title: str):
    inner = dark_card(canvas, box, title)
    im = crop_replay_caption(im)
    im = trim_near_bg(im, pad=20)
    fit_contain(im, inner, canvas, pad=8)


def draw_header(canvas, w, y, subtitle: str):
    d = ImageDraw.Draw(canvas)
    d.text((48, y), "ArchLang", font=sans(28, 650), fill=FG)
    brand_w = text_w(d, "ArchLang", sans(28, 650))
    d.text((48 + brand_w + 16, y + 8), "Designs that compile.", font=sans(16, 500), fill=PLUM_SOFT)
    sw = text_w(d, subtitle, sans(15, 500))
    d.text((w - 48 - sw, y + 10), subtitle, font=sans(15, 500), fill=MUTED)
    return y + 44


def draw_footer(canvas, w, h, text: str):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, h - 44, w, h], fill=(12, 14, 18, 255))
    d.text((48, h - 32), text, font=sans(14, 500), fill=MUTED)
    mark = "v3  ·  real compile · real 3D"
    mw = text_w(d, mark, sans(13, 500))
    d.text((w - 48 - mw, h - 32), mark, font=sans(13, 500), fill=(90, 94, 108, 255))


def highlight_line(text: str) -> list[tuple[str, tuple]]:
    """Return (segment, color) spans for one source line."""
    if not text:
        return [("", CODE_ID)]
    marks = [None] * len(text)

    def paint(span, color):
        a, b = span
        for i in range(a, b):
            if marks[i] is None:
                marks[i] = color

    m = CMT.search(text)
    if m:
        paint(m.span(), CODE_CMT)
    for m in STR.finditer(text):
        paint(m.span(), CODE_STR)
    for m in KW.finditer(text):
        paint(m.span(), CODE_KW)
    for m in NUM.finditer(text):
        paint(m.span(), CODE_NUM)

    spans = []
    i = 0
    n = len(text)
    while i < n:
        col = marks[i] or CODE_ID
        j = i + 1
        while j < n and (marks[j] or CODE_ID) == col:
            j += 1
        spans.append((text[i:j], col))
        i = j
    return spans


def draw_code(canvas, box, lines: list[str], start_no: int = 1, size: int = 15):
    x, y, w, h = box
    d = ImageDraw.Draw(canvas)
    rounded_rect(d, [x, y, x + w, y + h], 14, fill=(18, 20, 26, 255), outline=(48, 52, 64, 255))
    d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    fnt = mono(size, 450)
    ln_fnt = mono(size - 1, 400)
    line_h = size + 7
    max_lines = max(1, (h - 24) // line_h)
    shown = lines[:max_lines]
    cx = x + 16
    cy = y + 12
    gutter = text_w(d, "000", ln_fnt) + 12
    for i, line in enumerate(shown):
        no = f"{start_no + i:02d}"
        d.text((cx, cy), no, font=ln_fnt, fill=(78, 84, 96, 255))
        tx = cx + gutter
        for seg, col in highlight_line(line):
            d.text((tx, cy), seg, font=fnt, fill=col)
            tx += text_w(d, seg, fnt)
        cy += line_h


STUDIO_LINES = [
    'plan "Studio 1BR" {',
    "  units mm",
    "  scale 1:50",
    "",
    "  wall exterior thickness 200 {",
    "    (0,0) (7000,0)",
    "    (7000,6000) (0,6000) close",
    "  }",
    "  wall partition thickness 100 {",
    "    (4000,0) (4000,6000)",
    "  }",
    "",
    "  room id=r_living at (0,0)",
    '       size 4000x6000 label "Living / Kitchen"',
    "  room id=r_bed    at (4000,0)",
    '       size 3000x3000 label "Bedroom"',
    "  room id=r_hall   at (4000,3000)",
    '       size 3000x1400 label "Hall"',
    "  room id=r_bath   at (4000,4400)",
    '       size 3000x1600 label "Bath"',
    "",
    "  door id=d_main at (3000,6000) width 1000",
    "  window at (0,2000)    width 1500",
    "  window at (7000,1500) width 1200",
    "  furniture bed at (4300,300) size 1500x2000",
    "}",
]

COURT_LINES = [
    "# The courtyard is NOT a room.",
    "# Nothing is declared at (5000,3500)–(11000,7000):",
    "# it is the hole the building wraps around.",
    'plan "Courtyard House" {',
    "  units mm",
    "  scale 1:100",
    "  paper A2 landscape",
    "",
    "  zone living {",
    '    room id=r_live  label "Living"',
    '    room id=r_entry label "Entry"',
    '    room id=r_dining label "Dining"',
    "  }",
    "  zone private {",
    '    room id=r_bed1 label "Bedroom 1"',
    '    room id=r_bed2 label "Bedroom 2"',
    '    room id=r_bed3 label "Bedroom 3"',
    "  }",
    "",
    "  # sliding doors open onto the courtyard",
    "  door sliding on w_court at 50% width 900",
    "}",
]

PARAM_LINES_FOR = {
    2: 'let COUNT = 2             # number of units',
    3: 'let COUNT = 3             # number of units',
    4: 'let COUNT = 4             # number of units',
    5: 'let COUNT = 5             # number of units',
}

PARAM_BODY = [
    "let WALL  = 200",
    "let W     = 4000          # unit width",
    "let H     = 5000          # unit depth",
    "{count_line}",
    'let names = ["Studio A", "Studio B", …]',
    "",
    "for i in 0..COUNT {",
    "  let x = i * W",
    "  wall exterior thickness WALL {",
    "    (x, 0) (x + W, 0) (x + W, H) (x, H) close",
    "  }",
    '  room at (x, 0) size W x H label "{names[i]}"',
    "  furniture bed at (x + 300, 300) size 1500x2000",
    "  door at (x + W / 2, H) width 900",
    "}",
]


def load(p: Path) -> Image.Image:
    return Image.open(p).convert("RGBA")


def compose_01(w: int, h: int) -> Image.Image:
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    is_vert = h > w
    is_sq = abs(w - h) < 8
    header_y = 36 if not is_vert else 48
    draw_header(c, w, header_y, "same source  ·  compile  ·  archlang3d")
    footer_h = 44
    facts = "4 rooms  ·  42 m²  ·  3 doors  ·  3 windows  ·  every room reachable"
    margin = 48 if not is_vert else 64
    top = header_y + 52
    bottom = h - footer_h - 12
    plan = load(INT / "themes/studio-rendered.png")
    threed = load(INT / "replay/studio-3d-last.png")

    if is_vert:
        # 9:16 stacked: code, plan (largest), 3D
        avail = bottom - top
        code_h = int(avail * 0.28)
        plan_h = int(avail * 0.40)
        rest = avail - code_h - plan_h - 24
        code_box = (margin, top, w - 2 * margin, code_h)
        d.text((margin, top - 22), "studio.arch", font=sans(16, 600), fill=MUTED)
        draw_code(c, (code_box[0], code_box[1] + 4, code_box[2], code_box[3] - 4), STUDIO_LINES, size=15)
        y = top + code_h + 12
        paste_sheet(c, plan, (margin, y, w - 2 * margin, plan_h), "archlang compile  →  PNG  ·  theme rendered", crop="drawing")
        y = y + plan_h + 12
        paste_dark(c, threed, (margin, y, w - 2 * margin, rest), "archlang3d view --replay  ·  checked 3D from the same .arch")
    elif is_sq:
        code_h = 360
        d.text((margin, top - 22), "studio.arch", font=sans(16, 600), fill=MUTED)
        draw_code(c, (margin, top, w - 2 * margin, code_h), STUDIO_LINES, size=16)
        y = top + code_h + 16
        col_h = bottom - y
        gap = 16
        col_w = (w - 2 * margin - gap) // 2
        paste_sheet(c, plan, (margin, y, col_w, col_h), "archlang compile  →  PNG", crop="drawing")
        paste_dark(c, threed, (margin + col_w + gap, y, col_w, col_h), "archlang3d view --replay")
    else:
        # 16:9 triptych — plan gets the widest column
        gap = 18
        avail_w = w - 2 * margin - 2 * gap
        code_w = int(avail_w * 0.27)
        plan_w = int(avail_w * 0.42)
        three_w = avail_w - code_w - plan_w
        box_h = bottom - top
        d.text((margin, top - 22), "studio.arch", font=sans(16, 600), fill=MUTED)
        draw_code(c, (margin, top, code_w, box_h), STUDIO_LINES, size=15)
        paste_sheet(c, plan, (margin + code_w + gap, top, plan_w, box_h), "archlang compile  →  PNG  ·  theme rendered", crop="drawing")
        paste_dark(c, threed, (margin + code_w + gap + plan_w + gap, top, three_w, box_h), "archlang3d view --replay")
    draw_footer(c, w, h, facts)
    return c


def compose_02(w: int, h: int) -> Image.Image:
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    is_vert = h > w
    is_sq = abs(w - h) < 8
    header_y = 36 if not is_vert else 48
    draw_header(c, w, header_y, "courtyard-house.arch  ·  official example")
    footer_h = 44
    facts = "11 rooms  ·  163 m²  ·  10 doors  ·  15 windows  ·  the courtyard is a hole, not a room"
    margin = 48 if not is_vert else 64
    top = header_y + 52
    bottom = h - footer_h - 12
    plan = load(INT / "plans/courtyard-house.png")
    threed = load(INT / "replay/courtyard-3d-last.png")

    if is_vert:
        avail = bottom - top
        quote_h = 86
        plan_h = int((avail - quote_h) * 0.55)
        three_h = avail - quote_h - plan_h - 24
        quote = "The courtyard is not a room. Nothing is declared there — it is the hole the building wraps around."
        d.text((margin, top), quote, font=sans(18, 500), fill=FG)
        y = top + quote_h
        paste_sheet(c, plan, (margin, y, w - 2 * margin, plan_h), "archlang compile  →  dimensioned sheet", crop="drawing")
        y = y + plan_h + 12
        paste_dark(c, threed, (margin, y, w - 2 * margin, three_h), "archlang3d  ·  same source, walls risen, courtyard open to the sky")
    elif is_sq:
        quote_h = 64
        d.text((margin, top), "The courtyard is not a room — it is the hole the building wraps around.", font=sans(18, 500), fill=FG)
        y = top + quote_h
        col_h = bottom - y
        gap = 16
        col_w = (w - 2 * margin - gap) // 2
        paste_sheet(c, plan, (margin, y, col_w, col_h), "archlang compile  →  sheet", crop="drawing")
        paste_dark(c, threed, (margin + col_w + gap, y, col_w, col_h), "archlang3d view --replay")
    else:
        gap = 18
        avail_w = w - 2 * margin - gap
        plan_w = int(avail_w * 0.56)
        three_w = avail_w - plan_w
        box_h = bottom - top
        paste_sheet(c, plan, (margin, top, plan_w, box_h), "archlang compile  →  PNG  ·  courtyard-house.arch", crop="drawing")
        paste_dark(c, threed, (margin + plan_w + gap, top, three_w, box_h), "archlang3d view --replay  ·  same building")
    draw_footer(c, w, h, facts)
    return c


def compose_03(w: int, h: int) -> Image.Image:
    """Lint / fix: review sheet vs clean compiled plan, with 2D diagnostic type."""
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    is_vert = h > w
    is_sq = abs(w - h) < 8
    header_y = 36 if not is_vert else 48
    draw_header(c, w, header_y, "archlang preview --review   then   lint  ·  suggest  ·  compile")
    footer_h = 44
    facts = "W_BEDROOM_NO_WINDOW  ·  fix: add a window on an exterior wall of the room"
    margin = 48 if not is_vert else 64
    top = header_y + 52
    bottom = h - footer_h - 12
    before = load(INT / "lint/studio-nowindow-review.png")
    after = load(INT / "plans/studio.png")

    banner_h = 78 if not is_vert else 110
    # diagnostic banner
    bx, by, bw = margin, top, w - 2 * margin
    rounded_rect(d, [bx, by, bx + bw, by + banner_h], 14, fill=(42, 24, 28, 255), outline=(120, 48, 52, 255))
    d.text((bx + 20, by + 12), "BEFORE", font=sans(13, 650), fill=RED)
    d.text((bx + 20, by + 32), "W_BEDROOM_NO_WINDOW", font=mono(20 if not is_vert else 18, 600), fill=AMBER)
    msg = 'Bedroom "Bedroom" has no window.'
    d.text((bx + 20, by + (52 if not is_vert else 58)), msg, font=sans(15, 500), fill=FG)
    # after note on the right of banner (landscape / square)
    if not is_vert:
        after_l = "AFTER   window at (7000,1500) width 1200   →  lint clean"
        aw = text_w(d, after_l, sans(15, 600))
        d.text((bx + bw - aw - 20, by + 30), after_l, font=sans(15, 600), fill=GREEN)
    else:
        d.text((bx + 20, by + 82), "AFTER  window at (7000,1500) width 1200  →  lint clean", font=sans(15, 600), fill=GREEN)

    y = top + banner_h + 16
    if is_vert:
        avail = bottom - y
        a_h = (avail - 12) // 2
        paste_sheet(c, before, (margin, y, w - 2 * margin, a_h), "archlang preview --review  ·  warning ringed on the sheet", crop="trim")
        y = y + a_h + 12
        paste_sheet(c, after, (margin, y, w - 2 * margin, bottom - y), "archlang compile  ·  window restored  ·  lint clean", crop="drawing")
    else:
        gap = 18
        col_w = (w - 2 * margin - gap) // 2
        col_h = bottom - y
        paste_sheet(c, before, (margin, y, col_w, col_h), "BEFORE  ·  preview --review", crop="trim")
        paste_sheet(c, after, (margin + col_w + gap, y, col_w, col_h), "AFTER  ·  compile  ·  lint clean", crop="drawing")
    draw_footer(c, w, h, facts)
    return c


def compose_parametric_alt(w: int, h: int) -> Image.Image:
    """Used only if we want a fourth concept; kept for the parametric video poster if needed."""
    c = new_canvas(w, h)
    header_y = 36
    draw_header(c, w, header_y, "parametric.arch  ·  change COUNT, the row regenerates")
    margin = 48
    top = header_y + 52
    bottom = h - 56
    counts = [2, 3, 4, 5]
    gap = 14
    n = len(counts)
    col_w = (w - 2 * margin - gap * (n - 1)) // n
    col_h = bottom - top
    for i, nunits in enumerate(counts):
        x = margin + i * (col_w + gap)
        img = load(INT / f"plans/parametric-count{nunits}.png")
        paste_sheet(c, img, (x, top, col_w, col_h), f"let COUNT = {nunits}", crop="drawing")
    draw_footer(c, w, h, "for i in 0..COUNT  ·  one number rebuilds the row")
    return c


SIZES = {
    "16x9": (1920, 1080),
    "1x1": (1080, 1080),
    "9x16": (1080, 1920),
}


def save(im: Image.Image, name: str):
    path = OUT / name
    rgb = Image.new("RGB", im.size, (15, 17, 21))
    rgb.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
    rgb.save(path, "PNG", optimize=True)
    print(f"wrote {path} {rgb.size}")
    return path


def main():
    heroes = [
        ("01-code-plan-3d", compose_01),
        ("02-courtyard-plan-3d", compose_02),
        ("03-lint-fix", compose_03),
    ]
    for stem, fn in heroes:
        for label, (w, h) in SIZES.items():
            save(fn(w, h), f"{stem}-{label}.png")


if __name__ == "__main__":
    main()
