import bmesh
import math

UNIT_MULT = {
    "CM": 1.0,
    "M":  100.0,
    "IN": 2.54,
    "FT": 30.48,
}

UNIT_LABEL = {
    "CM": "px/cm",
    "M":  "px/m",
    "IN": "px/in",
    "FT": "px/ft",
}

TD_PRESETS_CM = [
    ["20.48", "10.24", "5.12"],
    ["2.56",  "1.28",  "0.64"],
]


def _face_uv_area(face, uv_layer):
    uvs = [loop[uv_layer].uv for loop in face.loops]
    if len(uvs) < 3:
        return 0.0
    area = 0.0
    u0 = uvs[0]
    for i in range(1, len(uvs) - 1):
        area += abs((uvs[i] - u0).cross(uvs[i + 1] - u0)) * 0.5
    return area


def _face_world_area(face, matrix_world):
    verts = [matrix_world @ v.co for v in face.verts]
    if len(verts) < 3:
        return 0.0
    area = 0.0
    v0 = verts[0]
    for i in range(1, len(verts) - 1):
        area += (verts[i] - v0).cross(verts[i + 1] - v0).length * 0.5
    return area


def calc_density(obj, tex_size, selected_only=False):
    if obj.type != "MESH":
        return None

    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()

    uv_layer = bm.loops.layers.uv.active
    if not uv_layer:
        bm.free()
        return None

    total_uv = 0.0
    total_world = 0.0

    for face in bm.faces:
        if selected_only and not face.select:
            continue
        total_uv += _face_uv_area(face, uv_layer)
        total_world += _face_world_area(face, obj.matrix_world)

    bm.free()

    world_cm2 = total_world * 10_000.0
    if world_cm2 < 1e-9:
        return None

    td_cm = math.sqrt(tex_size ** 2 * total_uv / world_cm2)

    return {
        "td_cm": td_cm,
        "uv_pct": total_uv * 100.0,
        "world_cm2": world_cm2,
    }


def calc_density_multi(objects, tex_size, selected_only=False):
    total_world = 0.0
    weighted_td = 0.0
    weighted_uv = 0.0

    for obj in objects:
        r = calc_density(obj, tex_size, selected_only)
        if r is None:
            continue
        total_world += r["world_cm2"]
        weighted_td += r["td_cm"] * r["world_cm2"]
        weighted_uv += r["uv_pct"] * r["world_cm2"]

    if total_world < 1e-9:
        return None

    return {
        "td_cm": weighted_td / total_world,
        "uv_pct": weighted_uv / total_world,
        "world_cm2": total_world,
    }


def td_quality(td_cm):
    if td_cm < 5:
        return "Too Low", "COLORSET_01_VEC"
    if td_cm < 10:
        return "Low", "COLORSET_02_VEC"
    if td_cm < 20:
        return "Good", "COLORSET_03_VEC"
    if td_cm < 40:
        return "High", "COLORSET_04_VEC"
    return "Overkill", "COLORSET_06_VEC"
