import bpy

ID_OP_ADD = "gl.add_instance"
ID_OP_REMOVE = "gl.remove_instance"
ID_INSTANCE_enable = "enabled"
ID_INSTANCE_expand = "expanded"

def _get_GPU():
    from bpy_gl import GLSLbase
    return GLSLbase
GPUobjs = []
# ---------------------------------------------------------
def toggle(self, context):
    GL = _get_GPU()
    GL.load_shader(self.shaderType)

    if self.enabled and self.handler_id == -1:
        i=0
        for d in bpy.context.scene.gl_stack:
            if self == d:
                self.handler_id = i
                break
            else:
                i+=1

        while GPUobjs.__len__() <= self.handler_id:
            GPUobjs.append(None)

        pair = bpy.gl_stream[self.shaderType]
        shader = pair[1]
        desc = pair[0]
        ui_spec = getattr(
            self, 
            self.shaderType, 
            None
        )

        args = (
            shader,
            desc.CALL_BATCH(shader,ui_spec),
            ui_spec
        )

        handler = bpy.types.SpaceView3D.draw_handler_add(
            desc.CALL_EXEC, args,
            desc.DRAW_REGION, desc.DRAW_TYPE
        )
        GPUobjs[self.handler_id]=handler
    
    elif not self.enabled and self.handler_id != -1:
        pair = bpy.gl_stream[self.shaderType]
        desc = pair[0]
        bpy.types.SpaceView3D.draw_handler_remove(
            GPUobjs[self.handler_id], desc.DRAW_REGION
        )
        GPUobjs[self.handler_id] = None
        self.handler_id = -1

class gl_instance_sk(bpy.types.PropertyGroup):
    shaderType: bpy.props.StringProperty(name="shader", default="")
    enabled: bpy.props.BoolProperty(default=False, update=toggle)
    expanded: bpy.props.BoolProperty(default=True)
    handler_id : bpy.props.IntProperty(default=-1)

#-------------------------------------------------------------

def get_items(self, context):
    return [(key, key, "") for key in bpy.gl_stream.keys()]
class gl_OP_add_instance(bpy.types.Operator):
    bl_idname = ID_OP_ADD
    bl_label = "Add GLSL Instance"

    selected_type: bpy.props.EnumProperty(
        name="shaders",
        items=get_items
    )

    def invoke(self, context, event):
            wm = context.window_manager
            return wm.invoke_props_dialog(self)

    def execute(self, context):
        new_i = context.scene.gl_stack.add()
        new_i.shaderType = self.selected_type
        return {'FINISHED'}

class gl_OP_remove_instance(bpy.types.Operator):
    bl_idname = ID_OP_REMOVE
    bl_label = ""
    index_i : bpy.props.IntProperty(default=-1)

    def execute(self, context):
        if self.index_i < 0:
            return {'CANCELED'}
        x = bpy.context.scene.gl_stack[self.index_i]
        x.enabled = False
        bpy.context.scene.gl_stack.remove(self.index_i)
        return {'FINISHED'}
#-------------------------------------------------------------
class gl_panel(bpy.types.Panel):
    bl_label = "GLSL"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'GLSL manager'

    def draw(self, context):
        layout = self.layout

        box = layout.box()
        row = box.row(align=True)

        row.operator(ID_OP_ADD, text="Add Instance")

        i = 0
        for item in context.scene.gl_stack:
            box = layout.box()
            row = box.row(align=True)
            
            row.prop(item, ID_INSTANCE_expand,
                icon='TRIA_DOWN' if item.expanded else 'TRIA_RIGHT',
                icon_only=True, emboss=False
            )
            row.label(text=item.shaderType, 
                icon='SHADING_RENDERED')
            row.prop(item, ID_INSTANCE_enable, text="")
            
            op_R = row.operator(ID_OP_REMOVE, 
                              text="", icon='X')
            op_R.index_i = i # Index Save

            if not item.expanded:
                continue

            custom_params = getattr(item,item.shaderType)
            for prop in custom_params.bl_rna.properties:
                row=box.row(align=True)
                row.prop(custom_params,prop.identifier)
            i+=1

classes = [
    gl_instance_sk, 
    gl_OP_add_instance,
    gl_OP_remove_instance,
    gl_panel
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    for pair in bpy.gl_stream.values():
        desc = pair[0]
        bpy.utils.register_class(desc.PARAMS)
        setattr(
            gl_instance_sk, desc.NAME,
            bpy.props.PointerProperty(type=desc.PARAMS)
        )
    bpy.types.Scene.gl_stack = bpy.props.CollectionProperty(type=gl_instance_sk)
