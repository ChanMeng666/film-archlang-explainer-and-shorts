#!/usr/bin/env python3
"""v5 motion compositor: easing, camera, chrome, drawing helpers."""
from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, "/workspace/archlang-spectacle/pipeline/v4")
from compose_v4 import (  # noqa: E402
    SHEET as SHEET_T, CARD, WHITE, MUTED, LINE, CODE_BG, CODE_KW, CODE_STR,
    CODE_NUM, CODE_CMT, CODE_ID, FOOTER_BG, sans, mono, text_w, highlight_line,
    crop_main_drawing, trim_margins, STUDIO_LINES, STUDIO_LINES_COMPACT,
    load, INT3, INT4,
)

W, H = 1920, 1080
FPS = 24
SHEET = (245, 242, 234, 255)
PLUM = (128, 82, 255, 255)       # #8052ff
PLUM_DEEP = (88, 48, 196, 255)
INK = (17, 17, 17, 255)          # #111111
WHITE_A = (255, 255, 255, 255)
CARD_A = (255, 253, 249, 255)
GREEN = (28, 122, 68, 255)
RED = (176, 36, 36, 255)
AMBER = (168, 96, 12, 255)

ROOT = Path("/workspace/archlang-spectacle")
OUT = ROOT / "output/v5"
INT5 = OUT / "intermediates"
REPLAY = INT5 / "replay3d"
THUMBS = ROOT / "output/v4/intermediates/exports/thumbs"


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_rgb(a, b, t):
    return tuple(int(lerp(a[i], b[i], t)) for i in range(min(len(a), len(b))))


def ease_in_out_cubic(t):
    t = clamp(t)
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


def ease_out_cubic(t):
    t = clamp(t)
    return 1 - pow(1 - t, 3)


def ease_in_cubic(t):
    t = clamp(t)
    return t * t * t


def ease_out_quart(t):
    t = clamp(t)
    return 1 - pow(1 - t, 4)


def ease_in_out_quart(t):
    t = clamp(t)
    return 8 * t * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 4) / 2


def spring(t, duration=0.9, freq=7.5, decay=6.2):
    """0 → 1 with a small overshoot, then settle."""
    if t <= 0:
        return 0.0
    if t >= duration:
        return 1.0
    u = t / duration
    return 1 - math.exp(-decay * u) * math.cos(freq * math.pi * u)


def pulse(t, period=1.2):
    return 0.5 + 0.5 * math.sin(2 * math.pi * t / period)


def remap(t, t0, t1, ease=ease_in_out_cubic):
    if t1 <= t0:
        return 1.0 if t >= t1 else 0.0
    return ease(clamp((t - t0) / (t1 - t0)))


def new_canvas(w=W, h=H):
    return Image.new("RGBA", (w, h), SHEET)


def paste_fit(canvas, im, box, pad=8, fill=None):
    x, y, w, h = box
    if fill:
        d = ImageDraw.Draw(canvas)
        d.rounded_rectangle([x, y, x + w, y + h], 14, fill=fill)
    im = im.convert("RGBA")
    iw, ih = im.size
    scale = min((w - pad * 2) / max(iw, 1), (h - pad * 2) / max(ih, 1))
    nw, nh = max(1, int(iw * scale)), max(1, int(ih * scale))
    px = x + (w - nw) // 2
    py = y + (h - nh) // 2
    canvas.alpha_composite(im.resize((nw, nh), Image.Resampling.LANCZOS), (px, py))
    return px, py, nw, nh


def ken_burns(im, box, zoom=1.0, focus=(0.5, 0.5), canvas=None):
    """Fit `im` into `box`, then zoom into `focus` (normalized). zoom=1 is contain."""
    x, y, w, h = box
    im = im.convert("RGBA")
    iw, ih = im.size
    contain = min(w / max(iw, 1), h / max(ih, 1))
    z = max(contain * zoom, 1e-6)
    nw, nh = max(1, int(iw * z)), max(1, int(ih * z))
    scaled = im.resize((nw, nh), Image.Resampling.BILINEAR)
    fx, fy = focus
    cx, cy = nw * fx, nh * fy
    left = int(cx - w / 2)
    top = int(cy - h / 2)
    left = max(0, min(left, max(0, nw - w)))
    top = max(0, min(top, max(0, nh - h)))
    cropped = scaled.crop((left, top, left + w, top + h))
    if cropped.size != (w, h):
        bg = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        bg.paste(cropped, ((w - cropped.size[0]) // 2, (h - cropped.size[1]) // 2))
        cropped = bg
    if canvas is not None:
        canvas.alpha_composite(cropped, (x, y))
    return cropped


def rounded_card(canvas, box, radius=16, fill=CARD_A, outline=LINE, accent=False):
    x, y, w, h = box
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x + 3, y + 5, x + w + 3, y + h + 5], radius, fill=(214, 208, 196, 70))
    d.rounded_rectangle([x, y, x + w, y + h], radius, fill=fill, outline=outline, width=1)
    if accent:
        d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    return (x + 16, y + 16, w - 32, h - 32)


def draw_code(canvas, box, lines, size=15, highlight=None, typed=None, cursor=False, t=0.0):
    """Draw syntax-highlighted code. `typed` = visible character count; `highlight` = line index."""
    x, y, w, h = box
    d = ImageDraw.Draw(canvas)
    d.rounded_rectangle([x + 3, y + 5, x + w + 3, y + h + 5], 14, fill=(214, 208, 196, 70))
    d.rounded_rectangle([x, y, x + w, y + h], 14, fill=CODE_BG, outline=LINE)
    d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    fnt = mono(size, 450)
    ln_fnt = mono(max(size - 1, 11), 400)
    line_h = size + 7
    # apply typing mask
    vis = list(lines)
    if typed is not None:
        acc = 0
        out = []
        for line in lines:
            if acc + len(line) + 1 <= typed:
                out.append(line)
                acc += len(line) + 1
            else:
                remain = max(0, typed - acc)
                out.append(line[:remain])
                break
        vis = out
    max_lines = max(1, (h - 24) // line_h)
    vis = vis[:max_lines]
    cx = x + 16
    cy = y + 14
    gutter = text_w(d, "000", ln_fnt) + 12
    last_tx = cx + gutter
    last_cy = cy
    for i, line in enumerate(vis):
        if highlight is not None and i == highlight:
            d.rounded_rectangle(
                [x + 10, cy - 2, x + w - 12, cy + line_h - 2],
                6, fill=(128, 82, 255, 38),
            )
            d.rectangle([x + 6, cy - 2, x + 10, cy + line_h - 2], fill=PLUM)
        no = f"{i + 1:02d}"
        d.text((cx, cy), no, font=ln_fnt, fill=(168, 170, 176, 255))
        tx = cx + gutter
        for seg, col in highlight_line(line):
            d.text((tx, cy), seg, font=fnt, fill=col)
            tx += text_w(d, seg, fnt)
        last_tx, last_cy = tx, cy
        cy += line_h
    if cursor and vis is not None:
        on = (int(t * 2) % 2) == 0
        if on:
            d.rectangle([last_tx + 1, last_cy + 2, last_tx + 8, last_cy + line_h - 4], fill=PLUM)
    return vis


def source_char_count(lines):
    return sum(len(ln) + 1 for ln in lines)


# Room boxes as fractions of the cropped studio sheet (incl. dims).
ROOMS = {
    "living": (0.07, 0.11, 0.52, 0.88),
    "bedroom": (0.50, 0.14, 0.74, 0.49),
    "hall": (0.50, 0.49, 0.74, 0.67),
    "bath": (0.50, 0.67, 0.74, 0.88),
    "kitchen": (0.09, 0.12, 0.48, 0.34),
    "sofa": (0.10, 0.66, 0.42, 0.86),
}

# Line index in STUDIO_LINES → room key
LINE_TO_ROOM = {
    10: "living", 11: "living",
    12: "bedroom", 13: "bedroom",
    14: "hall", 15: "hall",
    16: "bath", 17: "bath",
}


def room_screen_box(plan_box, key):
    x, y, w, h = plan_box
    fx0, fy0, fx1, fy1 = ROOMS[key]
    return (x + fx0 * w, y + fy0 * h, x + fx1 * w, y + fy1 * h)


def map_room(im, box, key, zoom=1.0, focus=(0.5, 0.5)):
    """Map a ROOMS fraction through the same contain/zoom/crop as ken_burns."""
    x, y, w, h = box
    iw, ih = im.size
    contain = min(w / max(iw, 1), h / max(ih, 1))
    z = max(contain * zoom, 1e-6)
    nw, nh = iw * z, ih * z
    fx, fy = focus
    left = nw * fx - w / 2
    top = nh * fy - h / 2
    left = max(0.0, min(left, max(0.0, nw - w)))
    top = max(0.0, min(top, max(0.0, nh - h)))
    if nw >= w:
        ox = x - left
    else:
        ox = x + (w - nw) / 2.0
    if nh >= h:
        oy = y - top
    else:
        oy = y + (h - nh) / 2.0
    fx0, fy0, fx1, fy1 = ROOMS[key]
    return (ox + fx0 * nw, oy + fy0 * nh, ox + fx1 * nw, oy + fy1 * nh)


def draw_room_glow(canvas, plan_box, key, alpha=90):
    x0, y0, x1, y1 = room_screen_box(plan_box, key)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rounded_rectangle([x0, y0, x1, y1], 10, fill=(128, 82, 255, int(alpha)))
    d.rounded_rectangle([x0, y0, x1, y1], 10, outline=PLUM, width=3)
    canvas.alpha_composite(overlay)


def draw_connector(canvas, p0, p1, progress=1.0, width=3):
    progress = clamp(progress)
    if progress <= 0:
        return
    x0, y0 = p0
    x1, y1 = p1
    # eased endpoint along a slight curve (quad bezier via mid bump)
    mx = (x0 + x1) / 2
    my = (y0 + y1) / 2 - 40
    # sample curve up to progress
    pts = []
    steps = 24
    n = max(2, int(steps * progress))
    for i in range(n + 1):
        u = i / steps
        # quadratic bezier
        bx = (1 - u) ** 2 * x0 + 2 * (1 - u) * u * mx + u ** 2 * x1
        by = (1 - u) ** 2 * y0 + 2 * (1 - u) * u * my + u ** 2 * y1
        pts.append((bx, by))
    d = ImageDraw.Draw(canvas)
    if len(pts) >= 2:
        d.line(pts, fill=PLUM, width=width, joint="curve")
    # arrow head at tip
    if progress > 0.85 and len(pts) >= 2:
        ax, ay = pts[-1]
        bx, by = pts[-2]
        ang = math.atan2(ay - by, ax - bx)
        s = 10
        d.polygon([
            (ax, ay),
            (ax - s * math.cos(ang - 0.45), ay - s * math.sin(ang - 0.45)),
            (ax - s * math.cos(ang + 0.45), ay - s * math.sin(ang + 0.45)),
        ], fill=PLUM)
    # endpoints
    d.ellipse([x0 - 5, y0 - 5, x0 + 5, y0 + 5], fill=PLUM)
    if progress > 0.9:
        d.ellipse([x1 - 6, y1 - 6, x1 + 6, y1 + 6], fill=PLUM)


def draw_progress(canvas, t, total, w=W, h=H):
    d = ImageDraw.Draw(canvas)
    d.rectangle([0, 0, w, 6], fill=(226, 222, 214, 255))
    d.rectangle([0, 0, int(w * clamp(t / max(total, 0.01))), 6], fill=PLUM)


def draw_header(canvas, chapter_i, n_chapters, chapter_name, w=W):
    d = ImageDraw.Draw(canvas)
    d.text((40, 18), "ArchLang", font=sans(26, 650), fill=INK)
    bw = text_w(d, "ArchLang", sans(26, 650))
    d.text((40 + bw + 14, 26), "Designs that compile.", font=sans(15, 500), fill=PLUM_DEEP)
    label = f"{chapter_i + 1:02d}  /  {n_chapters:02d}   ·   {chapter_name}"
    lw = text_w(d, label, sans(15, 600))
    d.text((w - 40 - lw, 26), label, font=sans(15, 600), fill=MUTED)


def draw_lower_third(canvas, num, title, why, t_local, w=W, h=H):
    """Slides up and fades in over the first 0.7s of a chapter."""
    u = spring(t_local, duration=0.85, freq=6.5, decay=6.5)
    slide = int((1 - u) * 36)
    alpha_bg = int(230 * min(1, u + 0.15))
    y0 = h - 108 + slide
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    d.rectangle([0, y0, w, h + 8], fill=(236, 232, 222, alpha_bg))
    d.rectangle([0, y0, 8, h + 8], fill=PLUM)
    # number badge
    badge = f"{num:02d}"
    d.rounded_rectangle([32, y0 + 22, 96, y0 + 78], 10, fill=PLUM)
    tw = text_w(d, badge, sans(26, 650))
    d.text((64 - tw / 2, y0 + 32), badge, font=sans(26, 650), fill=WHITE_A)
    d.text((112, y0 + 20), title, font=sans(26, 650), fill=INK)
    d.text((112, y0 + 56), why, font=sans(16, 500), fill=MUTED)
    mark = "archlang.uk"
    d.text((w - 40 - text_w(d, mark, sans(14, 600)), y0 + 58), mark, font=sans(14, 600), fill=PLUM_DEEP)
    canvas.alpha_composite(overlay)


def draw_chapter_burst(canvas, num, title, t_local, w=W, h=H):
    """Large kinetic chapter number for the opening ~1s, then fades."""
    if t_local > 1.25:
        return
    fade = 1.0 if t_local < 0.7 else clamp(1 - (t_local - 0.7) / 0.55)
    s = spring(t_local, duration=0.7, freq=7.0, decay=7.0)
    overlay = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(overlay)
    # veil so type reads
    d.rectangle([0, 70, 520, 260], fill=(245, 242, 234, int(140 * fade)))
    ntxt = f"{num:02d}"
    fnt = sans(int(72 + 18 * (1 - s)), 650)
    d.text((48, 86), ntxt, font=fnt, fill=(128, 82, 255, int(255 * fade)))
    d.text((48 + text_w(d, ntxt, fnt) + 16, 128), title, font=sans(28, 600),
           fill=(17, 17, 17, int(255 * fade)))
    canvas.alpha_composite(overlay)


CHAPTERS_META = [
    # (id, duration, short name, display title, why-it-matters)
    ("hook", 7.0, "Hook", "A language for floor plans",
     "Why it matters — one file becomes a precise sheet and a 3D model."),
    ("write", 9.5, "Write", "Write the building as text",
     "Why it matters — rooms, walls and openings are source you can diff."),
    ("compile", 7.0, "Compile", "The compiler draws the sheet",
     "Why it matters — the same source always produces the same drawing."),
    ("themes", 7.0, "Themes", "Restyle, don’t redraw",
     "Why it matters — inks and fills change; measurements never do."),
    ("describe", 7.0, "Describe", "Facts, not a guess",
     "Why it matters — areas and reachability come back as data an agent can read."),
    ("lint", 7.0, "Lint", "Catch the missing window",
     "Why it matters — every warning has a code, and often a ready fix."),
    ("fix", 6.0, "Fix", "Suggest, apply, compile again",
     "Why it matters — the review ring disappears when the source is corrected."),
    ("param", 8.0, "Parametric", "Change one number",
     "Why it matters — a loop writes the row; you don’t copy rooms by hand."),
    ("rise", 12.0, "archlang3d", "The plan draws itself",
     "Why it matters — walls rise from the same source, in daylight."),
    ("export", 7.0, "Export", "One source, five formats",
     "Why it matters — SVG, DXF, PDF, PNG and a checked GLB fan out from one file."),
    ("mcp", 7.0, "MCP", "The compiler is the agent interface",
     "Why it matters — an agent writes ArchLang, calls tools, and reads the facts."),
    ("end", 6.5, "End", "Designs that compile.",
     "archlang.uk  ·  playground.archlang.uk  ·  @chanmeng666/archlang"),
]


def chapter_starts():
    t = 0.0
    out = []
    for meta in CHAPTERS_META:
        out.append(t)
        t += meta[1]
    return out, t


def which_chapter(t):
    starts, total = chapter_starts()
    for i, s in enumerate(starts):
        d = CHAPTERS_META[i][1]
        if t < s + d - 1e-6 or i == len(starts) - 1:
            return i, t - s, d
    return len(starts) - 1, 0.0, CHAPTERS_META[-1][1]
