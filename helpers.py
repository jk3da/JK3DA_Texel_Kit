def _get_selected_meshes(context):
    sel = [o for o in context.selected_objects if o.type == "MESH"]
    if not sel and context.active_object and context.active_object.type == "MESH":
        sel = [context.active_object]
    return sel
