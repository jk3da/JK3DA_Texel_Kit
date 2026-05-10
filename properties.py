import bpy
from .core import UNIT_MULT, UNIT_LABEL, TD_PRESETS_CM, td_quality
from .checker import _update_checker_scale


class JK3DATexelKitProps(bpy.types.PropertyGroup):

    tex_size: bpy.props.EnumProperty(
        name="Texture Size",
        description="Reference texture resolution for TD calculation",
        items=[
            ("512",  "512",  ""),
            ("1024", "1024", ""),
            ("2048", "2048", ""),
            ("4096", "4096", ""),
        ],
        default="1024",
    )
    units: bpy.props.EnumProperty(
        name="Units",
        description="Display unit for Texel Density values",
        items=[
            ("CM", "px/cm", "Pixels per centimetre"),
            ("M",  "px/m",  "Pixels per metre"),
            ("IN", "px/in", "Pixels per inch"),
            ("FT", "px/ft", "Pixels per foot"),
        ],
        default="CM",
    )
    sel_faces: bpy.props.BoolProperty(
        name="Selected Faces Only",
        description="In Edit Mode: calculate only on selected faces",
        default=False,
    )

    target_td: bpy.props.StringProperty(
        name="Target TD",
        description="Desired Texel Density value in the current unit",
        default="10.24",
    )
    set_method: bpy.props.EnumProperty(
        name="Method",
        description="How to scale UVs across multiple islands",
        items=[
            ("EACH", "Each",    "Scale each island independently"),
            ("AVG",  "Average", "Scale all islands by the same factor"),
        ],
        default="EACH",
    )

    checker_image: bpy.props.PointerProperty(
        name="Checker Image",
        description="Custom checker map. Leave empty to use a generated grid",
        type=bpy.types.Image,
    )
    checker_type: bpy.props.EnumProperty(
        name="Grid Type",
        description="Fallback when no custom image is selected",
        items=[
            ("COLOR_GRID", "Color Grid", "Colourful UV checker grid"),
            ("UV_GRID",    "UV Grid",    "Classic black-and-white UV grid"),
        ],
        default="COLOR_GRID",
    )
    checker_res: bpy.props.EnumProperty(
        name="Resolution",
        description="Resolution of the generated fallback grid",
        items=[
            ("512",  "512",  ""),
            ("1024", "1024", ""),
            ("2048", "2048", ""),
        ],
        default="1024",
    )

    def _on_scale_change(self, context):
        _update_checker_scale(self.checker_scale)

    checker_scale: bpy.props.FloatProperty(
        name="Scale",
        description="Number of checker tiles across one UV unit",
        default=8.0, min=0.5, max=128.0,
        update=_on_scale_change,
    )

    has_result: bpy.props.BoolProperty(default=False)
    r_td_cm: bpy.props.FloatProperty(default=0.0)
    r_uv_pct: bpy.props.FloatProperty(default=0.0)
    r_world_cm2: bpy.props.FloatProperty(default=0.0)
    r_obj_count: bpy.props.IntProperty(default=0)
