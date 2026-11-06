"""A-frame mark as architectural monument — letter / house / plan at once, in 3D spectacle."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    reset_scene, mat_principled, mat_emission, add_sun, add_area, add_camera,
    extrude_rect_wall, add_text, set_eevee_quality, render_still, PLUM, WHITE, SHEET, INK
)

OUT = str(Path(__file__).resolve().parents[2] / "output" / "images" / "03-aframe-monument-hero.png")
OUT_SQUARE = str(Path(__file__).resolve().parents[2] / "output" / "images" / "03-aframe-monument-1x1.png")

scene = reset_scene()
set_eevee_quality(scene, samples=28)

mat_wall = mat_principled("AWall", PLUM, metallic=0.2, roughness=0.18, emission=PLUM, emission_strength=1.2)
mat_sheet = mat_principled("Sheet", SHEET, metallic=0.0, roughness=0.65)
mat_ink = mat_principled("InkLine", INK, metallic=0.0, roughness=0.4)
mat_glow = mat_emission("DoorGlow", PLUM, strength=7.0)
mat_white = mat_emission("White", WHITE, strength=2.5)

# Floating sheet podium
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, -0.15))
podium = bpy.context.active_object
podium.scale = (14, 10, 0.3)
podium.data.materials.append(mat_sheet)

# Drafting grid lines on podium (thin cubes)
for i in range(-6, 7):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(i * 1.0, 0, 0.02))
    line = bpy.context.active_object
    line.scale = (0.02, 9, 0.01)
    line.data.materials.append(mat_ink)
for j in range(-4, 5):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, j * 1.0, 0.02))
    line = bpy.context.active_object
    line.scale = (12, 0.02, 0.01)
    line.data.materials.append(mat_ink)

# A-frame: two leaning gable walls + crossbar door
# Left stroke
bpy.ops.mesh.primitive_cube_add(size=1, location=(-2.2, 0, 3.5))
L = bpy.context.active_object
L.scale = (0.55, 3.2, 7.5)
L.rotation_euler = (0, 0, math.radians(18))
L.rotation_euler[1] = math.radians(22)
L.data.materials.append(mat_wall)

# Right stroke
bpy.ops.mesh.primitive_cube_add(size=1, location=(2.2, 0, 3.5))
R = bpy.context.active_object
R.scale = (0.55, 3.2, 7.5)
R.rotation_euler = (0, 0, math.radians(-18))
R.rotation_euler[1] = math.radians(-22)
R.data.materials.append(mat_wall)

# Crossbar = door opening with swing arc suggestion
bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 2.2))
bar = bpy.context.active_object
bar.scale = (3.6, 0.35, 0.45)
bar.data.materials.append(mat_glow)

# Door swing arc (torus sector approximation — thin torus)
bpy.ops.mesh.primitive_torus_add(major_radius=1.6, minor_radius=0.04, location=(0, 1.4, 1.0), abso_major_rad=1.6, abso_minor_rad=0.04)
arc = bpy.context.active_object
arc.rotation_euler = (math.radians(90), 0, 0)
arc.data.materials.append(mat_glow)

# Pendant light at apex
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.25, location=(0, 0, 7.2))
bulb = bpy.context.active_object
bulb.data.materials.append(mat_glow)
bpy.ops.mesh.primitive_cylinder_add(radius=0.03, depth=1.2, location=(0, 0, 6.5))
cord = bpy.context.active_object
cord.data.materials.append(mat_ink)

# Furniture glyphs in the two "leg rooms"
for x in (-1.8, 1.8):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x, -0.8, 0.35))
    f = bpy.context.active_object
    f.scale = (1.1, 0.7, 0.5)
    f.data.materials.append(mat_ink)

# Title — placed on the sheet in-camera
add_text("ArchLang", location=(0, -4.2, 0.25), size=0.75, material=mat_ink, extrude=0.05, align="CENTER")
add_text("letter · house · floor plan", location=(0, -5.0, 0.25), size=0.28, material=mat_wall, extrude=0.02, align="CENTER")
add_text("Designs that compile.", location=(0, -5.7, 0.25), size=0.26, material=mat_glow, extrude=0.02, align="CENTER")

add_sun(energy=2.8, rotation=(0.85, 0.25, 0.4))
add_area("Front", location=(0, -10, 6), size=14, energy=400, color=(0.7, 0.6, 1.0))
add_area("Top", location=(0, 0, 14), size=10, energy=250, color=(1, 1, 1))
add_camera(location=(7.5, -11.0, 5.8), target=(0, -1.5, 2.8), lens=32)

render_still(OUT, 1920, 1080)
render_still(OUT_SQUARE, 1080, 1080)
print("DONE 03")
