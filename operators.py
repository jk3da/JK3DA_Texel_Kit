import bpy
from .core import calc_density_multi, UNIT_MULT
from .checker import assign_checker, revert_materials
from .helpers import _get_selected_meshes
from .report_data import _scene_report as scene_report_data


class JK3DA_OT_ScanDensity(bpy.types.Operator):
    bl_idname = "jk3da.scan_density"
    bl_label = "Scan Density"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        p = context.scene.jk3da_texelkit
        sel = _get_selected_meshes(context)

        if not sel:
            self.report({"WARNING"}, "Select at least one mesh object")
            return {"CANCELLED"}

        selected_only = (context.mode == "EDIT_MESH" and p.sel_faces)
        result = calc_density_multi(sel, int(p.tex_size), selected_only)

        if result is None:
            self.report({"WARNING"}, "No valid UVs found or surface area is zero")
            return {"CANCELLED"}

        p.r_td_cm = result["td_cm"]
        p.r_uv_pct = result["uv_pct"]
        p.r_world_cm2 = result["world_cm2"]
        p.r_obj_count = len(sel)
        p.has_result = True
        return {"FINISHED"}


class JK3DA_OT_SetDensity(bpy.types.Operator):
    bl_idname = "jk3da.set_density"
    bl_label = "Set Density"
    bl_options = {"REGISTER", "UNDO"}

    preset_val: bpy.props.StringProperty(default="")

    def execute(self, context):
        p = context.scene.jk3da_texelkit
        raw = self.preset_val or p.target_td

        if raw == "_HALF":
            if not p.has_result:
                self.report({"WARNING"}, "Run Scan first")
                return {"CANCELLED"}
            target_cm = p.r_td_cm * 0.5
        elif raw == "_DOUBLE":
            if not p.has_result:
                self.report({"WARNING"}, "Run Scan first")
                return {"CANCELLED"}
            target_cm = p.r_td_cm * 2.0
        else:
            try:
                target_display = float(raw.replace(",", "."))
            except ValueError:
                self.report({"WARNING"}, "Invalid TD value — enter a number")
                return {"CANCELLED"}
            target_cm = target_display / UNIT_MULT.get(p.units, 1.0)

        sel = _get_selected_meshes(context)
        if not sel:
            self.report({"WARNING"}, "Select at least one mesh object")
            return {"CANCELLED"}

        was_edit = (context.mode == "EDIT_MESH")
        if was_edit:
            bpy.ops.object.mode_set(mode="OBJECT")

        if p.set_method == "AVG":
            combined = calc_density_multi(sel, int(p.tex_size))
            avg_factor = (target_cm / combined["td_cm"]) if combined and combined["td_cm"] > 1e-6 else None
        else:
            avg_factor = None

        for obj in sel:
            if any(s < 0 for s in obj.scale):
                self.report({"WARNING"}, f"{obj.name}: apply scale first (Ctrl+A)")
                continue

            uv = obj.data.uv_layers.active
            if not uv:
                continue

            if avg_factor is not None:
                factor = avg_factor
            else:
                from .core import calc_density
                result = calc_density(obj, int(p.tex_size))
                if result is None or result["td_cm"] < 1e-6:
                    continue
                factor = target_cm / result["td_cm"]

            if not (0.0 < factor < 1000.0):
                self.report({"WARNING"}, f"{obj.name}: scale factor out of range")
                continue

            coords = [ld.uv[:] for ld in uv.data]
            cx = sum(c[0] for c in coords) / len(coords)
            cy = sum(c[1] for c in coords) / len(coords)
            for ld in uv.data:
                ld.uv = (
                    cx + (ld.uv[0] - cx) * factor,
                    cy + (ld.uv[1] - cy) * factor,
                )

        if was_edit:
            bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.jk3da.scan_density()
        return {"FINISHED"}


class JK3DA_OT_CopyToTarget(bpy.types.Operator):
    bl_idname = "jk3da.copy_to_target"
    bl_label = "Use as Target"

    def execute(self, context):
        p = context.scene.jk3da_texelkit
        if not p.has_result:
            self.report({"WARNING"}, "Nothing scanned yet")
            return {"CANCELLED"}
        display = p.r_td_cm * UNIT_MULT.get(p.units, 1.0)
        p.target_td = f"{display:.3f}"
        return {"FINISHED"}


class JK3DA_OT_NormalizeUVs(bpy.types.Operator):
    bl_idname = "jk3da.normalize_uvs"
    bl_label = "Normalize UVs"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        sel = _get_selected_meshes(context)
        if not sel:
            self.report({"WARNING"}, "Select at least one mesh object")
            return {"CANCELLED"}

        was_edit = (context.mode == "EDIT_MESH")
        if was_edit:
            bpy.ops.object.mode_set(mode="OBJECT")

        for obj in sel:
            uv = obj.data.uv_layers.active
            if not uv:
                continue

            coords = [ld.uv[:] for ld in uv.data]
            min_u = min(c[0] for c in coords)
            max_u = max(c[0] for c in coords)
            min_v = min(c[1] for c in coords)
            max_v = max(c[1] for c in coords)
            span = max(max_u - min_u, max_v - min_v)

            if span < 1e-9:
                continue

            scale = 1.0 / span
            cx = (min_u + max_u) * 0.5
            cy = (min_v + max_v) * 0.5

            for ld in uv.data:
                ld.uv = (
                    0.5 + (ld.uv[0] - cx) * scale,
                    0.5 + (ld.uv[1] - cy) * scale,
                )

        if was_edit:
            bpy.ops.object.mode_set(mode="EDIT")

        bpy.ops.jk3da.scan_density()
        return {"FINISHED"}


class JK3DA_OT_ApplyChecker(bpy.types.Operator):
    bl_idname = "jk3da.apply_checker"
    bl_label = "Preview"

    def execute(self, context):
        p = context.scene.jk3da_texelkit
        sel = _get_selected_meshes(context)
        if not sel:
            self.report({"WARNING"}, "Select at least one mesh object")
            return {"CANCELLED"}

        custom_image = p.checker_image if p.checker_image else None

        for obj in sel:
            assign_checker(obj, p.checker_scale, custom_image)

        for area in context.screen.areas:
            if area.type == "VIEW_3D":
                area.spaces[0].shading.type = "MATERIAL"

        return {"FINISHED"}


class JK3DA_OT_RevertMaterials(bpy.types.Operator):
    bl_idname = "jk3da.revert_materials"
    bl_label = "Revert"

    def execute(self, context):
        sel = _get_selected_meshes(context)
        reverted = sum(1 for obj in sel if revert_materials(obj))
        self.report({"INFO"}, f"Reverted {reverted} object(s)")
        return {"FINISHED"}


from .ui import _scene_report as scene_report_data


class JK3DA_OT_SceneReport(bpy.types.Operator):
    bl_idname = "jk3da.scene_report"
    bl_label = "Scene TD Report"
    bl_options = {"REGISTER"}

    def execute(self, context):
        p = context.scene.jk3da_texelkit
        scene_report_data.clear()

        for obj in context.scene.objects:
            if obj.type != "MESH" or not obj.data.uv_layers:
                continue
            from .core import calc_density
            r = calc_density(obj, int(p.tex_size))
            if r is None:
                continue
            scene_report_data.append({
                "name": obj.name,
                "td_cm": r["td_cm"],
                "uv_pct": r["uv_pct"],
            })

        scene_report_data.sort(key=lambda x: x["td_cm"])

        count = len(scene_report_data)
        self.report({"INFO"}, f"Scanned {count} object(s)")
        return {"FINISHED"}


class JK3DA_OT_SelectReportObject(bpy.types.Operator):
    bl_idname = "jk3da.select_report_obj"
    bl_label = "Select"

    obj_name: bpy.props.StringProperty()

    def execute(self, context):
        target = bpy.data.objects.get(self.obj_name)
        if not target:
            self.report({"WARNING"}, f"Object '{self.obj_name}' not found")
            return {"CANCELLED"}
        bpy.ops.object.select_all(action="DESELECT")
        target.select_set(True)
        context.view_layer.objects.active = target
        return {"FINISHED"}

