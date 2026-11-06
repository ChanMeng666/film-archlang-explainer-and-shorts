#!/usr/bin/env python3
"""v5 chapter scenes — each returns a 1920x1080 (or 1080x1920) RGBA frame."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from engine import (
    W, H, SHEET, PLUM, PLUM_DEEP, INK, WHITE_A, CARD_A, LINE, MUTED, GREEN, RED, AMBER,
    FPS, INT3, INT5, REPLAY, THUMBS, STUDIO_LINES, STUDIO_LINES_COMPACT,
    new_canvas, paste_fit, ken_burns, rounded_card, draw_code, source_char_count,
    ROOMS, LINE_TO_ROOM, room_screen_box, map_room, draw_room_glow, draw_connector,
    draw_progress, draw_header, draw_lower_third, draw_chapter_burst,
    CHAPTERS_META, chapter_starts, remap, spring, ease_in_out_cubic, ease_out_cubic,
    ease_out_quart, pulse, clamp, lerp, text_w, sans, mono, load, crop_main_drawing,
    trim_margins,
)
from compose_v4 import sans as _sans  # already imported via engine

# ---------------------------------------------------------------------------
# Asset cache
# ---------------------------------------------------------------------------
_CACHE = {}


def A(key, loader):
    if key not in _CACHE:
        _CACHE[key] = loader()
    return _CACHE[key]


def studio_plan():
    return A("studio", lambda: crop_main_drawing(load(INT3 / "themes/studio-rendered.png")))


def studio_pres():
    return A("pres", lambda: crop_main_drawing(load(INT3 / "themes/studio-presentation.png")))


def courtyard_plan():
    return A("court", lambda: crop_main_drawing(load(INT3 / "plans/courtyard-house.png")))


def courtyard_3d():
    def _l():
        im = load(INT5.parent.parent / "v4/intermediates/replay/frames/courtyard_3d_last.png")
        # strip chrome-ish bottom
        return im.crop((320, 70, 1590, 994))
    return A("c3d", _l)


def studio_3d():
    def _l():
        im = load(INT5.parent.parent / "v4/intermediates/replay/frames/studio_3d_last.png")
        return im.crop((397, 70, 1521, 994))
    return A("s3d", _l)


def lint_before():
    return A("lintb", lambda: trim_margins(load(INT3 / "lint/studio-nowindow-review.png"), pad=20))


def lint_after():
    return A("linta", lambda: crop_main_drawing(load(INT3 / "plans/studio.png")))


def param_plan(n):
    return A(f"p{n}", lambda: crop_main_drawing(load(INT3 / f"plans/parametric-count{n}.png")))


def replay_frame(i):
    i = int(clamp(i, 0, 287))
    p = REPLAY / f"{i:04d}.png"
    return A(f"r{i}", lambda: load(p))


def thumb(name):
    return A(f"th{name}", lambda: trim_margins(load(THUMBS / name), pad=10))


def apply_chrome(img, t, idx):
    starts, total = chapter_starts()
    meta = CHAPTERS_META[idx]
    _, dur, short, title, why = meta
    local = t - starts[idx]
    draw_progress(img, t, total, img.size[0], img.size[1])
    draw_header(img, idx, len(CHAPTERS_META), short, img.size[0])
    draw_lower_third(img, idx + 1, title, why, local, img.size[0], img.size[1])
    draw_chapter_burst(img, idx + 1, title, local, img.size[0], img.size[1])
    return img


# ---------------------------------------------------------------------------
# Scenes
# ---------------------------------------------------------------------------
def scene_hook(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    plan = courtyard_plan()
    threed = courtyard_3d()
    # Ken Burns: start slightly wide on the plan, push into the courtyard hole
    z = lerp(1.0, 1.22, remap(local, 0.3, 6.4))
    focus = (lerp(0.50, 0.52, remap(local, 0.3, 6.4)),
             lerp(0.48, 0.46, remap(local, 0.3, 6.4)))
    if h > w:
        # stacked
        rounded_card(c, (48, 80, w - 96, int(h * 0.38)), accent=True)
        ken_burns(plan, (60, 92, w - 120, int(h * 0.38) - 24), zoom=z, focus=focus, canvas=c)
        fade3 = remap(local, 1.6, 3.2, ease_out_cubic)
        box = (48, int(h * 0.40) + 96, w - 96, int(h * 0.28))
        rounded_card(c, box, accent=True)
        overlay = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ken_burns(threed, (box[0] + 12, box[1] + 12, box[2] - 24, box[3] - 24),
                  zoom=lerp(1.05, 1.18, fade3), focus=(0.45, 0.48), canvas=overlay)
        if fade3 < 1:
            overlay.putalpha(overlay.split()[-1].point(lambda a: int(a * fade3)))
        c.alpha_composite(overlay)
    else:
        left, right = (40, 72, 1040, 800), (1100, 72, 780, 800)
        rounded_card(c, left, accent=True)
        ken_burns(plan, (left[0] + 10, left[1] + 10, left[2] - 20, left[3] - 20),
                  zoom=z, focus=focus, canvas=c)
        fade3 = remap(local, 0.35, 1.5, ease_out_cubic)
        rounded_card(c, right, accent=True)
        overlay = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ken_burns(threed, (right[0] + 10, right[1] + 10, right[2] - 20, right[3] - 20),
                  zoom=lerp(1.0, 1.16, remap(local, 1.4, 6.5)), focus=(0.46, 0.48), canvas=overlay)
        if fade3 < 1:
            overlay.putalpha(overlay.split()[-1].point(lambda a: int(a * fade3)))
        c.alpha_composite(overlay)
        # proof chip
        u = remap(local, 3.2, 4.2, ease_out_cubic)
        if u > 0:
            d = ImageDraw.Draw(c)
            label = "same courtyard-house.arch"
            tw = text_w(d, label, sans(16, 600))
            x = 1100 + (780 - tw - 40) // 2
            y = 72 + int((1 - u) * 20)
            d.rounded_rectangle([x, y, x + tw + 40, y + 36], 18,
                                fill=(128, 82, 255, int(230 * u)))
            d.text((x + 20, y + 8), label, font=sans(16, 600),
                   fill=(255, 255, 255, int(255 * u)))
    return c


def scene_write(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    total_chars = source_char_count(STUDIO_LINES)
    type_t0, type_t1 = 1.15, dur - 0.6
    typed = int(total_chars * remap(local, type_t0, type_t1, ease_out_quart))
    box = (80, 80, w - 160, h - 220) if h <= w else (48, 80, w - 96, int(h * 0.55))
    draw_code(c, box, STUDIO_LINES, size=18 if h <= w else 16,
              typed=typed, cursor=True, t=local)
    return c


def scene_compile(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    plan = studio_plan()
    # sequence of room highlights after the title
    seq = [
        (1.20, 2.40, 10, "living", 'room id=r_living  ·  Living / Kitchen'),
        (2.40, 3.50, 12, "bedroom", 'room id=r_bed  ·  Bedroom'),
        (3.50, 4.50, 14, "hall", 'room id=r_hall  ·  Hall'),
        (4.50, 5.55, 16, "bath", 'room id=r_bath  ·  Bath'),
    ]
    hl = None
    room = None
    caption = ""
    prog = 0.0
    for a, b, li, rk, cap in seq:
        if a <= local < b:
            hl, room, caption = li, rk, cap
            prog = remap(local, a, a + 0.35, ease_out_cubic)
            break
        if local >= b:
            hl, room, caption = li, rk, cap
            prog = 1.0
    if h > w:
        code_box = (48, 80, w - 96, int(h * 0.34))
        plan_box = (48, int(h * 0.36) + 70, w - 96, int(h * 0.32))
    else:
        code_box = (40, 80, 700, 800)
        plan_box = (760, 80, 1120, 800)
    draw_code(c, code_box, STUDIO_LINES, size=15, highlight=hl, t=local)
    rounded_card(c, plan_box, accent=True)
    inner = (plan_box[0] + 12, plan_box[1] + 12, plan_box[2] - 24, plan_box[3] - 24)
    # slight Ken Burns throughout
    z = lerp(1.0, 1.08, remap(local, 0.4, dur - 0.4))
    ken_burns(plan, inner, zoom=z, focus=(0.48, 0.5), canvas=c)
    if room:
        glow = 50 + 40 * pulse(local, 1.0)
        rx0, ry0, rx1, ry1 = map_room(plan, inner, room, zoom=z, focus=(0.48, 0.5))
        overlay = Image.new("RGBA", c.size, (0, 0, 0, 0))
        dglow = ImageDraw.Draw(overlay)
        dglow.rounded_rectangle([rx0, ry0, rx1, ry1], 10, fill=(128, 82, 255, int(glow)))
        dglow.rounded_rectangle([rx0, ry0, rx1, ry1], 10, outline=PLUM, width=3)
        c.alpha_composite(overlay)
        line_h = 15 + 7
        code_x = code_box[0] + code_box[2] - 18
        code_y = code_box[1] + 14 + (hl or 0) * line_h + line_h / 2
        draw_connector(c, (code_x, code_y), ((rx0 + rx1) / 2, (ry0 + ry1) / 2), progress=prog)
        # callout
        d = ImageDraw.Draw(c)
        u = prog
        tw = text_w(d, caption, sans(15, 600))
        cx = inner[0] + 16
        cy = inner[1] + inner[3] - 48
        d.rounded_rectangle([cx, cy, cx + tw + 28, cy + 34], 8,
                            fill=(128, 82, 255, int(220 * u)))
        d.text((cx + 14, cy + 7), caption, font=sans(15, 600),
               fill=(255, 255, 255, int(255 * u)))
    return c


def scene_themes(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    a, b = studio_plan(), studio_pres()
    # top: two full sheets with a slow push
    z = lerp(1.0, 1.10, remap(local, 0.4, 6.5))
    if h > w:
        rounded_card(c, (40, 80, w - 80, 420), accent=True)
        ken_burns(a, (52, 92, w - 104, 396), zoom=z, focus=(0.35, 0.28), canvas=c)
        return c
    rounded_card(c, (40, 72, 910, 390), accent=True)
    rounded_card(c, (970, 72, 910, 390), accent=True)
    ken_burns(a, (52, 84, 886, 366), zoom=z, focus=(0.35, 0.3), canvas=c)
    ken_burns(b, (982, 84, 886, 366), zoom=z, focus=(0.35, 0.3), canvas=c)
    d = ImageDraw.Draw(c)
    d.text((60, 84), "theme rendered", font=sans(14, 600), fill=PLUM_DEEP)
    d.text((990, 84), "theme presentation", font=sans(14, 600), fill=PLUM_DEEP)
    # zooms reveal after 1.6s
    u = remap(local, 1.5, 2.4, ease_out_cubic)
    # kitchen zooms — focus on sink
    boxes = [
        (40, 480, 445, 400, a, (0.28, 0.22), "zoom  ·  kitchen  ·  rendered"),
        (505, 480, 445, 400, a, (0.28, 0.78), "zoom  ·  sofa  ·  rendered"),
        (970, 480, 445, 400, b, (0.28, 0.22), "zoom  ·  kitchen  ·  presentation"),
        (1435, 480, 445, 400, b, (0.28, 0.78), "zoom  ·  sofa  ·  presentation"),
    ]
    for i, (x, y, bw, bh, im, foc, label) in enumerate(boxes):
        delay = i * 0.08
        uu = remap(local, 1.5 + delay, 2.3 + delay, ease_out_cubic)
        if uu <= 0:
            continue
        yoff = int((1 - uu) * 24)
        rounded_card(c, (x, y + yoff, bw, bh), accent=True)
        ken_burns(im, (x + 10, y + yoff + 36, bw - 20, bh - 48), zoom=2.4, focus=foc, canvas=c)
        d.text((x + 18, y + yoff + 12), label, font=sans(13, 600),
               fill=(88, 48, 196, int(255 * uu)))
    return c


def scene_describe(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    plan = studio_plan()
    if h > w:
        plan_box = (40, 80, w - 80, 520)
    else:
        plan_box = (40, 72, 980, 800)
    rounded_card(c, plan_box, accent=True)
    ken_burns(plan, (plan_box[0] + 12, plan_box[1] + 12, plan_box[2] - 24, plan_box[3] - 24),
              zoom=lerp(1.0, 1.06, remap(local, 0.3, 6.5)), focus=(0.5, 0.5), canvas=c)
    rows = [
        ("Plan", "Studio 1BR", None),
        ("Rooms", "4", 4),
        ("Floor area", "42 m²", 42),
        ("Net area", "38.29 m²", 38.29),
        ("Doors", "3", 3),
        ("Windows", "3", 3),
        ("Reachable", "every room", None),
        ("Warnings", "none", None),
    ]
    card = (1050, 72, 830, 800) if h <= w else (40, 620, w - 80, 520)
    inner = rounded_card(c, card, accent=True)
    d = ImageDraw.Draw(c)
    d.text((card[0] + 28, card[1] + 20), "describe()  ·  --json", font=sans(16, 600), fill=PLUM_DEEP)
    yy = card[1] + 64
    for i, (k, final, numeric) in enumerate(rows):
        appear = remap(local, 1.1 + i * 0.22, 1.1 + i * 0.22 + 0.35, ease_out_cubic)
        if appear <= 0:
            continue
        x = card[0] + 32
        # underline grow
        d.line([(x, yy + 36), (x + int((card[2] - 64) * appear), yy + 36)], fill=LINE, width=1)
        d.text((x, yy), k, font=sans(20, 500), fill=(*MUTED[:3], int(255 * appear)))
        if numeric is not None:
            # count up
            ct = remap(local, 1.1 + i * 0.22, 1.1 + i * 0.22 + 0.9, ease_out_quart)
            val = numeric * ct
            if numeric == 38.29:
                txt = f"{val:.2f} m²"
            elif numeric == 42:
                txt = f"{int(round(val))} m²"
            else:
                txt = f"{int(round(val))}"
        else:
            txt = final
        tw = text_w(d, txt, sans(22, 650))
        d.text((card[0] + card[2] - 32 - tw, yy), txt, font=sans(22, 650),
               fill=(17, 17, 17, int(255 * appear)))
        yy += 86 if h <= w else 54
    return c


def scene_lint(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    before = lint_before()
    if h > w:
        plan_box = (40, 80, w - 80, 700)
    else:
        plan_box = (40, 72, 1180, 800)
    rounded_card(c, plan_box, accent=True)
    inner = (plan_box[0] + 12, plan_box[1] + 12, plan_box[2] - 24, plan_box[3] - 24)
    ken_burns(before, inner, zoom=1.04,
              focus=(0.48, 0.42), canvas=c)
    # pulsing ring around the bedroom (left-of-center on the fitted review sheet)
    ring_u = remap(local, 1.3, 2.0)
    if ring_u > 0:
        overlay = Image.new("RGBA", c.size, (0, 0, 0, 0))
        d = ImageDraw.Draw(overlay)
        cx = inner[0] + inner[2] * 0.445
        cy = inner[1] + inner[3] * 0.30
        rad = 108 + 14 * pulse(local, 0.9)
        width = 5
        alpha = int((90 + 80 * pulse(local, 0.9)) * ring_u)
        d.ellipse([cx - rad, cy - rad, cx + rad, cy + rad], outline=(128, 82, 255, alpha), width=width)
        d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(128, 82, 255, int(200 * ring_u)))
        c.alpha_composite(overlay)
        # callout
        d2 = ImageDraw.Draw(c)
        uu = remap(local, 1.6, 2.3, ease_out_cubic)
        if uu > 0:
            box = (1240, 160, 640, 520) if h <= w else (48, 800, w - 96, 280)
            rounded_card(c, box, accent=True)
            d2 = ImageDraw.Draw(c)
            d2.text((box[0] + 28, box[1] + 28), "BEFORE", font=sans(14, 650),
                    fill=(*RED[:3], int(255 * uu)))
            d2.text((box[0] + 28, box[1] + 64), "W_BEDROOM_NO_WINDOW",
                    font=mono(22, 650), fill=(*AMBER[:3], int(255 * uu)))
            d2.text((box[0] + 28, box[1] + 110), 'Bedroom "Bedroom"', font=sans(20, 500), fill=INK)
            d2.text((box[0] + 28, box[1] + 142), "has no window.", font=sans(20, 500), fill=INK)
            # underline the code name
            tw = text_w(d2, "W_BEDROOM_NO_WINDOW", mono(22, 650))
            ul = remap(local, 1.8, 2.6, ease_out_cubic)
            d2.line([(box[0] + 28, box[1] + 96),
                     (box[0] + 28 + int(tw * ul), box[1] + 96)], fill=PLUM, width=3)
            d2.text((box[0] + 28, box[1] + 210), "The compiler suggests:", font=sans(14, 500), fill=MUTED)
            d2.text((box[0] + 28, box[1] + 248), "window at (7000,1500)", font=mono(18, 500), fill=PLUM_DEEP)
            d2.text((box[0] + 28, box[1] + 280), "width 1200 wall exterior", font=mono(18, 500), fill=PLUM_DEEP)
    return c


def scene_fix(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    # aligned crops so the wipe reveals the new bedroom window, not a layout jump
    before = A("lint_broken_plan", lambda: crop_main_drawing(load(INT3 / "lint/studio-broken.png")))
    after = lint_after()
    if h > w:
        box = (40, 80, w - 80, 820)
    else:
        box = (40, 72, 1240, 800)
    rounded_card(c, box, accent=True)
    inner = (box[0] + 12, box[1] + 12, box[2] - 24, box[3] - 24)
    wipe = remap(local, 1.25, 3.4, ease_in_out_cubic)
    b_img = Image.new("RGBA", (inner[2], inner[3]), SHEET)
    a_img = Image.new("RGBA", (inner[2], inner[3]), SHEET)
    foc, z = (0.58, 0.36), 1.06
    ken_burns(before, (0, 0, inner[2], inner[3]), zoom=z, focus=foc, canvas=b_img)
    ken_burns(after, (0, 0, inner[2], inner[3]), zoom=z, focus=foc, canvas=a_img)
    split = int(inner[2] * wipe)
    combined = b_img.copy()
    if split > 0:
        combined.paste(a_img.crop((0, 0, split, inner[3])), (0, 0))
    c.alpha_composite(combined, (inner[0], inner[1]))
    d = ImageDraw.Draw(c)
    dx = inner[0] + split
    d.rectangle([dx - 2, inner[1], dx + 2, inner[1] + inner[3]], fill=PLUM)
    # AFTER revealed on the left of the divider; BEFORE remains on the right
    if split > 100:
        ax = dx - 118
        d.rounded_rectangle([ax, inner[1] + 16, ax + 102, inner[1] + 50], 8,
                            fill=(28, 122, 68, 220))
        d.text((ax + 22, inner[1] + 22), "AFTER", font=sans(14, 650), fill=WHITE_A)
    if inner[2] - split > 100:
        bx = dx + 16
        d.rounded_rectangle([bx, inner[1] + 16, bx + 118, inner[1] + 50], 8,
                            fill=(176, 36, 36, 220))
        d.text((bx + 18, inner[1] + 22), "BEFORE", font=sans(14, 650), fill=WHITE_A)
    # side proof card
    if h <= w:
        rounded_card(c, (1300, 160, 580, 520), accent=True)
        uu = remap(local, 3.2, 4.1, ease_out_cubic)
        d.text((1328, 188), "AFTER", font=sans(14, 650), fill=GREEN)
        d.text((1328, 230), "lint clean", font=sans(32, 650),
               fill=(28, 122, 68, int(255 * max(uu, 0.4))))
        d.text((1328, 300), "window at (7000,1500)", font=mono(16, 500), fill=INK)
        d.text((1328, 330), "width 1200", font=mono(16, 500), fill=INK)
        d.text((1328, 400), "The east wall of the bedroom", font=sans(18, 500), fill=INK)
        d.text((1328, 430), "now has a window.", font=sans(18, 500), fill=INK)
        d.text((1328, 500), "every room reachable", font=sans(18, 600), fill=GREEN)
    return c


def scene_param(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    # slider from COUNT 2 → 5 over 1.6–7.2s
    u = remap(local, 1.5, 7.0, ease_in_out_cubic)
    count_f = 2 + 3 * u
    # crossfade between floor(count) and ceil
    lo = int(count_f) if count_f < 5 else 5
    hi = min(5, lo + 1)
    lo = max(2, lo)
    frac = count_f - lo if hi != lo else 0
    img_lo, img_hi = param_plan(lo), param_plan(hi)
    if h > w:
        plan_box = (40, 80, w - 80, 700)
        slider_box = (80, 820, w - 160, 80)
    else:
        plan_box = (40, 72, 1240, 720)
        slider_box = (80, 820, 1160, 70)
        # code sidebar
        code = [
            "let WALL = 200",
            "let W    = 4000",
            "let H    = 5000",
            f"let COUNT = {int(round(count_f))}          # change this",
            "for i in 0..COUNT {",
            "  let x = i * W",
            "  wall exterior thickness WALL {",
            "    (x,0) (x+W,0) (x+W,H) (x,H) close",
            "  }",
            '  room at (x, 0) size W x H',
            '       label "{names[i]}"',
            "}",
        ]
        draw_code(c, (1300, 72, 580, 720), code, size=16, highlight=3, t=local)
    rounded_card(c, plan_box, accent=True)
    inner = (plan_box[0] + 12, plan_box[1] + 12, plan_box[2] - 24, plan_box[3] - 24)
    base = Image.new("RGBA", (inner[2], inner[3]), SHEET)
    ken_burns(img_lo, (0, 0, inner[2], inner[3]), zoom=1.02, focus=(0.5, 0.45), canvas=base)
    if frac > 0.02:
        top = Image.new("RGBA", (inner[2], inner[3]), (0, 0, 0, 0))
        ken_burns(img_hi, (0, 0, inner[2], inner[3]), zoom=1.02, focus=(0.5, 0.45), canvas=top)
        top.putalpha(top.split()[-1].point(lambda a: int(a * frac)))
        base.alpha_composite(top)
    c.alpha_composite(base, (inner[0], inner[1]))
    # slider UI
    d = ImageDraw.Draw(c)
    sx, sy, sw, sh = slider_box
    d.rounded_rectangle([sx, sy, sx + sw, sy + sh], 20, fill=CARD_A, outline=LINE)
    d.text((sx + 20, sy + 22), "COUNT", font=sans(14, 600), fill=MUTED)
    track_x0, track_x1 = sx + 120, sx + sw - 80
    track_y = sy + sh // 2
    d.rounded_rectangle([track_x0, track_y - 4, track_x1, track_y + 4], 4, fill=(226, 222, 214, 255))
    fill_x = track_x0 + (track_x1 - track_x0) * ((count_f - 2) / 3)
    d.rounded_rectangle([track_x0, track_y - 4, fill_x, track_y + 4], 4, fill=PLUM)
    for n, label in [(2, "2"), (3, "3"), (4, "4"), (5, "5")]:
        tx = track_x0 + (track_x1 - track_x0) * ((n - 2) / 3)
        d.ellipse([tx - 4, track_y - 4, tx + 4, track_y + 4], fill=PLUM_DEEP)
        d.text((tx - 4, track_y + 12), label, font=sans(12, 500), fill=MUTED)
    d.ellipse([fill_x - 14, track_y - 14, fill_x + 14, track_y + 14], fill=PLUM)
    val = f"{int(round(count_f))}"
    d.text((sx + sw - 50, sy + 18), val, font=sans(22, 650), fill=PLUM_DEEP)
    return c


def scene_rise(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    if h > w:
        # skip the tiny early plan-draw; walls-up fills a tall 9:16 band
        u = remap(local, 0.2, dur - 0.1)
        fi = 140 + u * (287 - 140)
        fr = replay_frame(fi)
        box = (0, 72, w, h - 72 - 168)
        ken_burns(fr, box, zoom=2.45, focus=(0.47, 0.42), canvas=c)
    else:
        u = remap(local, 0.6, dur - 0.15)
        fi = u * 287
        fr = replay_frame(fi)
        c.alpha_composite(fr.resize((w, h), Image.Resampling.BILINEAR), (0, 0))
    return c


def scene_export(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    items = [
        ("SVG", "studio.svg", "vector sheet", "studio-svg.png"),
        ("DXF", "studio.dxf", "CAD wireframe", "studio-dxf.png"),
        ("PDF", "studio.pdf", "printable sheet", "studio-pdf.png"),
        ("PNG", "studio.png", "raster preview", "studio-png.png"),
        ("GLB", "studio.glb", "checked 3D", "studio-glb.png"),
    ]
    # source file icon in the center that stays, cards fan out
    src_u = remap(local, 0.35, 1.0, ease_out_cubic)
    d.rounded_rectangle([860, 430, 1060, 560], 16,
                        fill=(128, 82, 255, int(240 * max(src_u, 0.3))))
    d.text((888, 458), "studio.arch", font=mono(16, 650), fill=WHITE_A)
    d.text((900, 492), "one source", font=sans(14, 500), fill=WHITE_A)
    n = len(items)
    gap = 22
    card_w = (w - 80 - gap * (n - 1)) // n
    cy = 140
    ch = 720
    for i, (fmt, fname, note, fn) in enumerate(items):
        delay = 0.55 + i * 0.12
        u = spring(local - delay, duration=0.85, freq=6.8, decay=6.8)
        if u <= 0:
            continue
        target_x = 40 + i * (card_w + gap)
        # start from canvas center
        x = int(lerp(860, target_x, u))
        y = int(lerp(430, cy, u))
        ww = int(lerp(200, card_w, u))
        hh = int(lerp(130, ch, u))
        if ww < 80 or hh < 80:
            continue
        rounded_card(c, (x, y, ww, hh), accent=True)
        dd = ImageDraw.Draw(c)
        dd.text((x + 18, y + 16), fmt, font=sans(min(28, max(14, ww // 8)), 650), fill=PLUM_DEEP)
        if hh > 70:
            dd.text((x + 18, y + 54), fname, font=mono(13, 500), fill=INK)
        if hh > 90:
            dd.text((x + 18, y + 76), note, font=sans(13, 500), fill=MUTED)
        if hh > 200 and ww > 140:
            im = thumb(fn)
            paste_fit(c, im, (x + 14, y + 108, max(40, ww - 28), max(40, hh - 130),), pad=6)
    return c


def scene_mcp(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    # prompt bubble
    u1 = remap(local, 0.4, 1.2, ease_out_cubic)
    prompt = "Draft a 42 m² one-bed studio in ArchLang, with a window in every room."
    if u1 > 0:
        d.rounded_rectangle([80, 100, 1240, 210], 18,
                            fill=(255, 253, 249, int(255 * u1)), outline=LINE)
        d.rounded_rectangle([80, 100, 160, 210], 18, fill=(128, 82, 255, int(240 * u1)))
        d.text((96, 138), "You", font=sans(16, 650), fill=WHITE_A)
        d.text((180, 128), prompt[: int(len(prompt) * remap(local, 0.5, 2.0, ease_out_quart))],
               font=sans(20, 500), fill=INK)
    tools = [
        ("compile", "npx @chanmeng666/archlang compile studio.arch --json"),
        ("describe", "npx @chanmeng666/archlang describe studio.arch --json"),
        ("lint", "npx @chanmeng666/archlang lint studio.arch --json"),
        ("view", "npx archlang3d view studio.arch --replay --theme light"),
    ]
    yy = 240
    for i, (name, cmd) in enumerate(tools):
        uu = remap(local, 2.0 + i * 0.35, 2.0 + i * 0.35 + 0.4, ease_out_cubic)
        if uu <= 0:
            continue
        xoff = int((1 - uu) * 30)
        d.rounded_rectangle([80 + xoff, yy, 1240 + xoff, yy + 72], 12,
                            fill=CARD_A, outline=LINE)
        d.rounded_rectangle([96 + xoff, yy + 16, 220 + xoff, yy + 56], 8, fill=PLUM)
        tw = text_w(d, name, sans(14, 650))
        d.text((158 + xoff - tw / 2, yy + 26), name, font=sans(14, 650), fill=WHITE_A)
        d.text((240 + xoff, yy + 24), cmd, font=mono(16, 500), fill=INK)
        yy += 88
    # drawing appears
    u3 = remap(local, 3.6, 4.6, ease_out_cubic)
    if u3 > 0:
        plan = studio_plan()
        box = (1300, 100, 580, 760)
        rounded_card(c, box, accent=True)
        overlay = Image.new("RGBA", c.size, (0, 0, 0, 0))
        ken_burns(plan, (box[0] + 12, box[1] + 40, box[2] - 24, box[3] - 56),
                  zoom=lerp(1.12, 1.0, u3), focus=(0.5, 0.5), canvas=overlay)
        overlay.putalpha(overlay.split()[-1].point(lambda a: int(a * u3)))
        c.alpha_composite(overlay)
        d.text((box[0] + 20, box[1] + 12), "drawing from the same source",
               font=sans(13, 600), fill=PLUM_DEEP)
    return c


def scene_end(local, dur, w=W, h=H):
    c = new_canvas(w, h)
    d = ImageDraw.Draw(c)
    u = spring(local, duration=1.0, freq=6.2, decay=6.5)
    title = "ArchLang"
    fnt = sans(74, 650)
    tw = text_w(d, title, fnt)
    d.text(((w - tw) // 2, int(h * 0.32) + int((1 - u) * 24)), title, font=fnt,
           fill=(17, 17, 17, int(255 * min(1, u + 0.1))))
    line = "Designs that compile."
    u2 = remap(local, 0.45, 1.3, ease_out_cubic)
    lw = text_w(d, line, sans(34, 500))
    d.text(((w - lw) // 2, int(h * 0.32) + 100), line, font=sans(34, 500),
           fill=(88, 48, 196, int(255 * u2)))
    url = "archlang.uk"
    u3 = remap(local, 0.9, 1.7, ease_out_cubic)
    uw = text_w(d, url, sans(28, 600))
    d.text(((w - uw) // 2, int(h * 0.32) + 168), url, font=sans(28, 600),
           fill=(17, 17, 17, int(255 * u3)))
    sub = "playground.archlang.uk   ·   @chanmeng666/archlang   ·   archlang3d"
    u4 = remap(local, 1.3, 2.1, ease_out_cubic)
    sw = text_w(d, sub, sans(16, 500))
    d.text(((w - sw) // 2, int(h * 0.32) + 230), sub, font=sans(16, 500),
           fill=(*MUTED[:3], int(255 * u4)))
    return c


SCENES = {
    "hook": scene_hook,
    "write": scene_write,
    "compile": scene_compile,
    "themes": scene_themes,
    "describe": scene_describe,
    "lint": scene_lint,
    "fix": scene_fix,
    "param": scene_param,
    "rise": scene_rise,
    "export": scene_export,
    "mcp": scene_mcp,
    "end": scene_end,
}


def render_explainer_frame(t, w=W, h=H):
    from engine import which_chapter
    idx, local, dur = which_chapter(t)
    key = CHAPTERS_META[idx][0]
    img = SCENES[key](local, dur, w, h)
    return apply_chrome(img, t, idx)
