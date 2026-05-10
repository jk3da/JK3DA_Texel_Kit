import bpy
from .core import UNIT_MULT, UNIT_LABEL, TD_PRESETS_CM, td_quality
from .report_data import _scene_report


class JK3DA_PT_TexelKit(bpy.types.Panel):
    bl_label = "JK3DA Texel Kit"
    bl_idname = "JK3DA_PT_TexelKit"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "JK3DA Texel Kit"

    @classmethod
    def poll(cls, context):
        return context.active_object is not None

    def draw_header(self, context):
        self.layout.label(text="", icon="COLORSET_02_VEC")

    def draw(self, context):
        layout = self.layout
        p = context.scene.jk3da_texelkit
        obj = context.active_object
        mode = context.mode

        top = layout.row(align=True)
        top.prop(p, "units", text="")
        top.prop(p, "tex_size", expand=True)

        layout.separator(factor=0.3)

        status = layout.box()
        status.scale_y = 0.85

        if not obj or obj.type != "MESH":
            status.label(text="Select a mesh object", icon="ERROR")
            return

        row = status.row(align=True)
        row.label(text=obj.name, icon="MESH_DATA")
        uv_ok = bool(obj.data.uv_layers)
        row.label(
            text=obj.data.uv_layers.active.name if uv_ok else "No UV map",
            icon="UV" if uv_ok else "ERROR",
        )

        mesh_sel = [o for o in context.selected_objects if o.type == "MESH"]
        if len(mesh_sel) > 1:
            status.label(text=f"{len(mesh_sel)} meshes selected", icon="COLORSET_02_VEC")

        if mode == "EDIT_MESH":
            status.prop(p, "sel_faces", icon="FACESEL")

        bad_scale = [
            o for o in (mesh_sel or [obj])
            if o.type == "MESH" and any(abs(s - 1.0) > 0.001 for s in o.scale)
        ]
        if bad_scale:
            warn = layout.box()
            warn.alert = True
            warn.label(text="Apply Scale first!  Ctrl+A", icon="ERROR")
            warn.label(text=", ".join(o.name for o in bad_scale[:3]))

        layout.separator(factor=0.3)

        scan_row = layout.row()
        scan_row.scale_y = 1.6
        scan_row.operator("jk3da.scan_density", text="SCAN DENSITY", icon="VIEWZOOM")

        if p.has_result:
            layout.separator(factor=0.3)
            res = layout.box()

            display_td = p.r_td_cm * UNIT_MULT.get(p.units, 1.0)
            unit_label = UNIT_LABEL.get(p.units, "px/cm")
            q_label, q_icon = td_quality(p.r_td_cm)

            big = res.row(align=True)
            big.scale_y = 1.3
            big.label(text=f"{display_td:.2f} {unit_label}", icon="COLORSET_02_VEC")
            big.label(text=q_label, icon=q_icon)

            grid = res.grid_flow(row_major=True, columns=2, align=True)
            grid.label(text="UV Space")
            grid.label(text=f"{p.r_uv_pct:.1f} %")
            grid.label(text="World Area")
            grid.label(text=f"{p.r_world_cm2:.0f} cm2")
            if p.r_obj_count > 1:
                grid.label(text="Objects")
                grid.label(text=str(p.r_obj_count))

            res.operator("jk3da.copy_to_target", text="Use as Target", icon="COPYDOWN")

        layout.separator(factor=0.3)

        tgt = layout.box()
        tgt.label(text="Set Density", icon="IMPORT")

        row = tgt.row(align=True)
        row.prop(p, "target_td", text="")
        row.label(text=UNIT_LABEL.get(p.units, "px/cm"))
        row.prop(p, "set_method", text="")

        tgt.operator("jk3da.set_density", text="Apply", icon="IMPORT")
        tgt.operator("jk3da.normalize_uvs", text="Normalize UVs", icon="UV")

        tgt.separator(factor=0.3)
        mult = UNIT_MULT.get(p.units, 1.0)
        for preset_row in TD_PRESETS_CM:
            row = tgt.row(align=True)
            for val_cm in preset_row:
                display_v = float(val_cm) * mult
                label = f"{display_v:.2f}".rstrip("0").rstrip(".")
                op = row.operator("jk3da.set_density", text=label)
                op.preset_val = val_cm

        half_double = tgt.row(align=True)
        half_double.operator("jk3da.set_density", text="x 0.5", icon="REMOVE").preset_val = "_HALF"
        half_double.operator("jk3da.set_density", text="x 2", icon="ADD").preset_val = "_DOUBLE"

        layout.separator(factor=0.3)

        chk = layout.box()
        chk.label(text="Checker Preview", icon="MATERIAL")

        chk.template_ID(p, "checker_image", open="image.open")

        if not p.checker_image:
            chk.label(text="Default: Orange / Dark checker", icon="INFO")

        chk.prop(p, "checker_scale", text="Scale")

        btn = chk.row(align=True)
        btn.scale_y = 1.2
        btn.operator("jk3da.apply_checker", text="Preview", icon="HIDE_OFF")
        btn.operator("jk3da.revert_materials", text="Revert", icon="LOOP_BACK")


class JK3DA_PT_TexelKit_UV(bpy.types.Panel):
    bl_label = "JK3DA Texel Kit"
    bl_idname = "JK3DA_PT_TexelKit_UV"
    bl_space_type = "IMAGE_EDITOR"
    bl_region_type = "UI"
    bl_category = "JK3DA Texel Kit"

    @classmethod
    def poll(cls, context):
        return (
            context.active_object is not None
            and context.active_object.type == "MESH"
            and context.space_data.mode == "UV"
        )

    def draw_header(self, context):
        self.layout.label(text="", icon="COLORSET_02_VEC")

    def draw(self, context):
        layout = self.layout
        p = context.scene.jk3da_texelkit
        obj = context.active_object
        mode = context.mode

        top = layout.row(align=True)
        top.prop(p, "units", text="")
        top.prop(p, "tex_size", expand=True)

        layout.separator(factor=0.3)

        status = layout.box()
        status.scale_y = 0.85

        row = status.row(align=True)
        row.label(text=obj.name, icon="MESH_DATA")
        uv_ok = bool(obj.data.uv_layers)
        row.label(
            text=obj.data.uv_layers.active.name if uv_ok else "No UV map",
            icon="UV" if uv_ok else "ERROR",
        )

        mesh_sel = [o for o in context.selected_objects if o.type == "MESH"]
        if len(mesh_sel) > 1:
            status.label(text=f"{len(mesh_sel)} meshes selected", icon="COLORSET_02_VEC")

        if mode == "EDIT_MESH":
            status.prop(p, "sel_faces", icon="FACESEL")

        bad_scale = [
            o for o in (mesh_sel or [obj])
            if o.type == "MESH" and any(abs(s - 1.0) > 0.001 for s in o.scale)
        ]
        if bad_scale:
            warn = layout.box()
            warn.alert = True
            warn.label(text="Apply Scale first!  Ctrl+A", icon="ERROR")
            warn.label(text=", ".join(o.name for o in bad_scale[:3]))

        layout.separator(factor=0.3)

        scan_row = layout.row()
        scan_row.scale_y = 1.5
        scan_row.operator("jk3da.scan_density", text="SCAN DENSITY", icon="VIEWZOOM")

        if p.has_result:
            layout.separator(factor=0.3)
            res = layout.box()

            display_td = p.r_td_cm * UNIT_MULT.get(p.units, 1.0)
            unit_label = UNIT_LABEL.get(p.units, "px/cm")
            q_label, q_icon = td_quality(p.r_td_cm)

            big = res.row(align=True)
            big.scale_y = 1.3
            big.label(text=f"{display_td:.2f} {unit_label}", icon="COLORSET_02_VEC")
            big.label(text=q_label, icon=q_icon)

            grid = res.grid_flow(row_major=True, columns=2, align=True)
            grid.label(text="UV Space")
            grid.label(text=f"{p.r_uv_pct:.1f} %")
            grid.label(text="World Area")
            grid.label(text=f"{p.r_world_cm2:.0f} cm2")
            if p.r_obj_count > 1:
                grid.label(text="Objects")
                grid.label(text=str(p.r_obj_count))

            res.operator("jk3da.copy_to_target", text="Use as Target", icon="COPYDOWN")

        layout.separator(factor=0.3)

        tgt = layout.box()
        tgt.label(text="Set Density", icon="IMPORT")

        row = tgt.row(align=True)
        row.prop(p, "target_td", text="")
        row.label(text=UNIT_LABEL.get(p.units, "px/cm"))
        row.prop(p, "set_method", text="")

        tgt.operator("jk3da.set_density", text="Apply", icon="IMPORT")
        tgt.operator("jk3da.normalize_uvs", text="Normalize UVs", icon="UV")

        tgt.separator(factor=0.3)
        mult = UNIT_MULT.get(p.units, 1.0)
        for preset_row in TD_PRESETS_CM:
            row = tgt.row(align=True)
            for val_cm in preset_row:
                display_v = float(val_cm) * mult
                label = f"{display_v:.2f}".rstrip("0").rstrip(".")
                op = row.operator("jk3da.set_density", text=label)
                op.preset_val = val_cm

        half_double = tgt.row(align=True)
        half_double.operator("jk3da.set_density", text="x 0.5", icon="REMOVE").preset_val = "_HALF"
        half_double.operator("jk3da.set_density", text="x 2", icon="ADD").preset_val = "_DOUBLE"

        layout.separator(factor=0.3)

        chk = layout.box()
        chk.label(text="Checker Preview", icon="MATERIAL")

        chk.template_ID(p, "checker_image", open="image.open")

        if not p.checker_image:
            chk.label(text="Default: Orange / Dark checker", icon="INFO")

        chk.prop(p, "checker_scale", text="Scale")

        btn = chk.row(align=True)
        btn.scale_y = 1.2
        btn.operator("jk3da.apply_checker", text="Preview", icon="HIDE_OFF")
        btn.operator("jk3da.revert_materials", text="Revert", icon="LOOP_BACK")


class JK3DA_PT_SceneReport(bpy.types.Panel):
    bl_label = "Scene TD Report"
    bl_idname = "JK3DA_PT_SceneReport"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "JK3DA Texel Kit"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        self.layout.label(text="", icon="SPREADSHEET")

    def draw(self, context):
        global _scene_report
        layout = self.layout
        p = context.scene.jk3da_texelkit

        layout.operator("jk3da.scene_report", text="Scan Scene", icon="SPREADSHEET")

        if not _scene_report:
            layout.label(text="No results — click Scan Scene", icon="INFO")
            return

        mult = UNIT_MULT.get(p.units, 1.0)
        unit_label = UNIT_LABEL.get(p.units, "px/cm")

        header = layout.row(align=True)
        header.label(text="Object")
        header.label(text="TD")
        header.label(text="UV%")

        layout.separator(factor=0.2)

        for entry in _scene_report:
            q_label, q_icon = td_quality(entry["td_cm"])
            display_td = entry["td_cm"] * mult

            row = layout.row(align=True)
            row.scale_y = 0.9

            op = row.operator(
                "jk3da.select_report_obj",
                text=entry["name"][:18],
                icon=q_icon,
                emboss=False,
            )
            op.obj_name = entry["name"]

            row.label(text=f"{display_td:.1f}")
            row.label(text=f"{entry['uv_pct']:.0f}%")
