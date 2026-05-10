import bpy

_MAT_NAME = "JK3DA_Texel_Kit_Checker"
_CHECKER_IMG_NAME = "JK3DA_Checker_Internal"


def _generate_checker_image(size=1024):
    import array

    img = bpy.data.images.get(_CHECKER_IMG_NAME)
    if img:
        bpy.data.images.remove(img)

    img = bpy.data.images.new(_CHECKER_IMG_NAME, width=size, height=size, alpha=False)
    img["jk3da_internal"] = True

    pixels = array.array("f", [0.0] * (size * size * 4))
    col_a = (0.900, 0.380, 0.0, 1.0)
    col_b = (0.0, 0.0, 0.0, 1.0)
    half = size // 2

    for y in range(size):
        for x in range(size):
            checker = ((x // half) + (y // half)) % 2
            col = col_a if checker == 0 else col_b
            idx = (y * size + x) * 4
            pixels[idx] = col[0]
            pixels[idx + 1] = col[1]
            pixels[idx + 2] = col[2]
            pixels[idx + 3] = col[3]

    img.pixels = list(pixels)
    img.pack()
    return img


def _build_checker_material(custom_image, scale):
    old_mat = bpy.data.materials.get(_MAT_NAME)
    if old_mat:
        bpy.data.materials.remove(old_mat)

    mat = bpy.data.materials.new(_MAT_NAME)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()

    tc = nt.nodes.new("ShaderNodeTexCoord")
    tc.location = (-500, 0)
    mapping = nt.nodes.new("ShaderNodeMapping")
    mapping.location = (-250, 0)
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.location = (50, 0)
    emit = nt.nodes.new("ShaderNodeEmission")
    emit.location = (380, 0)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (580, 0)

    mapping.inputs["Scale"].default_value = (scale, scale, scale)

    if custom_image:
        tex.image = custom_image
        tex.interpolation = "Linear"
    else:
        tex.image = _generate_checker_image(1024)
        tex.interpolation = "Closest"

    tex.extension = "REPEAT"
    nt.links.new(tc.outputs["UV"], mapping.inputs["Vector"])
    nt.links.new(mapping.outputs["Vector"], tex.inputs["Vector"])
    nt.links.new(tex.outputs["Color"], emit.inputs["Color"])
    nt.links.new(emit.outputs["Emission"], out.inputs["Surface"])

    return mat


def _update_checker_scale(scale):
    mat = bpy.data.materials.get(_MAT_NAME)
    if not mat:
        return
    for node in mat.node_tree.nodes:
        if node.type == "MAPPING":
            node.inputs["Scale"].default_value = (scale, scale, scale)
            break


def assign_checker(obj, scale, custom_image=None):
    obj["jk3da_stored_mats"] = [
        slot.material.name if slot.material else ""
        for slot in obj.material_slots
    ]
    mat = _build_checker_material(custom_image, scale)
    if not obj.material_slots:
        obj.data.materials.append(mat)
    else:
        for slot in obj.material_slots:
            slot.material = mat


def revert_materials(obj):
    stored = obj.get("jk3da_stored_mats")
    if not stored:
        return False
    for i, slot in enumerate(obj.material_slots):
        name = stored[i] if i < len(stored) else ""
        slot.material = bpy.data.materials.get(name) if name else None
    del obj["jk3da_stored_mats"]
    return True
