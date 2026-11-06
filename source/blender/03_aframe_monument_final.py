"""FINAL 03: A-frame monument + high-contrast hexagon SVG; wordmark fully in frame."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, setup_spectacle_lights, add_camera, add_text, add_sheet_plane,
    add_image_plane, render_still, PLUM
)

OUT = ROOT / "output" / "images" / "final"
OUT.mkdir(parents=True, exist_ok=True)
TEX = ROOT / "source" / "textures" / "hexagon-pavilion.png"

scene = reset_scene()
set_eevee_quality(scene, samples=40)

mat_wall = mat_plum_wall("AWall")
mat_sh = mat_sheet()
mat_ik = mat_ink()
mat_glow = mat_emission("DoorGlow", PLUM, strength=6.0)

add_sheet_plane(size=20, location=(0, 0, 0), material=mat_sh)
if TEX.exists():
    add_image_plane(TEX, location=(0, 1.2, 0.018), width=11.5, name="HexSVG", emission=1.0)

# Drafting grid (subtle, don't overpower SVG)
for i in range(-5, 6):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 1.15, 0, 0.012))
    line = bpy.context.active_object
    line.scale = (0.012, 9.0, 0.006)
    line.data.materials.append(mat_ik)
for j in range(-4, 5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, j * 1.1, 0.012))
    line = bpy.context.active_object
    line.scale = (11.5, 0.012, 0.006)
    line.data.materials.append(mat_ik)

bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.1, 0, 3.35))
L = bpy.context.active_object
L.scale = (0.5, 2.9, 7.0)
L.rotation_euler = (0, math.radians(22), math.radians(15))
L.data.materials.append(mat_wall)

bpy.ops.mesh.primitive_cube_add(size=1, location=(2.1, 0, 3.35))
R = bpy.context.active_object
R.scale = (0.5, 2.9, 7.0)
R.rotation_euler = (0, math.radians(-22), math.radians(-15))
R.data.materials.append(mat_wall)

bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.1))
bar = bpy.context.active_object
bar.scale = (3.3, 0.3, 0.4)
bar.data.materials.append(mat_glow)

bpy.ops.mesh.primitive_torus_add(major_radius=1.45, minor_radius=0.032, location=(0, 1.2, 0.92))
arc = bpy.context.active_object
arc.rotation_euler = (math.radians(90), 0, 0)
arc.data.materials.append(mat_glow)

bpy.ops.mesh.primitive_uv_sphere_add(radius=0.2, location=(0, 0, 6.8))
bpy.context.active_object.data.materials.append(mat_glow)
bpy.ops.mesh.primitive_cylinder_add(radius=0.022, depth=0.95, location=(0, 0, 6.2))
bpy.context.active_object.data.materials.append(mat_ik)

for x in (-1.65, 1.65):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.65, 0.3))
    f = bpy.context.active_object
    f.scale = (0.95, 0.6, 0.42)
    f.data.materials.append(mat_ik)

# Wordmark FULLY in frame — closer to monument, larger
add_text("ArchLang", (0, -4.2, 0.06), size=0.75, material=mat_ik, extrude=0.055, align="CENTER")
add_text("letter  ·  house  ·  floor plan", (0, -4.95, 0.06), size=0.30, material=mat_wall, extrude=0.02, align="CENTER")
add_text("Designs that compile.", (0, -5.6, 0.06), size=0.28, material=mat_glow, extrude=0.02, align="CENTER")

setup_spectacle_lights(target=(0, 0, 2.8))

# 16:9 — camera pulled back / aimed so wordmark stays in frame
add_camera(location=(8.5, -13.5, 6.5), target=(0, -1.5, 2.2), lens=28)
render_still(OUT / "03-aframe-monument-hero-final.png", 1920, 1080)
# 1:1
add_camera(location=(6.2, -10.0, 5.2), target=(0, -1.0, 2.3), lens=30)
render_still(OUT / "03-aframe-monument-1x1-final.png", 1080, 1080)
# 9:16 vertical
add_camera(location=(5.0, -11.0, 6.2), target=(0, -1.2, 2.5), lens=26)
render_still(OUT / "03-aframe-monument-9x16-final.png", 1080, 1920)
print("DONE 03 FINAL")
