#!/usr/bin/env python3
"""Generate bright 1080p chapter slides for the v4 explainer and vertical cutdown."""
from __future__ import annotations
import sys
sys.path.insert(0, "/workspace/archlang-spectacle/pipeline/v4")
from pathlib import Path
from PIL import Image, ImageDraw
from compose_v4 import (
    SHEET, WHITE, CARD, INK, MUTED, PLUM, PLUM_DEEP, LINE, CODE_BG, GREEN, RED, AMBER,
    FOOTER_BG, sans, mono, text_w, new_canvas, card, paste_sheet, paste_3d, draw_code,
    STUDIO_LINES, load, crop_main_drawing, INT3, INT4, paste_dim_inset, trim_margins,
)

SLIDES = Path("/workspace/archlang-spectacle/output/v4/intermediates/frames")
SLIDES.mkdir(parents=True, exist_ok=True)
W, H = 1920, 1080


def caption_bar(c, title, body):
    d = ImageDraw.Draw(c)
    d.rectangle([0, H - 118, W, H], fill=FOOTER_BG)
    d.rectangle([0, H - 118, 8, H], fill=PLUM)
    d.text((40, H - 104), title, font=sans(22, 650), fill=INK)
    d.text((40, H - 68), body, font=sans(28, 500), fill=INK)
    d.text((W - 40 - text_w(d, "archlang.uk", sans(16, 600)), H - 48), "archlang.uk", font=sans(16, 600), fill=PLUM_DEEP)


def header(c, subtitle=""):
    d = ImageDraw.Draw(c)
    d.text((40, 28), "ArchLang", font=sans(30, 650), fill=INK)
    bw = text_w(d, "ArchLang", sans(30, 650))
    d.text((40 + bw + 16, 38), "Designs that compile.", font=sans(16, 500), fill=PLUM_DEEP)
    if subtitle:
        sw = text_w(d, subtitle, sans(16, 500))
        d.text((W - 40 - sw, 38), subtitle, font=sans(16, 500), fill=MUTED)


def save(im, name):
    p = SLIDES / name
    rgb = Image.new("RGB", im.size, (245, 242, 234))
    rgb.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
    rgb.save(p, "PNG", optimize=True)
    print("slide", p.name, rgb.size)
    return p


def slide_hook():
    c = new_canvas(W, H)
    header(c, "floor plans as code")
    plan = load(INT3 / "plans/courtyard-house.png")
    threed = load(INT4 / "replay/frames/courtyard_3d_last.png")
    paste_sheet(c, plan, (40, 84, 1040, 668), "archlang compile  →  courtyard-house.arch")
    paste_dim_inset(c, plan, (40, 764, 1040, 154))
    paste_3d(c, threed, (1100, 84, 780, 834), "archlang3d view --replay — light")
    caption_bar(c, "A language for floor plans", "Write .arch source. The compiler draws a precise sheet — and a 3D model of the same building.")
    save(c, "00_hook.png")


def slide_compile():
    c = new_canvas(W, H)
    header(c, "archlang compile")
    draw_code(c, (40, 84, 620, 850), STUDIO_LINES, size=16)
    plan = load(INT3 / "themes/studio-rendered.png")
    paste_sheet(c, plan, (680, 84, 1200, 850), "theme rendered  ·  PNG")
    caption_bar(c, "archlang compile plan.arch -o plan.png", "The same text always produces the same drawing, byte for byte.")
    save(c, "02_compile.png")


def _zoom_card(c, src, crop_box, box, title):
    x, y, w, h = box
    d = ImageDraw.Draw(c)
    d.rounded_rectangle([x + 3, y + 5, x + w + 3, y + h + 5], 12, fill=(214, 208, 196, 80))
    d.rounded_rectangle([x, y, x + w, y + h], 12, fill=CARD, outline=LINE)
    d.rectangle([x, y, x + 5, y + h], fill=PLUM)
    d.text((x + 16, y + 10), title, font=sans(14, 600), fill=PLUM_DEEP)
    z = src.convert("RGBA").crop(crop_box)
    inner = (x + 12, y + 34, w - 24, h - 46)
    ix, iy, iw, ih = inner
    zw, zh = z.size
    scale = min(iw / max(zw, 1), ih / max(zh, 1))
    nw, nh = max(1, int(zw * scale)), max(1, int(zh * scale))
    px = ix + (iw - nw) // 2
    py = iy + (ih - nh) // 2
    d.rounded_rectangle([px - 3, py - 3, px + nw + 3, py + nh + 3], 6, fill=WHITE)
    c.alpha_composite(z.resize((nw, nh), Image.Resampling.LANCZOS), (px, py))


def slide_themes():
    c = new_canvas(W, H)
    header(c, "theme rendered  ·  theme presentation")
    a = load(INT3 / "themes/studio-rendered.png")
    b = load(INT3 / "themes/studio-presentation.png")
    paste_sheet(c, a, (40, 84, 910, 400), "theme rendered  ·  full sheet")
    paste_sheet(c, b, (970, 84, 910, 400), "theme presentation  ·  full sheet")
    kit, sofa = (260, 268, 1020, 520), (300, 1140, 980, 1455)
    _zoom_card(c, a, kit, (40, 500, 445, 330), "zoom  ·  kitchen  ·  rendered")
    _zoom_card(c, a, sofa, (505, 500, 445, 330), "zoom  ·  sofa  ·  rendered")
    _zoom_card(c, b, kit, (970, 500, 445, 330), "zoom  ·  kitchen  ·  presentation")
    _zoom_card(c, b, sofa, (1435, 500, 445, 330), "zoom  ·  sofa  ·  presentation")
    caption_bar(c, "Themes restyle the sheet, never the geometry", "Rendered: cooler grey sink and taupe sofa. Presentation: warmer parchment fills. Walls and sizes stay identical.")
    save(c, "03_themes.png")


def slide_describe():
    c = new_canvas(W, H)
    d = ImageDraw.Draw(c)
    header(c, "archlang describe --json")
    plan = load(INT3 / "themes/studio-rendered.png")
    paste_sheet(c, plan, (40, 84, 1040, 850), "studio.arch  ·  compiled sheet")
    inner = card(c, (1100, 84, 780, 850), "describe()  ·  facts, not a guess")
    x, y, w, h = inner
    rows = [
        ("Plan", "Studio 1BR"),
        ("Rooms", "4"),
        ("Floor area", "42 m²"),
        ("Net area", "38.29 m²"),
        ("Doors", "3"),
        ("Windows", "3"),
        ("Reachable", "every room"),
        ("Warnings", "none"),
    ]
    yy = y + 24
    for k, v in rows:
        d.text((x + 20, yy), k, font=sans(22, 500), fill=MUTED)
        d.text((x + w - 20 - text_w(d, v, sans(22, 650)), yy), v, font=sans(22, 650), fill=INK)
        d.line([(x + 16, yy + 40), (x + w - 16, yy + 40)], fill=LINE, width=1)
        yy += 54
    caption_bar(c, "archlang describe plan.arch --json", "Areas, adjacency and reachability come back as data an agent can read without looking at the image.")
    save(c, "04_describe.png")


def slide_lint():
    c = new_canvas(W, H)
    d = ImageDraw.Draw(c)
    header(c, "archlang preview --review")
    before = load(INT3 / "lint/studio-nowindow-review.png")
    paste_sheet(c, before, (40, 84, 1180, 850), "review sheet  ·  1 warning ringed", crop="trim")
    inner = card(c, (1240, 84, 640, 850), "lint()")
    x, y, w, h = inner
    d.text((x + 20, y + 20), "BEFORE", font=sans(16, 650), fill=RED)
    d.text((x + 20, y + 58), "W_BEDROOM_NO_WINDOW", font=mono(22, 650), fill=AMBER)
    d.text((x + 20, y + 100), 'Bedroom "Bedroom"', font=sans(20, 500), fill=INK)
    d.text((x + 20, y + 132), "has no window.", font=sans(20, 500), fill=INK)
    d.text((x + 20, y + 200), "Fix the compiler suggests:", font=sans(16, 500), fill=MUTED)
    d.text((x + 20, y + 240), "window at (7000,1500)", font=mono(18, 500), fill=PLUM_DEEP)
    d.text((x + 20, y + 270), "width 1200 wall exterior", font=mono(18, 500), fill=PLUM_DEEP)
    caption_bar(c, "archlang lint  ·  preview --review", "Each warning has a code and, where there is one, a fix an agent can apply.")
    save(c, "05_lint.png")


def slide_fix():
    c = new_canvas(W, H)
    d = ImageDraw.Draw(c)
    header(c, "archlang suggest  ·  then compile again")
    after = load(INT3 / "plans/studio.png")
    paste_sheet(c, after, (40, 84, 1180, 850), "AFTER  ·  window restored  ·  lint clean")
    inner = card(c, (1240, 84, 640, 850), "fixed")
    x, y, w, h = inner
    d.text((x + 20, y + 20), "AFTER", font=sans(16, 650), fill=GREEN)
    d.text((x + 20, y + 58), "lint clean", font=sans(28, 650), fill=GREEN)
    d.text((x + 20, y + 120), "window at (7000,1500)", font=mono(18, 500), fill=INK)
    d.text((x + 20, y + 150), "width 1200", font=mono(18, 500), fill=INK)
    d.text((x + 20, y + 220), "The east wall of the", font=sans(20, 500), fill=INK)
    d.text((x + 20, y + 252), "bedroom now has a window.", font=sans(20, 500), fill=INK)
    d.text((x + 20, y + 320), "every room reachable", font=sans(20, 600), fill=GREEN)
    caption_bar(c, "Write the suggested window, compile again", "The review ring disappears. The drawing and the facts agree.")
    save(c, "06_fix.png")


def slide_param(n):
    c = new_canvas(W, H)
    header(c, "parametric.arch  ·  for i in 0..COUNT")
    code = [
        "let WALL = 200",
        "let W    = 4000",
        "let H    = 5000",
        f"let COUNT = {n}          # change this",
        "for i in 0..COUNT {",
        "  let x = i * W",
        "  wall exterior thickness WALL {",
        "    (x,0) (x+W,0) (x+W,H) (x,H) close",
        "  }",
        '  room at (x, 0) size W x H',
        '       label "{names[i]}"',
        "}",
    ]
    draw_code(c, (40, 84, 620, 850), code, size=18)
    plan = load(INT3 / f"plans/parametric-count{n}.png")
    paste_sheet(c, plan, (680, 84, 1200, 850), f"archlang compile  ·  COUNT = {n}")
    caption_bar(c, "Change one number, the row regenerates", f"let COUNT = {n}   ·   {n} studio units written by a loop, not copied by hand.")
    save(c, f"07_param_{n}.png")


def slide_export():
    c = new_canvas(W, H)
    d = ImageDraw.Draw(c)
    header(c, "one source, many exports")
    thumbs = Path("/workspace/archlang-spectacle/output/v4/intermediates/exports/thumbs")
    items = [
        ("SVG", "studio.svg", "vector sheet", thumbs / "studio-svg.png"),
        ("DXF", "studio.dxf", "CAD wireframe", thumbs / "studio-dxf.png"),
        ("PDF", "studio.pdf", "printable sheet", thumbs / "studio-pdf.png"),
        ("PNG", "studio.png", "raster preview", thumbs / "studio-png.png"),
        ("GLB", "studio.glb", "checked 3D build", thumbs / "studio-glb.png"),
    ]
    gap = 20
    n = len(items)
    card_w = (W - 80 - gap * (n - 1)) // n
    for i, (fmt, fname, note, thumb) in enumerate(items):
        x = 40 + i * (card_w + gap)
        y = 92
        d.rounded_rectangle([x + 3, y + 5, x + card_w + 3, y + 748], 16, fill=(214, 208, 196, 80))
        d.rounded_rectangle([x, y, x + card_w, y + 748], 16, fill=CARD, outline=LINE)
        d.text((x + 18, y + 16), fmt, font=sans(32, 650), fill=PLUM_DEEP)
        d.text((x + 18, y + 56), fname, font=mono(14, 500), fill=INK)
        d.text((x + 18, y + 78), note, font=sans(14, 500), fill=MUTED)
        im = trim_margins(load(thumb), pad=12)
        inner = (x + 14, y + 108, card_w - 28, 600)
        ix, iy, iw, ih = inner
        zw, zh = im.size
        scale = min(iw / max(zw, 1), ih / max(zh, 1))
        nw, nh = max(1, int(zw * scale)), max(1, int(zh * scale))
        px = ix + (iw - nw) // 2
        py = iy + (ih - nh) // 2
        d.rounded_rectangle([px - 4, py - 4, px + nw + 4, py + nh + 4], 8, fill=WHITE, outline=LINE)
        c.alpha_composite(im.resize((nw, nh), Image.Resampling.LANCZOS), (px, py))
    caption_bar(c, "archlang compile -f svg|dxf|pdf|png   ·   archlang3d build -o plan.glb", "Real files from the same studio.arch: SVG, DXF, PDF, PNG, and a checked GLB.")
    save(c, "09_export.png")


def slide_mcp():
    c = new_canvas(W, H)
    d = ImageDraw.Draw(c)
    header(c, "MCP  ·  CLI  ·  skill")
    cmds = [
        ("1", "npx -y @chanmeng666/archlang compile plan.arch --json"),
        ("2", "npx -y @chanmeng666/archlang describe plan.arch --json"),
        ("3", "npx -y @chanmeng666/archlang lint plan.arch --json"),
        ("4", "npx -y @chanmeng666/archlang fix plan.arch"),
        ("5", "npx archlang3d view plan.arch --replay -o plan.html"),
    ]
    box = card(c, (80, 110, 1760, 780), "The compiler is the agent interface")
    x, y, w, h = box
    yy = y + 20
    for num, cmd in cmds:
        d.rounded_rectangle([x + 16, yy, x + w - 16, yy + 88], 12, fill=CODE_BG, outline=LINE)
        d.text((x + 36, yy + 28), num, font=sans(22, 650), fill=PLUM_DEEP)
        d.text((x + 80, yy + 30), cmd, font=mono(22, 500), fill=INK)
        yy += 104
    caption_bar(c, "Every command takes --json", "An agent writes ArchLang, reads describe() and lint(), applies the fix, and recompiles.")
    save(c, "10_mcp.png")


def slide_end():
    c = new_canvas(W, H)
    d = ImageDraw.Draw(c)
    d.text((W // 2 - text_w(d, "ArchLang", sans(72, 650)) // 2, 340), "ArchLang", font=sans(72, 650), fill=INK)
    line = "Designs that compile."
    d.text((W // 2 - text_w(d, line, sans(36, 500)) // 2, 440), line, font=sans(36, 500), fill=PLUM_DEEP)
    url = "archlang.uk"
    d.text((W // 2 - text_w(d, url, sans(32, 600)) // 2, 540), url, font=sans(32, 600), fill=INK)
    sub = "playground.archlang.uk   ·   @chanmeng666/archlang   ·   archlang3d"
    d.text((W // 2 - text_w(d, sub, sans(18, 500)) // 2, 640), sub, font=sans(18, 500), fill=MUTED)
    save(c, "11_end.png")


def slide_end_vertical():
    c = new_canvas(1080, 1920)
    d = ImageDraw.Draw(c)
    d.text((1080 // 2 - text_w(d, "ArchLang", sans(64, 650)) // 2, 780), "ArchLang", font=sans(64, 650), fill=INK)
    line = "Designs that compile."
    d.text((1080 // 2 - text_w(d, line, sans(28, 500)) // 2, 880), line, font=sans(28, 500), fill=PLUM_DEEP)
    url = "archlang.uk"
    d.text((1080 // 2 - text_w(d, url, sans(28, 600)) // 2, 980), url, font=sans(28, 600), fill=INK)
    save(c, "11_end_9x16.png")


def typing_frames():
    out = SLIDES / "typing"
    out.mkdir(exist_ok=True)
    lines = STUDIO_LINES
    # flatten to a growing list of visible lines
    n = len(lines)
    # 1 frame per added line plus a few hold frames of the full file
    frames = []
    for i in range(1, n + 1):
        c = new_canvas(W, H)
        header(c, "write studio.arch")
        draw_code(c, (200, 84, 1520, 850), lines[:i], size=20)
        caption_bar(c, "Write the plan as text", "Rooms, walls, doors and windows in millimetres — a file you can diff.")
        save(c, f"typing/t{i:02d}.png")
    return n


def overlay_3d():
    """Top brand bar + bottom caption for the zoomed replay clip."""
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for y in range(0, 64):
        a = int(220 * (1 - y / 64))
        d.line([(0, y), (W, y)], fill=(245, 242, 234, a))
    d.text((40, 16), "ArchLang", font=sans(26, 650), fill=INK)
    bw = text_w(d, "ArchLang", sans(26, 650))
    d.text((40 + bw + 14, 24), "archlang3d view --replay — light", font=sans(16, 500), fill=PLUM_DEEP)
    d.rectangle([0, H - 92, W, H], fill=(236, 232, 222, 235))
    d.text((40, H - 78), "The plan draws itself, then the walls rise.", font=sans(24, 550), fill=INK)
    d.text((40, H - 42), "courtyard-house.arch   ·   11 rooms   ·   163 m²", font=sans(16, 500), fill=MUTED)
    mark = "archlang.uk"
    d.text((W - 40 - text_w(d, mark, sans(16, 600)), H - 42), mark, font=sans(16, 600), fill=PLUM_DEEP)
    im.save(SLIDES / "08_overlay.png")
    print("overlay written")


def main():
    slide_hook()
    typing_frames()
    slide_compile()
    slide_themes()
    slide_describe()
    slide_lint()
    slide_fix()
    for n in (2, 3, 4, 5):
        slide_param(n)
    slide_export()
    slide_mcp()
    slide_end()
    slide_end_vertical()
    overlay_3d()


if __name__ == "__main__":
    main()
