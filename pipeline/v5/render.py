#!/usr/bin/env python3
"""Render v5 explainer frames and encode."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "/workspace/archlang-spectacle/pipeline/v5")
sys.path.insert(0, "/workspace/archlang-spectacle/pipeline/v4")

from engine import FPS, W, H, chapter_starts, CHAPTERS_META, INT5, OUT
from scenes import render_explainer_frame

SEQ = INT5 / "seq"
PREV = INT5 / "preview"
SEQ.mkdir(parents=True, exist_ok=True)
PREV.mkdir(parents=True, exist_ok=True)


def total_duration():
    return sum(m[1] for m in CHAPTERS_META)


def save_frame(im, path: Path):
    rgb = Image.new("RGB", im.size, (245, 242, 234))
    rgb.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
    rgb.save(path, "PNG", optimize=False)


def preview(times):
    from PIL import Image
    global Image
    from PIL import Image as Im
    import scenes
    print("preview", times)
    for t in times:
        im = render_explainer_frame(t)
        dest = PREV / f"t{t:05.2f}.png".replace(".", "_")
        rgb = Im.new("RGB", im.size, (245, 242, 234))
        rgb.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        rgb.save(dest)
        print(" wrote", dest.name, im.size)


def render_all():
    from PIL import Image as Im
    total = total_duration()
    n = int(round(total * FPS))
    print(f"rendering {n} frames ({total:.2f}s @ {FPS}fps)")
    for i in range(n):
        t = i / FPS
        im = render_explainer_frame(t)
        rgb = Im.new("RGB", im.size, (245, 242, 234))
        rgb.paste(im, mask=im.split()[-1] if im.mode == "RGBA" else None)
        rgb.save(SEQ / f"{i:05d}.png")
        if i % 48 == 0:
            print(f"  {i}/{n}  t={t:.2f}s")
    print("done", n)


if __name__ == "__main__":
    from PIL import Image  # noqa: F401
    if "--preview" in sys.argv:
        preview([1.2, 4.0, 10.0, 18.2, 20.8, 26.0, 34.0, 40.2, 47.2, 55.0, 66.0, 73.2, 81.0, 87.0])
    else:
        render_all()
