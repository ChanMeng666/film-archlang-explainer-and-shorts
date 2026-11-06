"""FINAL 02: nested courtyard — solid walls + oversized SVG apron (readable sheet)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, mat_principled, setup_spectacle_lights, add_camera,
    extrude_rect_wall, add_text, add_sheet_plane, add_image_plane,
    render_still, PLUM, WHITE
)

OUT = ROOT / "output" / "images" / "final"
OUT.mkdir(parents=True, exist_ok=True)
TEX = ROOT / "source" / "textures" / "courtyard-depth5.png"

scene = reset_scene()
set_eevee_quality(scene, samples=40)

mat_wall = mat_plum_wall("Ring")
mat_core = mat_emission("Core", PLUM, strength=7.0)
mat_label = mat_emission("Label", WHITE, strength=3.2)
mat_sh = mat_sheet()
mat_ik = mat_ink()
mat_ground = mat_principled("VoidFloor", (0.03, 0.035, 0.045, 1.0), metallic=0.8, roughness=0.16)
mat_inner = mat_principled("Inner", (0.14, 0.10, 0.28, 1.0), metallic=0.4, roughness=0.3,
                           emission=PLUM, emission_strength=0.25)

bpy.ops.mesh.primitive_plane_add(size=48, location=(0, 0, -0.03))
bpy.context.active_object.data.materials.append(mat_ground)
add_sheet_plane(size=28, location=(0, 0, 0), material=mat_sh)

# Oversized compiled SVG — extends as a readable apron BEYOND the massing
if TEX.exists():
    add_image_plane(TEX, location=(0, 0.5, 0.02), width=16.0, name="CourtyardSVG", emission=1.0)
    add_image_plane(TEX, location=(9.5, -2.5, 0.03), width=7.5, name="SideSVG", emission=1.25)

BASE, DEPTH = 14.0, 5  # tighter footprint so SVG apron shows around it
for i in range(DEPTH):
    inset = i * 1.15
    span = BASE - 2 * inset
    h = 0.75 + i * 0.55
    thick = 0.14
    x0 = -BASE / 2 + inset
    y0 = -BASE / 2 + inset
    x1 = x0 + span
    y1 = y0 + span
    mat = mat_wall if i % 2 == 0 else mat_inner
    # Open the camera-facing south wall on inner rings so sheet center reads
    sides = [("N", x0, y1, x1, y1), ("W", x0, y0, x0, y1), ("E", x1, y0, x1, y1)]
    if i == 0:
        sides.append(("S", x0, y0, x1, y0))
    else:
        # leave a gap in the south wall (two stubs)
        mid = (x0 + x1) / 2
        gap = span * 0.35
        sides.append(("S1", x0, y0, mid - gap / 2, y0))
        sides.append(("S2", mid + gap / 2, y0, x1, y0))
    for name, a, b, c, d in [(f"{n}{i}", *coords) for n, *coords in sides]:
        extrude_rect_wall(name, a, b, c, d, h, thick, mat)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.035 + i * 0.008))
    slab = bpy.context.active_object
    slab.scale = (max(span - 0.35, 0.3), max(span - 0.35, 0.3), 0.018)
    slab.data.materials.append(mat_core if i == DEPTH - 1 else mat_inner)

bpy.ops.mesh.primitive_cylinder_add(radius=0.75, depth=3.6, location=(0, 0, 1.8))
bpy.context.active_object.data.materials.append(mat_core)

add_text("RECURSIVE COURTYARD", (0, -8.4, 0.06), size=0.88, material=mat_label, extrude=0.05, align="CENTER")
add_text("written as a loop  ·  compiled as a city", (0, -9.3, 0.06), size=0.36, material=mat_wall, extrude=0.02, align="CENTER")
add_text("ArchLang  ·  Designs that compile.", (0, -10.05, 0.06), size=0.28, material=mat_ik, extrude=0.014, align="CENTER")
add_text("DEPTH = 5", (8.2, 9.0, 0.06), size=0.68, material=mat_wall, extrude=0.032, align="CENTER")
add_text("for i in 1..DEPTH { let inset = i * 3500 }", (-8.5, 8.8, 0.06), size=0.32, material=mat_label, extrude=0.015, align="CENTER")

setup_spectacle_lights(target=(0, 0, 1.5))
add_camera(location=(9.5, -12.0, 8.5), target=(0, -1.5, 1.2), lens=28)
render_still(OUT / "02-recursive-courtyard-hero-final.png", 1920, 1080)
add_camera(location=(7.5, -9.5, 7.2), target=(0, -1.0, 1.3), lens=30)
render_still(OUT / "02-recursive-courtyard-1x1-final.png", 1080, 1080)
add_camera(location=(4.5, -7.8, 6.8), target=(0, -0.5, 1.6), lens=26)
render_still(OUT / "02-recursive-courtyard-9x16-final.png", 1080, 1920)
print("DONE 02 FINAL")
