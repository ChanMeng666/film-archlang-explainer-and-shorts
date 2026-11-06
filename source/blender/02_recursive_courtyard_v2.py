"""v2 Impossible architecture: nested courtyard + REAL compiled SVG on sheet. Clean type."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, mat_principled, setup_three_point, add_camera, extrude_rect_wall,
    add_text, add_billboard_text, add_sheet_plane, add_image_plane, render_still,
    PLUM, WHITE, INK, VOID
)

OUT = ROOT / "output" / "images"
TEX = ROOT / "source" / "textures" / "courtyard-depth5.png"

scene = reset_scene()
set_eevee_quality(scene, samples=56)

mat_wall = mat_plum_wall("RingWall")
mat_inner = mat_principled("Inner", (0.12, 0.10, 0.22, 1.0), metallic=0.55, roughness=0.28,
                           emission=PLUM, emission_strength=0.15, clearcoat=0.25)
mat_core = mat_emission("Core", PLUM, strength=6.5)
mat_label = mat_emission("Label", WHITE, strength=2.8)
mat_sh = mat_sheet()
mat_ik = mat_ink()
mat_ground = mat_principled("VoidFloor", (0.035, 0.04, 0.05, 1.0), metallic=0.75, roughness=0.18)

bpy.ops.mesh.primitive_plane_add(size=55, location=(0, 0, -0.02))
bpy.context.active_object.data.materials.append(mat_ground)

# Drafting sheet island
add_sheet_plane(size=28, location=(0, 0, 0), material=mat_sh)
if TEX.exists():
    add_image_plane(TEX, location=(0, 0, 0.02), width=14.5, name="CourtyardSVG", emission=0.40)

BASE, DEPTH = 22.0, 5
for i in range(DEPTH):
    inset = i * 1.85
    span = BASE - 2 * inset
    h = 0.95 + i * 0.72
    thick = 0.20 - i * 0.018
    x0 = -BASE / 2 + inset
    y0 = -BASE / 2 + inset
    x1 = x0 + span
    y1 = y0 + span
    mat = mat_wall if i % 2 == 0 else mat_inner
    extrude_rect_wall(f"N{i}", x0, y1, x1, y1, h, thick, mat)
    extrude_rect_wall(f"S{i}", x0, y0, x1, y0, h, thick, mat)
    extrude_rect_wall(f"W{i}", x0, y0, x0, y1, h, thick, mat)
    extrude_rect_wall(f"E{i}", x1, y0, x1, y1, h, thick, mat)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.04 + i * 0.015))
    slab = bpy.context.active_object
    slab.scale = (max(span - 0.5, 0.5), max(span - 0.5, 0.5), 0.03)
    slab.data.materials.append(mat_core if i == DEPTH - 1 else mat_inner)

bpy.ops.mesh.primitive_cylinder_add(radius=1.05, depth=5.0, location=(0, 0, 2.5))
bpy.context.active_object.data.materials.append(mat_core)

# Titles + code on the sheet plane (never mirrored). Keep in-camera.
add_text("RECURSIVE COURTYARD", (0, -10.8, 0.05), size=0.70, material=mat_label, extrude=0.04, align="CENTER")
add_text("written as a loop  ·  compiled as a city", (0, -11.7, 0.05), size=0.30, material=mat_wall, extrude=0.015, align="CENTER")
add_text("ArchLang  ·  Designs that compile.", (0, -12.4, 0.05), size=0.22, material=mat_ik, extrude=0.01, align="CENTER")
add_text("DEPTH = 5", (8.5, 9.5, 0.05), size=0.55, material=mat_wall, extrude=0.03, align="CENTER")
add_text('for i in 1..DEPTH { let inset = i * 3500 }', (-7.5, 9.5, 0.05), size=0.28, material=mat_label, extrude=0.015, align="CENTER")

cam = add_camera(location=(14, -17, 12), target=(0, -1.5, 1.8), lens=28)
setup_three_point(target=(0, 0, 2))
render_still(OUT / "02-recursive-courtyard-hero-v2.png", 1920, 1080)

# 9:16 — closer, less empty sky
add_camera(location=(8, -12, 10), target=(0, -1, 2.2), lens=28)
render_still(OUT / "02-recursive-courtyard-9x16-v2.png", 1080, 1920)

# 1:1 tighter crop
add_camera(location=(11, -13, 10), target=(0, -1, 1.8), lens=30)
render_still(OUT / "02-recursive-courtyard-1x1-v2.png", 1080, 1080)
print("DONE 02 v2")
