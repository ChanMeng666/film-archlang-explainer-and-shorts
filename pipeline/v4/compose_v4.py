#!/usr/bin/env python3
"""v4 bright stills: Sheet background, light code, light archlang3d frames."""
from __future__ import annotations

import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/archlang-spectacle")
INT3 = ROOT / "output/v3/intermediates"
INT4 = ROOT / "output/v4/intermediates"
OUT = ROOT / "output/v4/stills"
OUT.mkdir(parents=True, exist_ok=True)

SHEET = (245, 242, 234, 255)
WHITE = (255, 255, 255, 255)
CARD = (255, 253, 249, 255)
INK = (22, 24, 28, 255)
MUTED = (92, 96, 104, 255)
PLUM = (128, 82, 255, 255)
PLUM_DEEP = (88, 48, 196, 255)
LINE = (216, 210, 200, 255)
CODE_BG = (252, 250, 246, 255)
CODE_KW = (92, 48, 176, 255)
CODE_STR = (158, 96, 32, 255)
CODE_NUM = (16, 110, 168, 255)
CODE_CMT = (122, 126, 134, 255)
CODE_ID = (28, 32, 38, 255)
GREEN = (28, 122, 68, 255)
RED = (176, 36, 36, 255)
AMBER = (168, 96, 12, 255)
FOOTER_BG = (236, 232, 222, 255)

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
    return Image.new("RGBA", (w, h), SHEET)


def text_w(draw: ImageDraw.ImageDraw, text: str, fnt) -> int:
    return int(draw.textlength(text, font=fnt))


def trim_margins(im: Image.Image, pad: int = 18, ink_below: int = 246) -> Image.Image:
    rgb = im.convert("RGB")
    arr = np.asarray(rgb)
    mx = arr.max(axis=2)
    mn = arr.min(axis=2)
    near_white = (mn > ink_below) & (mx > ink_below)
    ink = ~near_white
    if not ink.any():
        return im.convert("RGBA")
    ys, xs = np.where(ink)
    x0, x1 = max(0, xs.min() - pad), min(arr.shape[1], xs.max() + pad + 1)
    y0, y1 = max(0, ys.min() - pad), min(arr.shape[0], ys.max() + pad + 1)
    return im.convert("RGBA").crop((int(x0), int(y0), int(x1), int(y1)))


def crop_main_drawing(im: Image.Image, pad: int = 16) -> Image.Image:
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


def trim_near_bg(im: Image.Image, pad: int = 16, tol: int = 14) -> Image.Image:
    arr = np.asarray(im.convert("RGB"))
    h, w = arr.shape[:2]
    border = np.concatenate([
        arr[:8, :].reshape(-1, 3),
        arr[-8:, :].reshape(-1, 3),
        arr[:, :8].reshape(-1, 3),
        arr[:, -8:].reshape(-1, 3),
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


def crop_replay_caption(im: Image.Image, bottom: int = 72) -> Image.Image:
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


def card(canvas: Image.Image, box, title: str) -> tuple[int, int, int, int]:
    x, y, w, h = box
    d = ImageDraw.Draw(canvas)
    # soft drop
    d.rounded_rectangle([x + 3, y + 5, x + w + 3, y + h + 5], 16, fill=(214, 208, 196, 90))
    d.rounded_rectangle([x, y, x + w, y + h], 16, fill=CARD, outline=LINE, width=1)
    d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    d.text((x + 18, y + 12), title, font=sans(16, 600), fill=MUTED)
    return (x + 14, y + 42, w - 28, h - 56)


def paste_sheet(canvas: Image.Image, im: Image.Image, box, title: str, crop="drawing"):
    inner = card(canvas, box, title)
    if crop == "drawing":
        im = crop_main_drawing(im)
    elif crop == "trim":
        im = trim_margins(im)
    x, y, w, h = inner
    pad = 10
    im = im.convert("RGBA")
    iw, ih = im.size
    scale = min((w - pad * 2) / max(iw, 1), (h - pad * 2) / max(ih, 1))
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    px = x + (w - nw) // 2
    py = y + (h - nh) // 2
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([px - 8, py - 8, px + nw + 8, py + nh + 8], 8, fill=WHITE, outline=(228, 222, 212, 255))
    canvas.alpha_composite(im.resize((nw, nh), Image.Resampling.LANCZOS), (px, py))


def crop_replay_model(im: Image.Image) -> Image.Image:
    """Strip replay chrome, then tightly crop the building."""
    im = im.convert("RGBA")
    w, h = im.size
    top, bottom = 70, 88
    im = im.crop((0, top, w, max(top + 1, h - bottom)))
    return trim_near_bg(im, pad=12, tol=10)


def paste_3d(canvas: Image.Image, im: Image.Image, box, title: str):
    inner = card(canvas, box, title)
    im = crop_replay_model(im)
    fit_contain(im, inner, canvas, pad=4)


DIM_CROP = (520, 100, 1480, 222)  # courtyard top dimension numerals only


def paste_dim_inset(canvas: Image.Image, plan: Image.Image, box, title="zoom  ·  overall width  16 300 mm"):
    x, y, w, h = box
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x + 3, y + 5, x + w + 3, y + h + 5], 12, fill=(214, 208, 196, 90))
    d.rounded_rectangle([x, y, x + w, y + h], 12, fill=CARD, outline=PLUM, width=2)
    d.text((x + 14, y + 8), title, font=sans(14, 600), fill=PLUM_DEEP)
    crop = plan.convert("RGBA").crop(DIM_CROP)
    inner_x, inner_y = x + 12, y + 30
    inner_w, inner_h = w - 24, h - 40
    iw, ih = crop.size
    scale = min(inner_w / max(iw, 1), inner_h / max(ih, 1))
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    px = inner_x + (inner_w - nw) // 2
    py = inner_y + (inner_h - nh) // 2
    d.rounded_rectangle([px - 4, py - 4, px + nw + 4, py + nh + 4], 6, fill=WHITE)
    canvas.alpha_composite(crop.resize((nw, nh), Image.Resampling.LANCZOS), (px, py))


def highlight_line(text: str) -> list[tuple[str, tuple]]:
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
    d.rounded_rectangle([x + 3, y + 5, x + w + 3, y + h + 5], 14, fill=(214, 208, 196, 80))
    d.rounded_rectangle([x, y, x + w, y + h], 14, fill=CODE_BG, outline=LINE)
    d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    fnt = mono(size, 450)
    ln_fnt = mono(max(size - 1, 12), 400)
    line_h = size + 7
    max_lines = max(1, (h - 24) // line_h)
    shown = lines[:max_lines]
    cx = x + 16
    cy = y + 12
    gutter = text_w(d, "000", ln_fnt) + 12
    for i, line in enumerate(shown):
        no = f"{start_no + i:02d}"
        d.text((cx, cy), no, font=ln_fnt, fill=(168, 170, 176, 255))
        tx = cx + gutter
        for seg, col in highlight_line(line):
            d.text((tx, cy), seg, font=fnt, fill=col)
            tx += text_w(d, seg, fnt)
        cy += line_h
    return len(shown)


def draw_header(canvas, w, y, subtitle: str):
    d = ImageDraw.Draw(canvas)
    d.text((48, y), "ArchLang", font=sans(28, 650), fill=INK)
    brand_w = text_w(d, "ArchLang", sans(28, 650))
    d.text((48 + brand_w + 16, y + 8), "Designs that compile.", font=sans(16, 500), fill=PLUM_DEEP)
    sw = text_w(d, subtitle, sans(15, 500))
    d.text((w - 48 - sw, y + 10), subtitle, font=sans(15, 500), fill=MUTED)
    return y + 44


def draw_footer(canvas, w, h, text: str):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, h - 48, w, h], fill=FOOTER_BG)
    d.text((48, h - 32), text, font=sans(14, 500), fill=MUTED)
    mark = "archlang.uk"
    mw = text_w(d, mark, sans(14, 600))
    d.text((w - 48 - mw, h - 32), mark, font=sans(14, 600), fill=PLUM_DEEP)


# Full studio excerpt used on 16:9 (tall code column).
STUDIO_LINES = [
    'plan "Studio 1BR" {',
    "  units mm",
    "  scale 1:50",
    "  wall exterior thickness 200 {",
    "    (0,0) (7000,0) (7000,6000) (0,6000) close",
    "  }",
    "  wall partition thickness 100 {",
    "    (4000,0) (4000,6000)",
    "  }",
    "",
    "  room id=r_living at (0,0)       size 4000x6000",
    '       label "Living / Kitchen"',
    "  room id=r_bed    at (4000,0)    size 3000x3000",
    '       label "Bedroom"',
    "  room id=r_hall   at (4000,3000) size 3000x1400",
    '       label "Hall"',
    "  room id=r_bath   at (4000,4400) size 3000x1600",
    '       label "Bath"',
    "",
    "  door id=d_main at (3000,6000) width 1000",
    "  window at (0,2000)    width 1500",
    "  window at (7000,1500) width 1200",
    "  furniture bed at (4300,300) size 1500x2000",
    "}",
]

# Complete snippet, fewer lines — used on 1:1 and 9:16 so nothing is cropped.
STUDIO_LINES_COMPACT = [
    'plan "Studio 1BR" {',
    "  units mm",
    "  scale 1:50",
    "  wall exterior thickness 200 {",
    "    (0,0) (7000,0) (7000,6000) (0,6000) close",
    "  }",
    "  wall partition thickness 100 { (4000,0) (4000,6000) }",
    '  room id=r_living at (0,0) size 4000x6000 label "Living / Kitchen"',
    '  room id=r_bed at (4000,0) size 3000x3000 label "Bedroom"',
    '  room id=r_hall at (4000,3000) size 3000x1400 label "Hall"',
    '  room id=r_bath at (4000,4400) size 3000x1600 label "Bath"',
    "  door id=d_main at (3000,6000) width 1000",
    "  window at (0,2000) width 1500",
    "  window at (7000,1500) width 1200",
    "  furniture bed at (4300,300) size 1500x2000",
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
    footer_h = 48
    facts = "4 rooms  ·  42 m²  ·  3 doors  ·  3 windows  ·  every room reachable"
    margin = 48 if not is_vert else 64
    top = header_y + 52
    bottom = h - footer_h - 12
    plan = load(INT3 / "themes/studio-rendered.png")
    threed = load(INT4 / "replay/frames/studio_3d_last.png")

    if is_vert:
        avail = bottom - top
        code_h = int(avail * 0.30)
        plan_h = int(avail * 0.38)
        rest = avail - code_h - plan_h - 24
        d.text((margin, top - 22), "studio.arch", font=sans(16, 600), fill=MUTED)
        shown = draw_code(c, (margin, top + 4, w - 2 * margin, code_h - 4), STUDIO_LINES_COMPACT, size=16)
        if shown < len(STUDIO_LINES_COMPACT):
            raise SystemExit(f"9:16 code crop: shown {shown}")
        y = top + code_h + 12
        paste_sheet(c, plan, (margin, y, w - 2 * margin, plan_h), "archlang compile  →  PNG  ·  theme rendered")
        y = y + plan_h + 12
        paste_3d(c, threed, (margin, y, w - 2 * margin, rest), "archlang3d view --replay --theme light")
    elif is_sq:
        code_h = 420
        d.text((margin, top - 22), "studio.arch", font=sans(16, 600), fill=MUTED)
        shown = draw_code(c, (margin, top, w - 2 * margin, code_h), STUDIO_LINES_COMPACT, size=15)
        if shown < len(STUDIO_LINES_COMPACT):
            raise SystemExit(f"1:1 code crop: shown {shown} / {len(STUDIO_LINES_COMPACT)}")
        y = top + code_h + 16
        col_h = bottom - y
        gap = 16
        col_w = (w - 2 * margin - gap) // 2
        paste_sheet(c, plan, (margin, y, col_w, col_h), "archlang compile  →  PNG")
        paste_3d(c, threed, (margin + col_w + gap, y, col_w, col_h), "archlang3d view --replay — light")
    else:
        gap = 18
        avail_w = w - 2 * margin - 2 * gap
        code_w = int(avail_w * 0.28)
        plan_w = int(avail_w * 0.42)
        three_w = avail_w - code_w - plan_w
        box_h = bottom - top
        d.text((margin, top - 22), "studio.arch", font=sans(16, 600), fill=MUTED)
        draw_code(c, (margin, top, code_w, box_h), STUDIO_LINES, size=15)
        paste_sheet(c, plan, (margin + code_w + gap, top, plan_w, box_h), "archlang compile  →  PNG  ·  theme rendered")
        paste_3d(c, threed, (margin + code_w + gap + plan_w + gap, top, three_w, box_h), "archlang3d view --replay — light")
    draw_footer(c, w, h, facts)
    return c


def compose_02(w: int, h: int) -> Image.Image:
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    is_vert = h > w
    is_sq = abs(w - h) < 8
    header_y = 36 if not is_vert else 48
    draw_header(c, w, header_y, "courtyard-house.arch  ·  official example")
    footer_h = 48
    facts = "11 rooms  ·  163 m²  ·  16.3 × 11.8 m  ·  the courtyard is a hole, not a room"
    margin = 48 if not is_vert else 64
    top = header_y + 52
    bottom = h - footer_h - 12
    plan = load(INT3 / "plans/courtyard-house.png")
    threed = load(INT4 / "replay/frames/courtyard_3d_last.png")

    if is_vert:
        avail = bottom - top
        quote_h = 92
        plan_h = int((avail - quote_h) * 0.56)
        three_h = avail - quote_h - plan_h - 24
        d.text((margin, top), "The courtyard is not a room.", font=sans(20, 600), fill=INK)
        d.text((margin, top + 34), "Nothing is declared there — it is the hole the building wraps around.", font=sans(16, 500), fill=MUTED)
        inset_h = 138
        three_h = max(220, three_h - inset_h - 12)
        y = top + quote_h
        paste_sheet(c, plan, (margin, y, w - 2 * margin, plan_h), "archlang compile  →  dimensioned sheet")
        y = y + plan_h + 10
        paste_dim_inset(c, plan, (margin, y, w - 2 * margin, inset_h))
        y = y + inset_h + 12
        paste_3d(c, threed, (margin, y, w - 2 * margin, three_h), "archlang3d view --replay --theme light")
    elif is_sq:
        quote_h = 70
        d.text((margin, top), "The courtyard is not a room — it is the hole the building wraps around.", font=sans(18, 500), fill=INK)
        y = top + quote_h
        col_h = bottom - y
        gap = 16
        col_w = (w - 2 * margin - gap) // 2
        paste_sheet(c, plan, (margin, y, col_w, col_h), "archlang compile  →  sheet")
        paste_3d(c, threed, (margin + col_w + gap, y, col_w, col_h), "archlang3d — light")
        paste_dim_inset(c, plan, (margin + 8, bottom - 152, col_w - 16, 140))
    else:
        gap = 18
        avail_w = w - 2 * margin - gap
        plan_w = int(avail_w * 0.56)
        three_w = avail_w - plan_w
        box_h = bottom - top
        inset_h = 150
        paste_sheet(c, plan, (margin, top, plan_w, box_h - inset_h - 12), "archlang compile  →  PNG  ·  courtyard-house.arch")
        paste_dim_inset(c, plan, (margin, top + box_h - inset_h, plan_w, inset_h))
        paste_3d(c, threed, (margin + plan_w + gap, top, three_w, box_h), "archlang3d view --replay — same building, light")
    draw_footer(c, w, h, facts)
    return c


def compose_03(w: int, h: int) -> Image.Image:
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    is_vert = h > w
    header_y = 36 if not is_vert else 48
    draw_header(c, w, header_y, "archlang preview --review   then   lint  ·  suggest  ·  compile")
    footer_h = 48
    facts = "W_BEDROOM_NO_WINDOW  ·  fix: add a window on an exterior wall of the room"
    margin = 48 if not is_vert else 64
    top = header_y + 52
    bottom = h - footer_h - 12
    before = load(INT3 / "lint/studio-nowindow-review.png")
    after = load(INT3 / "plans/studio.png")

    banner_h = 84 if not is_vert else 118
    bx, by, bw = margin, top, w - 2 * margin
    d.rounded_rectangle([bx, by, bx + bw, by + banner_h], 14, fill=(255, 244, 238, 255), outline=(220, 180, 168, 255))
    d.text((bx + 20, by + 12), "BEFORE", font=sans(13, 650), fill=RED)
    d.text((bx + 20, by + 34), "W_BEDROOM_NO_WINDOW", font=mono(20 if not is_vert else 18, 600), fill=AMBER)
    d.text((bx + 20, by + (58 if not is_vert else 62)), 'Bedroom "Bedroom" has no window.', font=sans(15, 500), fill=INK)
    after_l = "AFTER   window at (7000,1500) width 1200   →  lint clean"
    if not is_vert:
        aw = text_w(d, after_l, sans(15, 600))
        d.text((bx + bw - aw - 20, by + 34), after_l, font=sans(15, 600), fill=GREEN)
    else:
        d.text((bx + 20, by + 88), after_l, font=sans(15, 600), fill=GREEN)

    y = top + banner_h + 16
    if is_vert:
        avail = bottom - y
        a_h = (avail - 12) // 2
        paste_sheet(c, before, (margin, y, w - 2 * margin, a_h), "archlang preview --review  ·  warning ringed on the sheet", crop="trim")
        y = y + a_h + 12
        paste_sheet(c, after, (margin, y, w - 2 * margin, bottom - y), "archlang compile  ·  window restored  ·  lint clean")
    else:
        gap = 18
        col_w = (w - 2 * margin - gap) // 2
        col_h = bottom - y
        paste_sheet(c, before, (margin, y, col_w, col_h), "BEFORE  ·  preview --review", crop="trim")
        paste_sheet(c, after, (margin + col_w + gap, y, col_w, col_h), "AFTER  ·  compile  ·  lint clean")
    draw_footer(c, w, h, facts)
    return c


SIZES = {
    "16x9": (1920, 1080),
    "1x1": (1080, 1080),
    "9x16": (1080, 1920),
}


def save(im: Image.Image, name: str):
    path = OUT / name
    rgb = Image.new("RGB", im.size, (245, 242, 234))
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
