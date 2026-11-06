"""FINAL 04: code-assemble motion at 24fps (~6s = 144 frames)."""
import sys, math, random
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from lib_spectacle import (
    ROOT, reset_scene, set_eevee_quality, mat_plum_wall, mat_sheet, mat_ink,
    mat_emission, setup_spectacle_lights, add_camera, extrude_rect_wall,
    add_text, add_standing_code, add_sheet_plane, add_image_plane, PLUM
)

FRAMES = ROOT / "output" / "videos" / "frames_assemble_final"
FRAMES.mkdir(parents=True, exist_ok=True)
TEX = ROOT / "source" / "textures" / "laneway-house.png"

scene = reset_scene()
set_eevee_quality(scene, samples=14)
scene.render.fps = 24
scene.frame_start = 1
scene.frame_end = 144  # 6.0s
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.image_settings.file_format = "PNG"
scene.render.filepath = str(FRAMES / "frame_")

mat_wall = mat_plum_wall("W")
mat_sh = mat_sheet()
mat_glow = mat_emission("G", PLUM, strength=5.0)
mat_text = mat_emission("T", (0.95, 0.93, 1.0, 1.0), strength=3.5)
mat_ik = mat_ink()

add_sheet_plane(size=18, location=(0, 0, 0), material=mat_sh)
if TEX.exists():
    add_image_plane(TEX, location=(0, 0.2, 0.015), width=9.5, name="SVG", emission=0.7)

segments = [
    (-3.0, -2.5, 3.0, -2.5, 1.45),
    (3.0, -2.5, 3.0, 2.5, 1.65),
    (3.0, 2.5, -3.0, 2.5, 1.45),
    (-3.0, 2.5, -3.0, -2.5, 1.65),
    (0.35, -2.5, 0.35, 2.5, 1.15),
    (0.35, -0.25, 3.0, -0.25, 1.05),
]
for i, (x0, y0, x1, y1, h) in enumerate(segments):
    obj = extrude_rect_wall(f"Seg{i}", x0, y0, x1, y1, h, 0.15, mat_wall)
    if not obj:
        continue
    birth = 10 + i * 16
    obj.scale = (1, 1, 0.01)
    obj.keyframe_insert(data_path="scale", frame=1)
    obj.scale = (1, 1, 1)
    obj.keyframe_insert(data_path="scale", frame=birth)
    if obj.animation_data and obj.animation_data.action:
        for fc in obj.animation_data.action.fcurves:
            for kp in fc.keyframe_points:
                kp.interpolation = "BEZIER"

random.seed(7)
for i in range(28):
    bpy.ops.mesh.primitive_cube_add(size=0.09, location=(-3.5 + random.random()*7, -2.5+random.random()*5, 4+random.random()*3))
    t = bpy.context.active_object
    t.data.materials.append(mat_glow)
    t.keyframe_insert(data_path="location", frame=1)
    t.location.z = 0.2
    t.keyframe_insert(data_path="location", frame=35 + i)
    t.scale = (1, 1, 1)
    t.keyframe_insert(data_path="scale", frame=50 + i)
    t.scale = (0.01, 0.01, 0.01)
    t.keyframe_insert(data_path="scale", frame=70 + i)

code = 'plan \"Studio\" {\n  units mm\n  wall exterior …\n}'
add_standing_code(code, (-5.2, -3.8, 0.2), size=0.28, material=mat_text, tilt_x=1.12, yaw_z=-0.4)
add_text("ArchLang", (0, -5.0, 0.05), size=0.55, material=mat_ik, extrude=0.03, align="CENTER")
add_text("code → compile → drawing", (0, -5.7, 0.05), size=0.24, material=mat_wall, extrude=0.015, align="CENTER")

cam = add_camera(location=(-8.5, -9.5, 5.5), target=(0, 0, 0.9), lens=32)
cam.location = (-10, -11, 6.5)
cam.keyframe_insert(data_path="location", frame=1)
cam.location = (-6.2, -7.5, 4.4)
cam.keyframe_insert(data_path="location", frame=144)
for fr in (1, 144):
    scene.frame_set(fr)
    direction = __import__("mathutils").Vector((0, 0, 0.9)) - cam.location
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    cam.keyframe_insert(data_path="rotation_euler", frame=fr)

setup_spectacle_lights(target=(0, 0, 1))
bpy.ops.render.render(animation=True)
print("FRAMES DONE assemble final 24fps")
