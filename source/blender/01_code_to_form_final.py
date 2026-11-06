"""FINAL 01: readable source code on dark card + real laneway SVG apron + form."""
import sys, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, mat_principled, setup_spectacle_lights, add_camera, extrude_rect_wall,
    add_text, add_sheet_plane, add_image_plane, render_still, PLUM, VOID, WHITE
)

OUT = ROOT / "output" / "images" / "final"
OUT.mkdir(parents=True, exist_ok=True)
TEX = ROOT / "source" / "textures" / "laneway-house.png"

scene = reset_scene()
set_eevee_quality(scene, samples=40)

mat_wall = mat_plum_wall("WallF")
mat_sh = mat_sheet()
mat_ik = mat_ink()
mat_glow = mat_emission("Glow", PLUM, strength=5.0)
mat_code = mat_emission("Code", WHITE, strength=5.5)
mat_card = mat_principled("CodeCard", VOID, metallic=0.2, roughness=0.45)

add_sheet_plane(size=24, location=(0, 0, 0), material=mat_sh)

# SVG apron clearly to the RIGHT of the massing (not buried under walls)
if TEX.exists():
    add_image_plane(TEX, location=(5.8, 0.8, 0.025), width=8.5, name="LanewaySVG", emission=1.2)

# 3D massing LEFT-CENTER
walls = [
    (-4.5, -2.6, 0.8, -2.6, 1.7),
    (0.8, -2.6, 0.8, 2.6, 2.0),
    (0.8, 2.6, -4.5, 2.6, 1.7),
    (-4.5, 2.6, -4.5, -2.6, 2.0),
    (-1.9, -2.6, -1.9, 2.6, 1.35),
    (-1.9, -0.35, 0.8, -0.35, 1.2),
]
for i, (x0, y0, x1, y1, h) in enumerate(walls):
    extrude_rect_wall(f"W{i}", x0, y0, x1, y1, h, 0.15, mat_wall)

for loc, sc in [((-3.15, 0, 0.1), (2.4, 4.8, 0.05)), ((-0.55, -1.45, 0.1), (2.2, 1.9, 0.05)), ((-0.55, 1.1, 0.1), (2.2, 1.7, 0.05))]:
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.scale = sc
    o.data.materials.append(mat_glow)

# Dark card + flat readable code ON THE SHEET (never mirrored)
bpy.ops.mesh.primitive_cube_add(size=1, location=(-7.2, -0.2, 0.08))
card = bpy.context.active_object
card.scale = (3.6, 5.2, 0.06)
card.data.materials.append(mat_card)

code = """plan \"Laneway House\" {
  units mm
  grid 50
  wall exterior thickness 200
  room Living size 4200x6500
  room Bedroom uses bedroom
  door sliding width 1800
  # change one number —
  # one wall moves.
}"""
add_text(code, (-7.2, -0.2, 0.16), size=0.26, material=mat_code, extrude=0.012, align="CENTER")

# Titles fully in frame
add_text("ArchLang", (-1.5, -4.6, 0.06), size=0.78, material=mat_ik, extrude=0.05, align="CENTER")
add_text("Designs that compile.", (-1.5, -5.4, 0.06), size=0.32, material=mat_wall, extrude=0.02, align="CENTER")
add_text(".arch source  →  compiled SVG  →  form", (-1.5, -6.05, 0.06), size=0.20, material=mat_ik, extrude=0.01, align="CENTER")

random.seed(11)
for _ in range(28):
    bpy.ops.mesh.primitive_cube_add(size=0.06, location=(-5.5+random.random()*2.5, -1+random.random()*2, 1.2+random.random()*2))
    bpy.context.active_object.data.materials.append(mat_glow)

setup_spectacle_lights(target=(-1.5, 0, 1.0))
add_camera(location=(-8.5, -9.5, 6.0), target=(-1.8, -0.8, 0.9), lens=30)
render_still(OUT / "01-code-to-form-hero-final.png", 1920, 1080)
add_camera(location=(-6.5, -7.0, 4.8), target=(-1.5, -0.5, 0.9), lens=32)
render_still(OUT / "01-code-to-form-1x1-final.png", 1080, 1080)
add_camera(location=(-6.0, -8.2, 6.5), target=(-2.0, -0.5, 1.2), lens=26)
render_still(OUT / "01-code-to-form-9x16-final.png", 1080, 1920)
print("DONE 01 FINAL")
