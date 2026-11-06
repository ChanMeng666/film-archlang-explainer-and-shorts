"""Shared helpers for ArchLang spectacle Blender scripts (Blender 4.2 EEVEE)."""
import math
from pathlib import Path
import bpy
import mathutils

PLUM = (0.502, 0.322, 1.0, 1.0)          # #8052ff
PLUM_DEEP = (0.420, 0.227, 0.878, 1.0)   # #6b3ae0
VOID = (0.059, 0.067, 0.082, 1.0)        # #0f1115
SHEET = (0.961, 0.949, 0.918, 1.0)       # #f5f2ea
INK = (0.067, 0.067, 0.067, 1.0)         # #111111
WHITE = (1.0, 1.0, 1.0, 1.0)
REDLINE = (0.761, 0.212, 0.169, 1.0)
ROOT = Path(__file__).resolve().parents[2]


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Filmic"
    scene.view_settings.look = "Medium High Contrast"
    # World void with subtle gradient feel via strength
    world = bpy.data.worlds.new("VoidWorld")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    bg = nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = VOID
    bg.inputs["Strength"].default_value = 0.85
    out = nodes.new("ShaderNodeOutputWorld")
    links.new(bg.outputs["Background"], out.inputs["Surface"])
    return scene


def set_eevee_quality(scene, samples=48):
    scene.render.engine = "BLENDER_EEVEE_NEXT"
    ee = getattr(scene, "eevee", None)
    if ee is not None:
        if hasattr(ee, "taa_render_samples"):
            ee.taa_render_samples = samples
        if hasattr(ee, "use_shadows"):
            ee.use_shadows = True
        if hasattr(ee, "use_raytracing"):
            ee.use_raytracing = False
        if hasattr(ee, "use_volumetric_shadows"):
            ee.use_volumetric_shadows = False
        if hasattr(ee, "shadow_ray_count"):
            ee.shadow_ray_count = 2
        if hasattr(ee, "shadow_step_count"):
            ee.shadow_step_count = 8


def mat_emission(name, color, strength=2.5):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    em = nt.nodes.new("ShaderNodeEmission")
    em.inputs["Color"].default_value = color
    em.inputs["Strength"].default_value = strength
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    nt.links.new(em.outputs["Emission"], out.inputs["Surface"])
    return m


def mat_principled(name, color, metallic=0.2, roughness=0.32, emission=None, emission_strength=0.0,
                   clearcoat=0.0, clearcoat_roughness=0.2):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = color
    if "Metallic" in bsdf.inputs:
        bsdf.inputs["Metallic"].default_value = metallic
    if "Roughness" in bsdf.inputs:
        bsdf.inputs["Roughness"].default_value = roughness
    # Blender 4.x: Coat
    if clearcoat and "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = clearcoat
        if "Coat Roughness" in bsdf.inputs:
            bsdf.inputs["Coat Roughness"].default_value = clearcoat_roughness
    elif clearcoat and "Clearcoat" in bsdf.inputs:
        bsdf.inputs["Clearcoat"].default_value = clearcoat
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = emission
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    elif emission is not None and "Emission" in bsdf.inputs:
        bsdf.inputs["Emission"].default_value = emission
        if "Emission Strength" in bsdf.inputs:
            bsdf.inputs["Emission Strength"].default_value = emission_strength
    return m


def mat_plum_wall(name="PlumWall"):
    """Slightly richer plum wall: metallic sheen + soft emissive edge, not flat plastic."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes.get("Principled BSDF")
    # Noise-driven roughness variation
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 18.0
    noise.inputs["Detail"].default_value = 8.0
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.22, 0.22, 0.22, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.48, 0.48, 0.48, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])
    bsdf.inputs["Base Color"].default_value = PLUM
    bsdf.inputs["Metallic"].default_value = 0.35
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.35
        bsdf.inputs["Coat Roughness"].default_value = 0.15
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = PLUM
        bsdf.inputs["Emission Strength"].default_value = 0.25
    return m


def mat_sheet(name="Sheet"):
    return mat_principled(name, SHEET, metallic=0.0, roughness=0.62)


def mat_ink(name="Ink"):
    return mat_principled(name, INK, metallic=0.05, roughness=0.45)


def mat_image(name, image_path, emission=0.0):
    """Image texture material for projecting compiled ArchLang PNG sheets."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes.get("Principled BSDF")
    img = bpy.data.images.load(str(image_path))
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = img
    tex.interpolation = "Closest"
    links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if emission > 0 and "Emission Color" in bsdf.inputs:
        links.new(tex.outputs["Color"], bsdf.inputs["Emission Color"])
        bsdf.inputs["Emission Strength"].default_value = emission
    bsdf.inputs["Roughness"].default_value = 0.55
    bsdf.inputs["Metallic"].default_value = 0.0
    # Alpha if present
    if "Alpha" in bsdf.inputs:
        links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        m.blend_method = "BLEND"
    return m


def add_sun(energy=3.2, rotation=(0.95, 0.25, 0.55), color=(1.0, 0.96, 0.98)):
    light_data = bpy.data.lights.new(name="KeySun", type="SUN")
    light_data.energy = energy
    light_data.color = color
    if hasattr(light_data, "angle"):
        light_data.angle = math.radians(5)
    obj = bpy.data.objects.new(name="KeySun", object_data=light_data)
    bpy.context.collection.objects.link(obj)
    obj.rotation_euler = rotation
    return obj


def add_area(name, location, size=8.0, energy=180.0, color=(0.55, 0.45, 1.0),
             rotation=(0, 0, 0)):
    light_data = bpy.data.lights.new(name=name, type="AREA")
    light_data.energy = energy
    light_data.size = size
    light_data.color = color
    if hasattr(light_data, "spread"):
        light_data.spread = math.radians(120)
    obj = bpy.data.objects.new(name=name, object_data=light_data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    return obj


def setup_three_point(target=(0, 0, 1.5)):
    """Key (warm sun) + plum rim + soft fill — less flat EEVEE look."""
    add_sun(energy=2.8, rotation=(1.05, 0.15, 0.7))
    add_area("RimPlum", location=(6, -4, 7), size=10, energy=420,
             color=(0.55, 0.38, 1.0), rotation=(math.radians(50), 0, math.radians(40)))
    add_area("FillWarm", location=(-7, 5, 4), size=12, energy=160,
             color=(1.0, 0.94, 0.88), rotation=(math.radians(60), 0, math.radians(-35)))
    add_area("KickTop", location=(0, 0, 14), size=16, energy=90,
             color=(0.75, 0.7, 1.0), rotation=(0, 0, 0))


def add_camera(location, target=(0, 0, 1), lens=35):
    cam_data = bpy.data.cameras.new("Cam")
    cam_data.lens = lens
    cam = bpy.data.objects.new("Cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = location
    direction = mathutils.Vector(target) - mathutils.Vector(location)
    cam.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    bpy.context.scene.camera = cam
    return cam


def extrude_rect_wall(name, x0, y0, x1, y1, height, thickness, material):
    cx = (x0 + x1) / 2
    cy = (y0 + y1) / 2
    dx = x1 - x0
    dy = y1 - y0
    length = math.hypot(dx, dy)
    if length < 1e-6:
        return None
    bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, height / 2))
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (length, thickness, height)
    angle = math.atan2(dy, dx)
    obj.rotation_euler = (0, 0, angle)
    if material:
        obj.data.materials.clear()
        obj.data.materials.append(material)
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return obj


def add_text(body, location, size=0.35, material=None, extrude=0.02, align="LEFT",
             rotation=(0, 0, 0)):
    """Flat sheet-plane text (readable from above/front). Avoid upside-down orbits."""
    curve = bpy.data.curves.new(type="FONT", name="TextCurve")
    curve.body = body
    curve.size = size
    curve.extrude = extrude
    if align == "CENTER":
        curve.align_x = "CENTER"
        curve.align_y = "CENTER"
    obj = bpy.data.objects.new("Text", curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = rotation
    if material:
        obj.data.materials.append(material)
    return obj


def add_billboard_text(body, location, cam, size=0.3, material=None, extrude=0.015, align="LEFT"):
    """Camera-facing text so labels never render upside-down or mirrored."""
    obj = add_text(body, location, size=size, material=material, extrude=extrude, align=align)
    # Match camera orientation then flip 180 around local Y so glyphs face the lens
    obj.rotation_euler = cam.rotation_euler.copy()
    obj.rotation_euler.rotate_axis('Y', math.pi)
    return obj


def add_sheet_plane(size=18, location=(0, 0, 0), material=None):
    bpy.ops.mesh.primitive_plane_add(size=size, location=location)
    obj = bpy.context.active_object
    obj.name = "Sheet"
    if material:
        obj.data.materials.append(material)
    return obj


def add_image_plane(image_path, location=(0, 0, 0.02), width=10.0, name="PlanSheet", emission=0.55):
    """Project a compiled ArchLang PNG onto a plane on the drafting sheet."""
    img = bpy.data.images.load(str(image_path))
    aspect = img.size[1] / max(img.size[0], 1)
    height = width * aspect
    bpy.ops.mesh.primitive_plane_add(size=1, location=location)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = (width / 2, height / 2, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    mat = mat_image(f"Mat_{name}", image_path, emission=emission)
    obj.data.materials.append(mat)
    return obj



def mat_plum_glass(name="PlumGlass", alpha=0.48):
    """Semi-transparent plum so compiled SVG sheet reads through courtyard walls."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    # EEVEE transparency
    if hasattr(m, "blend_method"):
        m.blend_method = "BLEND"
    if hasattr(m, "shadow_method"):
        m.shadow_method = "HASHED"
    if hasattr(m, "use_backface_culling"):
        m.use_backface_culling = False
    if hasattr(m, "surface_render_method"):
        # Blender 4.2 EEVEE Next
        try:
            m.surface_render_method = "BLENDED"
        except Exception:
            pass
    nt = m.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = PLUM
    bsdf.inputs["Metallic"].default_value = 0.15
    bsdf.inputs["Roughness"].default_value = 0.22
    if "Alpha" in bsdf.inputs:
        bsdf.inputs["Alpha"].default_value = alpha
    # No refraction/transmission — alpha blend only (CPU-friendly EEVEE)
    if "Transmission Weight" in bsdf.inputs:
        bsdf.inputs["Transmission Weight"].default_value = 0.0
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = 0.0
    if "Coat Weight" in bsdf.inputs:
        bsdf.inputs["Coat Weight"].default_value = 0.4
        bsdf.inputs["Coat Roughness"].default_value = 0.12
    if "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = PLUM
        bsdf.inputs["Emission Strength"].default_value = 0.35
    return m


def add_standing_code(body, location, size=0.22, material=None, extrude=0.025,
                      tilt_x=1.15, yaw_z=-0.45):
    """Upright readable source panel (sheet-facing camera approx). Never mirrored."""
    obj = add_text(body, location, size=size, material=material, extrude=extrude, align="LEFT")
    obj.rotation_euler = (tilt_x, 0.0, yaw_z)
    return obj


def setup_spectacle_lights(target=(0, 0, 1.5)):
    """Punchier three-point + plum rim for final package."""
    add_sun(energy=3.4, rotation=(1.1, 0.12, 0.75), color=(1.0, 0.97, 0.99))
    add_area("RimPlum", location=(7, -5, 8), size=11, energy=520,
             color=(0.58, 0.40, 1.0), rotation=(math.radians(48), 0, math.radians(45)))
    add_area("FillWarm", location=(-8, 6, 5), size=14, energy=200,
             color=(1.0, 0.93, 0.86), rotation=(math.radians(55), 0, math.radians(-40)))
    add_area("KickTop", location=(0, 2, 16), size=18, energy=120,
             color=(0.7, 0.65, 1.0), rotation=(0, 0, 0))
    add_area("GroundBounce", location=(0, -2, 0.4), size=10, energy=80,
             color=(0.95, 0.92, 0.88), rotation=(math.radians(-90), 0, 0))

def render_still(path, res_x=1920, res_y=1080):
    scene = bpy.context.scene
    scene.render.resolution_x = res_x
    scene.render.resolution_y = res_y
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)
    print(f"WROTE {path}")
