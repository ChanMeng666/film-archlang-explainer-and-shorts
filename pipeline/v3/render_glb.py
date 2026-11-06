"""Import an ArchLang-3d GLB and render it. Camera + lights only — no extra building mesh."""
import sys
from pathlib import Path
import math
import bpy
from mathutils import Vector

ARGS = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
# usage: blender --background --python render_glb.py -- in.glb out.png [WxH] [transparent]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in list(bpy.data.meshes) + list(bpy.data.materials) + list(bpy.data.cameras) + list(bpy.data.lights):
        if block.users == 0:
            if isinstance(block, bpy.types.Mesh):
                bpy.data.meshes.remove(block)
            elif isinstance(block, bpy.types.Material):
                bpy.data.materials.remove(block)
            elif isinstance(block, bpy.types.Camera):
                bpy.data.cameras.remove(block)
            elif isinstance(block, bpy.types.Light):
                bpy.data.lights.remove(block)


def imported_objects():
    return [o for o in bpy.context.scene.objects if o.type in {"MESH", "EMPTY"}]


def scene_bounds(objs):
    mats = [o.matrix_world for o in objs if o.type == "MESH"]
    if not any(o.type == "MESH" for o in objs):
        return Vector((0, 0, 0)), Vector((1, 1, 1))
    mins = Vector((1e9, 1e9, 1e9))
    maxs = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != "MESH":
            continue
        for corner in o.bound_box:
            w = o.matrix_world @ Vector(corner)
            mins.x, mins.y, mins.z = min(mins.x, w.x), min(mins.y, w.y), min(mins.z, w.z)
            maxs.x, maxs.y, maxs.z = max(maxs.x, w.x), max(maxs.y, w.y), max(maxs.z, w.z)
    return mins, maxs


def setup_world(transparent):
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new("ShaderNodeBackground")
    out = nt.nodes.new("ShaderNodeOutputWorld")
    if transparent:
        bg.inputs["Color"].default_value = (0.02, 0.022, 0.028, 1)
        bg.inputs["Strength"].default_value = 0.15
    else:
        # Void #0f1115
        bg.inputs["Color"].default_value = (0.035, 0.039, 0.048, 1)
        bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])


def add_lights(center, size):
    # Neutral architectural lighting — no purple wash on the mesh.
    def light(name, type_, energy, loc, rot, color=(1, 0.98, 0.94)):
        data = bpy.data.lights.new(name, type_)
        data.energy = energy
        data.color = color
        if type_ == "AREA":
            data.size = max(size * 0.8, 2.0)
        obj = bpy.data.objects.new(name, data)
        obj.location = loc
        obj.rotation_euler = rot
        bpy.context.scene.collection.objects.link(obj)
        return obj

    s = size
    c = center
    light("Key", "AREA", 450, (c.x + s * 0.9, c.y - s * 1.1, c.z + s * 1.4),
          (math.radians(50), 0, math.radians(35)), (1.0, 0.97, 0.92))
    light("Fill", "AREA", 160, (c.x - s * 1.2, c.y - s * 0.4, c.z + s * 0.8),
          (math.radians(65), 0, math.radians(-50)), (0.82, 0.88, 1.0))
    light("Rim", "AREA", 90, (c.x - s * 0.2, c.y + s * 1.3, c.z + s * 1.1),
          (math.radians(40), 0, math.radians(180)), (0.70, 0.62, 1.0))  # faint plum rim only
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 2.2
    sun.color = (1.0, 0.98, 0.94)
    sun_obj = bpy.data.objects.new("Sun", sun)
    sun_obj.location = (c.x + s, c.y - s, c.z + s * 2)
    sun_obj.rotation_euler = (math.radians(45), math.radians(10), math.radians(30))
    bpy.context.scene.collection.objects.link(sun_obj)


def add_shadow_plane(mins, maxs):
    # Staging only: a shadow catcher under the imported model. Not building geometry.
    dx = maxs.x - mins.x
    dy = maxs.y - mins.y
    size = max(dx, dy) * 4
    bpy.ops.mesh.primitive_plane_add(size=size, location=((mins.x + maxs.x) / 2, (mins.y + maxs.y) / 2, mins.z - 0.001))
    plane = bpy.context.active_object
    plane.name = "ShadowCatcher"
    plane.is_shadow_catcher = True
    mat = bpy.data.materials.new("ShadowCatcherMat")
    mat.use_nodes = True
    plane.data.materials.append(mat)
    return plane


def frame_camera(mins, maxs, aspect):
    center = (mins + maxs) * 0.5
    size = max(maxs.x - mins.x, maxs.y - mins.y, maxs.z - mins.z, 0.5)
    # South-west and above — same corner ArchLang's iso/axon look from.
    dist = size * 2.35
    loc = Vector((center.x + dist * 0.82, center.y - dist * 0.95, center.z + dist * 0.72))
    cam_data = bpy.data.cameras.new("Camera")
    cam_data.lens = 50
    cam_data.clip_start = 0.01
    cam_data.clip_end = max(size * 40, 100)
    cam = bpy.data.objects.new("Camera", cam_data)
    cam.location = loc
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    direction = center - loc
    rot_quat = direction.to_track_quat("-Z", "Y")
    cam.rotation_euler = rot_quat.to_euler()
    return cam


def configure_render(width, height, transparent, out):
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = width
    scene.render.resolution_y = height
    scene.render.resolution_percentage = 100
    scene.render.filepath = str(out)
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA" if transparent else "RGB"
    scene.render.film_transparent = transparent
    scene.render.use_file_extension = True
    eevee = scene.eevee
    if hasattr(eevee, "taa_render_samples"):
        eevee.taa_render_samples = 64
    if hasattr(eevee, "use_shadows"):
        eevee.use_shadows = True
    view = scene.view_settings
    view.view_transform = "AgX"
    view.look = "None"
    view.exposure = 0.0


def main():
    glb = Path(ARGS[0])
    out = Path(ARGS[1])
    size = ARGS[2] if len(ARGS) > 2 else "1920x1080"
    transparent = (ARGS[3] if len(ARGS) > 3 else "transparent") == "transparent"
    w, h = (int(x) for x in size.lower().split("x"))
    out.parent.mkdir(parents=True, exist_ok=True)

    clear_scene()
    bpy.ops.import_scene.gltf(filepath=str(glb))
    objs = imported_objects()
    meshes = [o for o in objs if o.type == "MESH"]
    print(f"imported {len(meshes)} meshes from {glb.name}")
    for o in meshes[:12]:
        print(f"  mesh {o.name} verts={len(o.data.vertices)}")
    mins, maxs = scene_bounds(objs)
    print(f"bounds {tuple(mins)} .. {tuple(maxs)}")
    center = (mins + maxs) * 0.5
    size_m = max(maxs.x - mins.x, maxs.y - mins.y, maxs.z - mins.z, 0.5)
    setup_world(transparent)
    add_shadow_plane(mins, maxs)
    add_lights(center, size_m)
    frame_camera(mins, maxs, w / h)
    configure_render(w, h, transparent, out)
    bpy.ops.render.render(write_still=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
