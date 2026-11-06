"""Hero still: .arch source typography dissolving into / extruding a floor-plan structure."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    reset_scene, mat_principled, mat_emission, add_sun, add_area, add_camera,
    extrude_rect_wall, add_text, set_eevee_quality, render_still, PLUM, VOID, WHITE, SHEET, INK
)

OUT = str(Path(__file__).resolve().parents[2] / "output" / "images" / "01-code-to-form-hero.png")
OUT_SQUARE = str(Path(__file__).resolve().parents[2] / "output" / "images" / "01-code-to-form-1x1.png")

scene = reset_scene()
set_eevee_quality(scene, samples=24)

mat_wall = mat_principled("WallPlum", PLUM, metallic=0.25, roughness=0.28, emission=PLUM, emission_strength=0.35)
mat_glow = mat_emission("Glow", PLUM, strength=6.0)
mat_text = mat_emission("CodeGlow", (0.85, 0.8, 1.0, 1.0), strength=4.0)
mat_sheet = mat_principled("Sheet", SHEET, metallic=0.0, roughness=0.7)
mat_ink = mat_principled("Ink", INK, metallic=0.0, roughness=0.5)

# Ground plane — drafting sheet island floating in void
bpy.ops.mesh.primitive_plane_add(size=22, location=(0, 0, 0))
ground = bpy.context.active_object
ground.data.materials.append(mat_sheet)

# Floor-plan walls (laneway-ish layout in metres) rising from the sheet
walls = [
    (-3.5, -3.0, 3.5, -3.0),
    (3.5, -3.0, 3.5, 3.0),
    (3.5, 3.0, -3.5, 3.0),
    (-3.5, 3.0, -3.5, -3.0),
    (0.5, -3.0, 0.5, 3.0),   # partition
    (0.5, -0.5, 3.5, -0.5),
]
for i, (x0, y0, x1, y1) in enumerate(walls):
    h = 1.2 + (i % 3) * 0.55
    extrude_rect_wall(f"W{i}", x0, y0, x1, y1, height=h, thickness=0.18, material=mat_wall)

# Inner glowing volume blocks (rooms as light)
for name, loc, scale in [
    ("Live", (-1.5, 0, 0.15), (3.6, 5.6, 0.08)),
    ("Bed", (2.0, -1.7, 0.15), (2.6, 2.2, 0.08)),
    ("Bath", (2.0, 1.2, 0.15), (2.6, 2.0, 0.08)),
]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    o.data.materials.append(mat_glow)

# Floating source panel — the code that "authors" the form
code = """plan \"Laneway\" {
  units mm
  wall exterior { … }
  room Living size 4200x6500
  room Bedroom right-of Living
  door sliding width 1800
  # change one number —
  # one wall moves.
}"""
panel = add_text(code, location=(-7.2, -0.2, 2.8), size=0.22, material=mat_text, extrude=0.015)
panel.rotation_euler = (1.1, 0, -0.35)

# Brand wordmark line
title = add_text("ArchLang", location=(0, -5.2, 0.05), size=0.7, material=mat_ink, extrude=0.04, align="CENTER")
sub = add_text("Designs that compile.", location=(0, -6.0, 0.05), size=0.28, material=mat_wall, extrude=0.02, align="CENTER")

# Particles of "tokens" — small cubes drifting from code to walls
import random
random.seed(42)
for i in range(40):
    bpy.ops.mesh.primitive_cube_add(
        size=0.08,
        location=(-5.5 + random.random() * 4.5, -1 + random.random() * 2, 1.5 + random.random() * 2.5),
    )
    t = bpy.context.active_object
    t.data.materials.append(mat_glow)

add_sun(energy=2.5, rotation=(0.9, 0.15, 0.6))
add_area("Rim", location=(4, -6, 6), size=10, energy=350, color=(0.55, 0.45, 1.0))
add_area("Fill", location=(-6, 4, 5), size=8, energy=180, color=(1.0, 0.95, 0.9))
add_camera(location=(-9.5, -10.5, 6.5), target=(0, 0, 1.2), lens=32)

render_still(OUT, 1920, 1080)
render_still(OUT_SQUARE, 1080, 1080)
print("DONE 01")
