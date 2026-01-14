ID_OP_ADD_INSTANCE    = "pbnpr.add_instance"
ID_OP_REMOVE_INSTANCE = "pbnpr.remove_instance"
ID_INSTANCE_name       = "name"
ID_INSTANCE_shaderType = "shaderType"
ID_INSTANCE_enabled    = "enable"
ID_INSTANCE_expanded   = "expand"
ID_INSTANCE_params     = "params"

import bpy
GPUobjs = [] # [ [batch,Use_Handler,handler], ... ]

# ------------------------------------------------------------
def toggle_gpu_handler(self, context):
    """Constructor/Destructor for the GPU handler triggered by the 'enable' prop."""
    stack = context.scene.pbnpr_stack
    idx = -1
    for i, block in enumerate(stack):
        if block == self:
            idx = i
            break
    
    if idx == -1: return

    # --- THE FIX: Ensure GPUobjs index exists ---
    while len(GPUobjs) <= idx:
        GPUobjs.append([None, False, None]) # [batch, is_active, handler_ptr] 

    gpu_data = GPUobjs[idx]
    desc_data = bpy.gl_descs.get(self.shaderType)
    
    # If batch wasn't created yet (e.g. after file reload), create it now
    if gpu_data[0] is None and desc_data:
        gpu_data[0] = desc_data[0].CALL_BATCH(desc_data[1])

    if self.enable:
        if gpu_data[2] is None and desc_data:
            # Add handler and store the pointer in our parallel list
            gpu_data[2] = bpy.types.SpaceView3D.draw_handler_add(
                desc_data[0].CALL_EXEC, 
                (desc_data[1], gpu_data[0], getattr(self, f"ptr_{self.shaderType}")), 
                'WINDOW', 'POST_VIEW'
            )
    else:
        if gpu_data[2] is not None:
            bpy.types.SpaceView3D.draw_handler_remove(gpu_data[2], 'WINDOW')
            gpu_data[2] = None
class gl_Instance_data_base(bpy.types.PropertyGroup):
    name:       bpy.props.StringProperty(default="Shader")
    shaderType: bpy.props.StringProperty(default="XAXA")
    # Trigger the toggle logic whenever this changes 
    enable:     bpy.props.BoolProperty(default=False, update=toggle_gpu_handler) 
    expand:     bpy.props.BoolProperty(default=True)


# ------------------------------------------------------------
class gl_OP_MenuButton(bpy.types.Operator):
    bl_idname = ID_OP_ADD_INSTANCE
    bl_label = "Add Shader"
    shader: bpy.props.EnumProperty( #-X
        name="Shader",
        items=lambda self, ctx: [
                                    (k, k, "") for k in bpy.gl_descs.keys()
                                ] 
                                or [("NONE", "No shaders", "")]
            )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        block            = context.scene.pbnpr_stack.add()
        block.shaderType = self.shader
        block.name       = self.shader
        return {'FINISHED'}

class gl_OP_RemoveInstance(bpy.types.Operator):
    bl_idname = ID_OP_REMOVE_INSTANCE
    bl_label = "Remove Shader"

    index: bpy.props.IntProperty()#-X

    def execute(self, context):
        context.scene.pbnpr_stack.remove(self.index)
        return {'FINISHED'}


# ------------------------------------------------------------
class gl_Panel(bpy.types.Panel):
    bl_label = "PBNPR Shaders"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PBNPR'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        layout.operator(ID_OP_ADD_INSTANCE, 
                        icon='ADD')
 
        for i, block in enumerate(scene.pbnpr_stack):
            box = layout.box()
            row = box.row(align=True)

            row.prop(block, ID_INSTANCE_expanded,
                icon='TRIA_DOWN' if block.expand else 'TRIA_RIGHT',
                icon_only=True, emboss=False
            )
            row.label(text=block.name, 
                      icon='SHADING_RENDERED')
            row.prop(block, ID_INSTANCE_enabled, 
                     text="")

            op_R = row.operator(ID_OP_REMOVE_INSTANCE, 
                              text="", icon='X')
            op_R.index = i # Index Save

            if block.expand: 
                col = box.column(align=True) 
                active_ptr_name = f"ptr_{block.shaderType}"
                params = getattr(block, active_ptr_name, None) 
                
                for prop in params.bl_rna.properties: 
                    col.prop(params, prop.identifier)


# ------------------------------------------------------------

classes = (
    gl_Instance_data_base,
    gl_OP_MenuButton,
    gl_OP_RemoveInstance,
    gl_Panel
)

def register():
    bpy.utils.register_class(gl_Instance_data_base)
    
    for desc in bpy.gl_descs.values():
        desc = desc[0]
        bpy.utils.register_class(desc.UI_DATA)
        
        attr_name = f"ptr_{desc.NAME}" # e.g., ptr_TEMPLATE

        setattr(
            gl_Instance_data_base, 
            attr_name, 
            bpy.props.PointerProperty(type=desc.UI_DATA)
        )
    for cl in classes:
        try:
            bpy.utils.register_class(cl)
        except:
            continue    
    bpy.types.Scene.pbnpr_stack = bpy.props.CollectionProperty(type=gl_Instance_data_base)
    
def unregister():
    GPUobjs.clear()
    try:
        for i in bpy.gl_descs.values():
            bpy.utils.unregister_class(i[0].UI_DATA)
    except:
        pass
    try:
        del bpy.types.Scene.pbnpr_stack

        for cls in reversed(classes):
            bpy.utils.unregister_class(cls)
    except:
        pass
    for h in GPUobjs:
        if h[2] is not None:
            try:bpy.types.SpaceView3D.draw_handler_remove(h[2])
            except:pass