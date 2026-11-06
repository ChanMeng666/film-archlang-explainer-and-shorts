"""v2 A-frame monument with stronger lighting + hexagon SVG sheet accent."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, setup_three_point, add_camera, add_text, add_sheet_plane,
    add_image_plane, render_still, PLUM, WHITE
)

OUT = ROOT / "output" / "images"
TEX = ROOT / "source" / "textures" / "hexagon-pavilion.png"

scene = reset_scene()
set_eevee_quality(scene, samples=64)

mat_wall = mat_plum_wall("AWall")
mat_sh = mat_sheet()
mat_ik = mat_ink()
mat_glow = mat_emission("DoorGlow", PLUM, strength=5.5)

add_sheet_plane(size=18, location=(0, 0, 0), material=mat_sh)
# Real compiled hexagon pavilion as drafting context behind/under monument
if TEX.exists():
    add_image_plane(TEX, location=(0, 1.8, 0.012), width=9.5, name="HexSVG", emission=0.12)

# Drafting grid
for i in range(-6, 7):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 1.0, 0, 0.018))
    line = bpy.context.active_object
    line.scale = (0.015, 8.5, 0.008)
    line.data.materials.append(mat_ik)
for j in range(-4, 5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, j * 1.0, 0.018))
    line = bpy.context.active_object
    line.scale = (11, 0.015, 0.008)
    line.data.materials.append(mat_ik)

# A-frame
bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.15, 0, 3.4))
L = bpy.context.active_object
L.scale = (0.52, 3.0, 7.2)
L.rotation_euler = (0, math.radians(22), math.radians(16))
L.data.materials.append(mat_wall)

bpy.ops.mesh.primitive_cube_add(size=1, location=(2.15, 0, 3.4))
R = bpy.context.active_object
R.scale = (0.52, 3.0, 7.2)
R.rotation_euler = (0, math.radians(-22), math.radians(-16))
R.data.materials.append(mat_wall)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.15))
bar = bpy.context.active_object
bar.scale = (3.4, 0.32, 0.42)
bar.data.materials.append(mat_glow)

bpy.ops.mesh.primitive_torus_add(major_radius=1.5, minor_radius=0.035, location=(0, 1.25, 0.95))
arc = bpy.context.active_object
arc.rotation_euler = (math.radians(90), 0, 0)
arc.data.materials.append(mat_glow)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.22, location=(0, 0, 6.95))
bpy.context.active_object.data.materials.append(mat_glow)
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=1.0, location=(0, 0, 6.35))
bpy.context.active_object.data.materials.append(mat_ik)

for x in (-1.7, 1.7):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.7, 0.32))
    f = bpy.context.active_object
    f.scale = (1.0, 0.65, 0.45)
    f.data.materials.append(mat_ik)

# Readable titles on sheet
add_text("ArchLang", (0, -5.0, 0.05), size=0.78, material=mat_ik, extrude=0.05, align="CENTER")
add_text("letter  ·  house  ·  floor plan", (0, -5.85, 0.05), size=0.28, material=mat_wall, extrude=0.018, align="CENTER")
add_text("Designs that compile.", (0, -6.55, 0.05), size=0.26, material=mat_glow, extrude=0.018, align="CENTER")

setup_three_point(target=(0, 0, 3))
add_camera(location=(7.2, -10.5, 5.6), target=(0, -1.2, 2.6), lens=32)
render_still(OUT / "03-aframe-monument-hero-v2.png", 1920, 1080)
add_camera(location=(5.5, -8.0, 4.8), target=(0, -0.5, 2.8), lens=34)
render_still(OUT / "03-aframe-monument-1x1-v2.png", 1080, 1080)
print("DONE 03 v2")
