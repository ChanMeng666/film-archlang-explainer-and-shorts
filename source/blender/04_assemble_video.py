"""Short motion piece: floor-plan walls assembling from code tokens (6s @ 24fps)."""
import sys, math, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    reset_scene, mat_principled, mat_emission, add_sun, add_area, add_camera,
    extrude_rect_wall, add_text, set_eevee_quality, PLUM, WHITE, SHEET, INK
)

OUT_DIR = Path(__file__).resolve().parents[2] / "output" / "videos"
FRAMES_DIR = OUT_DIR / "frames_assemble"
FRAMES_DIR.mkdir(parents=True, exist_ok=True)
OUT_MP4 = str(OUT_DIR / "04-code-assemble.mp4")

scene = reset_scene()
set_eevee_quality(scene, samples=8)
scene.render.fps = 12
scene.frame_start = 1
scene.frame_end = 72  # 6 seconds @ 12fps
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(FRAMES_DIR / "frame_")

mat_wall = mat_principled("W", PLUM, metallic=0.3, roughness=0.25, emission=PLUM, emission_strength=0.45)
mat_sheet = mat_principled("S", SHEET, metallic=0.0, roughness=0.7)
mat_glow = mat_emission("G", PLUM, strength=5.0)
mat_text = mat_emission("T", WHITE, strength=3.0)
mat_ink = mat_principled("I", INK, metallic=0.0, roughness=0.5)

bpy.ops.mesh.primitive_plane_add(size=18, location=(0, 0, 0))
bpy.context.active_object.data.materials.append(mat_sheet)

# Wall segments with birth keyframes
segments = [
    (-3.2, -2.6, 3.2, -2.6, 1.4),
    (3.2, -2.6, 3.2, 2.6, 1.6),
    (3.2, 2.6, -3.2, 2.6, 1.4),
    (-3.2, 2.6, -3.2, -2.6, 1.6),
    (0.4, -2.6, 0.4, 2.6, 1.1),
    (0.4, -0.3, 3.2, -0.3, 1.0),
]
wall_objs = []
for i, (x0, y0, x1, y1, h) in enumerate(segments):
    obj = extrude_rect_wall(f"Seg{i}", x0, y0, x1, y1, h, 0.16, mat_wall)
    if obj is None:
        continue
    # Start buried / scaled to 0, rise in
    birth = 8 + i * 14
    obj.scale = (1, 1, 0.01)
    obj.keyframe_insert(data_path="scale", frame=1)
    obj.scale = (1, 1, 1)
    obj.keyframe_insert(data_path="scale", frame=birth)
    # ease
    for fc in obj.animation_data.action.fcurves:
        for kp in fc.keyframe_points:
            kp.interpolation = "BEZIER"
    wall_objs.append(obj)

# Token cubes raining in then vanishing
random.seed(7)
for i in range(30):
    bpy.ops.mesh.primitive_cube_add(size=0.1, location=(-4 + random.random()*8, -3+random.random()*6, 5+random.random()*3))
    t = bpy.context.active_object
    t.data.materials.append(mat_glow)
    z0 = t.location.z
    t.keyframe_insert(data_path="location", frame=1)
    t.location.z = 0.2
    t.keyframe_insert(data_path="location", frame=40 + i)
    t.scale = (1, 1, 1)
    t.keyframe_insert(data_path="scale", frame=50 + i)
    t.scale = (0.01, 0.01, 0.01)
    t.keyframe_insert(data_path="scale", frame=70 + i)

code = add_text('plan "Studio" { … }', location=(-5.5, -4.5, 3.5), size=0.35, material=mat_text, extrude=0.02)
code.rotation_euler = (1.15, 0, -0.4)
brand = add_text("ArchLang", location=(0, -5.5, 0.05), size=0.55, material=mat_ink, extrude=0.03, align="CENTER")
sub = add_text("code → compile → drawing", location=(0, -6.2, 0.05), size=0.25, material=mat_wall, extrude=0.015, align="CENTER")

# Camera fly
cam = add_camera(location=(-8, -9, 5.5), target=(0, 0, 0.8), lens=32)
cam.location = (-10, -11, 6.5)
cam.keyframe_insert(data_path="location", frame=1)
cam.location = (-6, -8, 4.5)
cam.keyframe_insert(data_path="location", frame=72)
# keep looking at origin roughly
for fr in (1, 72):
    scene.frame_set(fr)
    direction = __import__("mathutils").Vector((0, 0, 0.8)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=fr)

add_sun(energy=2.5, rotation=(0.9, 0.2, 0.5))
add_area("A", location=(5, -5, 6), size=8, energy=280, color=(0.55, 0.45, 1.0))

# Render animation frames
bpy.ops.render.render(animation=True)
print("FRAMES DONE")
