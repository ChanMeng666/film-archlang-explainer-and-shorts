"""v2 Hero: .arch source → extruded plan, with REAL compiled laneway SVG projected."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, setup_three_point, add_camera, extrude_rect_wall, add_text,
    add_billboard_text, add_sheet_plane, add_image_plane, render_still, PLUM, WHITE
)

OUT = ROOT / "output" / "images"
TEX = ROOT / "source" / "textures" / "laneway-house.png"

scene = reset_scene()
set_eevee_quality(scene, samples=56)

mat_wall = mat_plum_wall("WallV2")
mat_sh = mat_sheet()
mat_ik = mat_ink()
mat_glow = mat_emission("Glow", PLUM, strength=4.5)
mat_code = mat_emission("Code", (0.9, 0.88, 1.0, 1.0), strength=3.2)

add_sheet_plane(size=20, location=(0, 0, 0), material=mat_sh)

# REAL compiled ArchLang sheet under the 3D extrusion
if TEX.exists():
    add_image_plane(TEX, location=(0, 0, 0.015), width=12.5, name="LanewaySVG", emission=0.45)

# 3D walls rising from the plan (laneway-ish metres)
walls = [
    (-3.5, -3.0, 3.5, -3.0, 1.55),
    (3.5, -3.0, 3.5, 3.0, 1.85),
    (3.5, 3.0, -3.5, 3.0, 1.55),
    (-3.5, 3.0, -3.5, -3.0, 1.85),
    (0.5, -3.0, 0.5, 3.0, 1.25),
    (0.5, -0.5, 3.5, -0.5, 1.15),
]
for i, (x0, y0, x1, y1, h) in enumerate(walls):
    extrude_rect_wall(f"W{i}", x0, y0, x1, y1, h, 0.16, mat_wall)

# Soft room glow slabs
for loc, sc in [((-1.5, 0, 0.12), (3.5, 5.5, 0.06)), ((2.0, -1.7, 0.12), (2.5, 2.1, 0.06)), ((2.0, 1.15, 0.12), (2.5, 1.9, 0.06))]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.scale = sc
    o.data.materials.append(mat_glow)

cam = add_camera(location=(-8.0, -9.0, 5.8), target=(0, -0.5, 1.0), lens=32)

# Clean code panel — billboard so it never flips
code = """plan \"Laneway House\" {
  units mm
  wall exterior thickness 200
  room Living size 4200x6500
  room Bedroom  uses bedroom
  door sliding width 1800
  # change one number —
  # one wall moves.
}"""
# Standing code panel (readable, not mirrored)
code_obj = add_text(code, (-5.2, -4.0, 0.12), size=0.20, material=mat_code, extrude=0.02, align="LEFT")
code_obj.rotation_euler = (1.15, 0, -0.4)

# Titles on the sheet (readable, no orbit clutter)
add_text("ArchLang", (0, -5.6, 0.04), size=0.68, material=mat_ik, extrude=0.045, align="CENTER")
add_text("Designs that compile.", (0, -6.3, 0.04), size=0.28, material=mat_wall, extrude=0.02, align="CENTER")
add_text("real compiled .arch → SVG under extrusion", (0, -6.85, 0.04), size=0.17, material=mat_ik, extrude=0.01, align="CENTER")

# Sparse token cubes between code and form
import random
random.seed(7)
for i in range(28):
    bpy.ops.mesh.primitive_cube_add(size=0.07, location=(-4.8 + random.random()*3.5, -0.8+random.random()*1.8, 1.2+random.random()*2.2))
    bpy.context.active_object.data.materials.append(mat_glow)

setup_three_point(target=(0, 0, 1.2))
render_still(OUT / "01-code-to-form-hero-v2.png", 1920, 1080)
# Tighter 1:1 — closer camera
add_camera(location=(-6.2, -6.8, 4.8), target=(0, 0, 1.0), lens=35)
render_still(OUT / "01-code-to-form-1x1-v2.png", 1080, 1080)
print("DONE 01 v2")
