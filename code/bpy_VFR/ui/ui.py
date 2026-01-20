import bpy
ID_OP_MAKE_FRAMES = "vrf.frame_maker"

Prop = bpy.props
def _get_settings(context):
    return context.scene.sets_vfr
#==============================================================

class V_OP_makeFrames(bpy.types.Operator):
    bl_idname = ID_OP_MAKE_FRAMES
    bl_label = "Make seq"

    def execute(self, context):
        settings = _get_settings(context)
        
        return {"FINISHED"}
#==============================================================
def tog(self,context):
    self.stack = "Choose a modif"
class V_settings(bpy.types.PropertyGroup):
    seq_name:Prop.StringProperty(default="Template")
    frames_length:Prop.IntProperty(default=0)
    stack : Prop.EnumProperty(
        name="",
        items=[
            ("Choose a modif","Choose a modif",""),
            ("A","A",""),
            ("AA","AA","")
        ],
        update=tog
    )

class V_Panel(bpy.types.Panel):
    bl_label = "VRP - paint"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = "VRP"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        box = layout.box()
        row = box.row(align=True)

        settings = _get_settings(context)
        for prop in settings.bl_rna.properties:
            row.prop(
                settings,
                prop.identifier
            )
            row=box.row()


#==============================================================
classes = (
    V_settings,
    V_Panel
)
def register():
    for cl in classes:
        bpy.utils.register_class(cl)
    bpy.types.Scene.sets_vfr = bpy.props.PointerProperty(type=V_settings)
