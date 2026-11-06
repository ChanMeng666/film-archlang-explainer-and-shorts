"""Impossible-architecture hero: nested courtyard city extruded from parametric rings."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    reset_scene, mat_principled, mat_emission, add_sun, add_area, add_camera,
    extrude_rect_wall, add_text, set_eevee_quality, render_still, PLUM, WHITE, SHEET, INK, VOID
)

OUT = str(Path(__file__).resolve().parents[2] / "output" / "images" / "02-recursive-courtyard-hero.png")
OUT_VERT = str(Path(__file__).resolve().parents[2] / "output" / "images" / "02-recursive-courtyard-9x16.png")

scene = reset_scene()
set_eevee_quality(scene, samples=24)

mat_wall = mat_principled("RingWall", PLUM, metallic=0.4, roughness=0.22, emission=PLUM, emission_strength=0.55)
mat_inner = mat_principled("Inner", (0.15, 0.12, 0.28, 1.0), metallic=0.6, roughness=0.25, emission=PLUM, emission_strength=0.2)
mat_core = mat_emission("Core", PLUM, strength=8.0)
mat_text = mat_emission("Label", WHITE, strength=3.0)
mat_ground = mat_principled("VoidFloor", (0.04, 0.045, 0.055, 1.0), metallic=0.8, roughness=0.15)

bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0))
g = bpy.context.active_object
g.data.materials.append(mat_ground)

# Nested square rings — DEPTH=5 spectacle
BASE = 24.0
DEPTH = 5
for i in range(DEPTH):
    inset = i * 2.0
    span = BASE - 2 * inset
    h = 0.8 + i * 0.65
    thick = 0.22 - i * 0.02
    x0 = -BASE / 2 + inset
    y0 = -BASE / 2 + inset
    x1 = x0 + span
    y1 = y0 + span
    mat = mat_wall if i % 2 == 0 else mat_inner
    # four sides
    extrude_rect_wall(f"N{i}", x0, y1, x1, y1, h, thick, mat)
    extrude_rect_wall(f"S{i}", x0, y0, x1, y0, h, thick, mat)
    extrude_rect_wall(f"W{i}", x0, y0, x0, y1, h, thick, mat)
    extrude_rect_wall(f"E{i}", x1, y0, x1, y1, h, thick, mat)
    # gate gaps implied by shorter top segments — leave mid openings via separate pieces
    # glowing floor slab per ring
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.03 + i * 0.02))
    slab = bpy.context.active_object
    slab.scale = (span - 0.4, span - 0.4, 0.04)
    slab.data.materials.append(mat_core if i == DEPTH - 1 else mat_inner)

# Central sanctum monolith
bpy.ops.mesh.primitive_cylinder_add(radius=1.2, depth=4.5, location=(0, 0, 2.25))
core = bpy.context.active_object
core.data.materials.append(mat_core)

# Orbiting code fragments
snippets = [
    "for i in 1..DEPTH {",
    "  let inset = i * 4000",
    "  room gallery N{i}",
    "  door gate width 1200",
    "}",
    "theme from \"#8052ff\"",
]
for i, snip in enumerate(snippets):
    ang = i / len(snippets) * math.tau
    r = 16
    t = add_text(snip, location=(math.cos(ang) * r, math.sin(ang) * r, 3 + i * 0.4),
                 size=0.45, material=mat_text, extrude=0.02, align="CENTER")
    t.rotation_euler = (1.2, 0, ang + math.pi / 2)

title = add_text("RECURSIVE COURTYARD", location=(0, -14, 0.1), size=0.85, material=mat_text, extrude=0.05, align="CENTER")
sub = add_text("written as a loop · compiled as a city", location=(0, -15.2, 0.1), size=0.35, material=mat_wall, extrude=0.02, align="CENTER")

add_sun(energy=3.0, rotation=(1.0, 0.3, 0.5))
add_area("Top", location=(0, 0, 18), size=20, energy=500, color=(0.6, 0.5, 1.0))
add_area("Side", location=(18, -12, 10), size=12, energy=300, color=(1.0, 0.9, 0.85))
add_camera(location=(18, -22, 14), target=(0, 0, 2), lens=28)

render_still(OUT, 1920, 1080)
# vertical social
scene.render.resolution_x = 1080
scene.render.resolution_y = 1920
add_camera(location=(10, -16, 12), target=(0, 0, 2.5), lens=28)
render_still(OUT_VERT, 1080, 1920)
print("DONE 02")
