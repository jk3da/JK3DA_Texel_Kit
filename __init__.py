bl_info = {
    "name":        "JK3DA Texel Kit",
    "author":      "JK3DA (https://jk3da.com) — AI-assisted development",
    "version":     (1, 0, 0),
    "blender":     (4, 0, 0),
    "category":    "UV",
    "description": "Texel Density scanner, setter and checker preview.",
    "doc_url":     "https://jk3da.com",
}

from .properties import JK3DATexelKitProps
from .operators import (
    JK3DA_OT_ScanDensity,
    JK3DA_OT_SetDensity,
    JK3DA_OT_CopyToTarget,
    JK3DA_OT_NormalizeUVs,
    JK3DA_OT_ApplyChecker,
    JK3DA_OT_RevertMaterials,
    JK3DA_OT_SceneReport,
    JK3DA_OT_SelectReportObject,
)
from .ui import (
    JK3DA_PT_TexelKit,
    JK3DA_PT_TexelKit_UV,
    JK3DA_PT_SceneReport,
)

classes = [
    JK3DATexelKitProps,
    JK3DA_OT_ScanDensity,
    JK3DA_OT_SetDensity,
    JK3DA_OT_CopyToTarget,
    JK3DA_OT_NormalizeUVs,
    JK3DA_OT_ApplyChecker,
    JK3DA_OT_RevertMaterials,
    JK3DA_OT_SceneReport,
    JK3DA_OT_SelectReportObject,
    JK3DA_PT_TexelKit,
    JK3DA_PT_TexelKit_UV,
    JK3DA_PT_SceneReport,
]

import bpy


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.jk3da_texelkit = bpy.props.PointerProperty(type=JK3DATexelKitProps)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.jk3da_texelkit
