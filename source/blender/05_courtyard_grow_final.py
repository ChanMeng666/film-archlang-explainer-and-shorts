"""FINAL 05: courtyard DEPTH grow at 24fps (~7s = 168 frames), glass + SVG swap."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet,
    mat_ink, mat_emission, mat_principled, setup_spectacle_lights, add_camera,
    extrude_rect_wall, add_text, add_standing_code, add_image_plane, PLUM, WHITE
)

FRAMES = ROOT / "output" / "videos" / "frames_courtyard_grow_final"
FRAMES.mkdir(parents=True, exist_ok=True)
TEX_DIR = ROOT / "source" / "textures"

scene = reset_scene()
set_eevee_quality(scene, samples=12)
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 168  # 7.0s
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(FRAMES / "frame_")

mat_wall = mat_plum_wall("GW")
mat_glass = mat_wall  # solid; SVG shown via hide_render sheet swap
mat_rim = mat_plum_wall("GR")
mat_core = mat_emission("GC", PLUM, strength=6.5)
mat_label = mat_emission("GL", WHITE, strength=3.0)
mat_sh = mat_sheet()
mat_ik = mat_ink()
mat_ground = mat_principled("Gnd", (0.03, 0.035, 0.045, 1.0), metallic=0.75, roughness=0.18)

bpy.ops.mesh.primitive_plane_add(size=48, location=(0, 0, -0.03))
bpy.context.active_object.data.materials.append(mat_ground)
bpy.ops.mesh.primitive_plane_add(size=24, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_sh)

# SVG depth sheets — show one at a time
for d in range(1, 6):
    tex = TEX_DIR / f"courtyard-depth{d}.png"
    if not tex.exists():
        continue
    pl = add_image_plane(tex, location=(0, 0, 0.02 + d * 0.0005), width=13.5,
                         name=f"SVG_D{d}", emission=1.0)
    show0 = 1 + (d - 1) * 28
    show1 = show0 + 28 if d < 5 else 169
    pl.hide_render = True
    pl.keyframe_insert(data_path="hide_render", frame=1)
    pl.hide_render = False
    pl.keyframe_insert(data_path="hide_render", frame=show0)
    pl.hide_render = True
    pl.keyframe_insert(data_path="hide_render", frame=show1)

BASE, DEPTH = 18.5, 5
for i in range(DEPTH):
    inset = i * 1.55
    span = BASE - 2 * inset
    h = 0.95 + i * 0.5
    thick = 0.15 - i * 0.012
    x0 = -BASE / 2 + inset
    y0 = -BASE / 2 + inset
    x1 = x0 + span
    y1 = y0 + span
    mat = mat_rim if i == 0 else mat_wall
    sides = []
    for name, coords in [
        (f"N{i}", (x0, y1, x1, y1)),
        (f"S{i}", (x0, y0, x1, y0)),
        (f"W{i}", (x0, y0, x0, y1)),
        (f"E{i}", (x1, y0, x1, y1)),
    ]:
        obj = extrude_rect_wall(name, *coords, h, thick, mat)
        if obj:
            sides.append(obj)
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.035 + i * 0.01))
    slab = bpy.context.active_object
    slab.scale = (max(span - 0.4, 0.35), max(span - 0.4, 0.35), 0.02)
    slab.data.materials.append(mat_core)
    sides.append(slab)
    birth = 8 + i * 28
    for obj in sides:
        obj.scale = (1, 1, 0.01)
        obj.keyframe_insert(data_path="scale", frame=1)
        obj.keyframe_insert(data_path="scale", frame=max(1, birth - 3))
        obj.scale = (1, 1, 1)
        obj.keyframe_insert(data_path="scale", frame=birth)
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"

bpy.ops.mesh.primitive_cylinder_add(radius=0.85, depth=3.8, location=(0, 0, 1.9))
core = bpy.context.active_object
core.data.materials.append(mat_core)
core.scale = (1, 1, 0.01)
core.keyframe_insert(data_path="scale", frame=1)
core.scale = (1, 1, 1)
core.keyframe_insert(data_path="scale", frame=145)

for d in range(1, 6):
    t = add_text(f"DEPTH = {d}", (0, -9.8, 0.07), size=0.7, material=mat_label, extrude=0.035, align="CENTER")
    show0 = 1 + (d - 1) * 28
    show1 = show0 + 28 if d < 5 else 169
    t.hide_render = True
    t.keyframe_insert(data_path="hide_render", frame=1)
    t.hide_render = False
    t.keyframe_insert(data_path="hide_render", frame=show0)
    t.hide_render = True
    t.keyframe_insert(data_path="hide_render", frame=show1)

add_text("RECURSIVE COURTYARD", (0, -10.9, 0.07), size=0.55, material=mat_label, extrude=0.025, align="CENTER")
add_text("ArchLang  ·  Designs that compile.", (0, -11.7, 0.07), size=0.26, material=mat_ik, extrude=0.012, align="CENTER")
add_standing_code("for i in 1..DEPTH { … }", (-8.5, -7.0, 0.2), size=0.28, material=mat_label, tilt_x=1.1, yaw_z=-0.3)

cam = add_camera(location=(13, -16, 11), target=(0, -1.5, 1.5), lens=28)
cam.location = (15.5, -19, 12.5)
cam.keyframe_insert(data_path="location", frame=1)
cam.location = (11, -13.5, 9.5)
cam.keyframe_insert(data_path="location", frame=168)
for fr in (1, 168):
    scene.frame_set(fr)
    direction = __import__("mathutils").Vector((0, -1.5, 1.5)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=fr)

setup_spectacle_lights(target=(0, 0, 1.6))
bpy.ops.render.render(animation=True)
print("FRAMES DONE courtyard grow final 24fps")
