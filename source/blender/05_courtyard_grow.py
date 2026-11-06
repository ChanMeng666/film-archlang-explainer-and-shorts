"""Motion: recursive courtyard DEPTH growing ring-by-ring (6.5s @ 12fps)."""
import sys, math
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, mat_principled, setup_three_point, add_camera, extrude_rect_wall,
    add_text, add_image_plane, PLUM, WHITE
)

OUT_DIR = ROOT / "output" / "videos"
FRAMES = OUT_DIR / "frames_courtyard_grow"
FRAMES.mkdir(parents=True, exist_ok=True)
TEX_DIR = ROOT / "source" / "textures"

scene = reset_scene()
set_eevee_quality(scene, samples=12)
scene.render.fps = 12
scene.frame_start = 1
scene.frame_end = 78  # 6.5s
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(FRAMES / "frame_")

mat_wall = mat_plum_wall("GW")
mat_inner = mat_principled("GI", (0.12, 0.10, 0.22, 1.0), metallic=0.5, roughness=0.3,
                           emission=PLUM, emission_strength=0.2)
mat_core = mat_emission("GC", PLUM, strength=6.0)
mat_sh = mat_sheet()
mat_label = mat_emission("GL", WHITE, strength=2.5)
mat_ik = mat_ink()
mat_ground = mat_principled("GG", (0.035, 0.04, 0.05, 1.0), metallic=0.7, roughness=0.2)

bpy.ops.mesh.primitive_plane_add(size=50, location=(0, 0, -0.02))
bpy.context.active_object.data.materials.append(mat_ground)
add_sheet = bpy.ops.mesh.primitive_plane_add(size=26, location=(0, 0, 0))
sheet = bpy.context.active_object
sheet.data.materials.append(mat_sh)

# Project depth-1 sheet initially; we'll keyframe visibility of overlays via scale
svg_planes = []
for d in range(1, 6):
    tex = TEX_DIR / f"courtyard-depth{d}.png"
    if not tex.exists():
        continue
    pl = add_image_plane(tex, location=(0, 0, 0.015 + d * 0.001), width=12.5,
                         name=f"SVG_D{d}", emission=0.15)
    # hide all but grow in
    pl.scale = (0.001, 0.001, 0.001)
    pl.keyframe_insert(data_path="scale", frame=1)
    birth = 4 + (d - 1) * 12
    pl.scale = (1, 1, 1)
    pl.keyframe_insert(data_path="scale", frame=birth)
    # when next appears, fade previous by scaling down slightly? keep stacked; hide earlier
    if d < 5:
        hide_at = birth + 12
        pl.keyframe_insert(data_path="scale", frame=hide_at - 1)
        pl.scale = (0.001, 0.001, 0.001)
        pl.keyframe_insert(data_path="scale", frame=hide_at)
    svg_planes.append(pl)

BASE, DEPTH = 20.0, 5
ring_objs = []
for i in range(DEPTH):
    inset = i * 1.7
    span = BASE - 2 * inset
    h = 0.85 + i * 0.65
    thick = 0.18 - i * 0.015
    x0 = -BASE / 2 + inset
    y0 = -BASE / 2 + inset
    x1 = x0 + span
    y1 = y0 + span
    mat = mat_wall if i % 2 == 0 else mat_inner
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
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.03 + i * 0.012))
    slab = bpy.context.active_object
    slab.scale = (max(span - 0.4, 0.4), max(span - 0.4, 0.4), 0.025)
    slab.data.materials.append(mat_core if i == DEPTH - 1 else mat_inner)
    sides.append(slab)
    # Birth keyframes: ring i appears around frame 6+i*12
    birth = 6 + i * 12
    for obj in sides:
        obj.scale = (1, 1, 0.01)
        obj.keyframe_insert(data_path="scale", frame=1)
        obj.keyframe_insert(data_path="scale", frame=max(1, birth - 2))
        obj.scale = (1, 1, 1)
        obj.keyframe_insert(data_path="scale", frame=birth)
        if obj.animation_data and obj.animation_data.action:
            for fc in obj.animation_data.action.fcurves:
                for kp in fc.keyframe_points:
                    kp.interpolation = "BEZIER"
    ring_objs.append(sides)

# Core monolith appears last
bpy.ops.mesh.primitive_cylinder_add(radius=0.95, depth=4.2, location=(0, 0, 2.1))
core = bpy.context.active_object
core.data.materials.append(mat_core)
core.scale = (1, 1, 0.01)
core.keyframe_insert(data_path="scale", frame=1)
core.scale = (1, 1, 1)
core.keyframe_insert(data_path="scale", frame=66)

# DEPTH counter text on sheet
depth_labels = []
for d in range(1, 6):
    t = add_text(f"DEPTH = {d}", (0, -11.5, 0.06), size=0.55, material=mat_label, extrude=0.03, align="CENTER")
    # show only during its window
    show0 = 4 + (d - 1) * 12
    show1 = show0 + 12 if d < 5 else 78
    t.hide_render = True
    t.keyframe_insert(data_path="hide_render", frame=1)
    t.hide_render = False
    t.keyframe_insert(data_path="hide_render", frame=show0)
    t.hide_render = True
    t.keyframe_insert(data_path="hide_render", frame=show1)
    depth_labels.append(t)

add_text("RECURSIVE COURTYARD", (0, -12.6, 0.06), size=0.45, material=mat_label, extrude=0.02, align="CENTER")
add_text("ArchLang  ·  Designs that compile.", (0, -13.4, 0.06), size=0.22, material=mat_ik, extrude=0.01, align="CENTER")

cam = add_camera(location=(15, -18, 12), target=(0, 0, 2), lens=28)
cam.location = (18, -22, 14)
cam.keyframe_insert(data_path="location", frame=1)
cam.location = (12, -15, 10)
cam.keyframe_insert(data_path="location", frame=78)
for fr in (1, 78):
    scene.frame_set(fr)
    direction = __import__("mathutils").Vector((0, 0, 2)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=fr)

setup_three_point(target=(0, 0, 2))
bpy.ops.render.render(animation=True)
print("FRAMES DONE courtyard grow")
