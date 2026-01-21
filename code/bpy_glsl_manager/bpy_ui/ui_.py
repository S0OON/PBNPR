import bpy 
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
import importlib.util
import shutil
import os

#===========================================================
def _get_streamKeys(self, context):
    items = [("Select", "Select Shader...", "")]
    for key in bpy.gl_stream.keys():
        items.append((key, key, f"Load {key} shader"))
    return items

#====================CONSTANT===============================
ID_OP_ADD_MOD_FROM_DIR = "gl.import_shader"
ID_OP_ADD_TEMP_MOD     = "gl.export_shader_template"
ID_OP_REMOVE           = "gl.remove_instance"
#===========================================================
def toggle(self, context):
    if self.enabled and self.handler_id == -1:
        i=0
        for j in bpy.context.scene.gl_stack:
            if self == j:
                self.handler_id = i
                break
            i+=1
        
        while bpy.gl_Hs.__len__() <= self.handler_id:
            bpy.gl_Hs.append(None)

        pair =    bpy.gl_stream[self.shaderType]
        desc =    pair[0]
        desc.CALL_REG()
        shader =  pair[1]
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
        
        bpy.gl_Hs[self.handler_id]=handler
    
    elif not self.enabled and self.handler_id != -1:
        pair = bpy.gl_stream[self.shaderType]
        desc = pair[0]
        
        bpy.types.SpaceView3D.draw_handler_remove(
            bpy.gl_Hs[self.handler_id], 
            desc.DRAW_REGION
        )
        bpy.gl_Hs[self.handler_id] = None
        self.handler_id = -1
class gl_instance_sk(bpy.types.PropertyGroup):
    enabled:     bpy.props.BoolProperty(default=False, update=toggle)
    expanded:    bpy.props.BoolProperty(default=True)
    shaderType:  bpy.props.StringProperty(name="shader", default="")
    handler_id : bpy.props.IntProperty(default=-1)

#=========================================================== 
def tog_enum(self, context):
    if self.selected_type == "Select": 
        return
    new_i = context.scene.gl_stack.add()
    new_i.shaderType = self.selected_type
    self.selected_type = "Select" 
class gl_mainSettings(bpy.types.PropertyGroup):
    selected_type: bpy.props.EnumProperty(
        name="", items=_get_streamKeys, update=tog_enum
    ) 

#=========================================================== 
class gl_OP_remove_instance(bpy.types.Operator):
    bl_idname = ID_OP_REMOVE
    bl_label = ""
    index_i : bpy.props.IntProperty(default=-1)

    def execute(self, context):
        stack = context.scene.gl_stack
        if 0 <= self.index_i < len(stack):
            stack[self.index_i].enabled = False # Triggers toggle() to remove handler
            stack.remove(self.index_i)
        return {'FINISHED'}

class gl_OP_Export_templateMOD(bpy.types.Operator, ExportHelper): # Use ExportHelper for folders
    bl_idname = ID_OP_ADD_TEMP_MOD
    bl_label = "Create New Shader Project"
    filename_ext = "" 
    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        addon_dir = os.path.dirname(os.path.dirname(__file__))
        template_src = os.path.join(addon_dir, "src_template")
        target_dir = os.path.join(self.directory, "new_shader")
        
        try:
            shutil.copytree(template_src, target_dir)
            self.report({'INFO'}, f"Template created: {target_dir}")
        except Exception as e:
            self.report({'ERROR'}, f"Export Failed: {str(e)}")
        return {'FINISHED'}
    
    def invoke(self, context, event):
        # We force the file selector to open
        # For folders, we ensure the directory property is used
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class gl_OP_import_shaderMOD(bpy.types.Operator, ImportHelper):
    bl_idname = ID_OP_ADD_MOD_FROM_DIR
    bl_label = "Load Shader Script"

    filter_glob: bpy.props.StringProperty(default="*.py", options={'HIDDEN'})

    def execute(self, context):
        try:
            spec = importlib.util.spec_from_file_location("dynamic_mod", self.filepath)
            ext_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(ext_mod)
            
            desc = ext_mod.DESCRIPTION
            bpy.gl_stream[desc.NAME]=[desc,None]
            desc.CALL_REG() # Compilation Test
            
            # UI Registration
            if not hasattr(gl_instance_sk, desc.NAME):
                bpy.utils.register_class(desc.PARAMS)
                setattr(gl_instance_sk, desc.NAME, bpy.props.PointerProperty(type=desc.PARAMS))
                
            self.report({'INFO'}, f"Loaded {desc.NAME}")
        except Exception as e:
            self.report({'ERROR'}, f"Failed: {e}")
        return {'FINISHED'}

    def invoke(self, context, event):
        # This ensures the window pops up even if called from a script
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#===========================================================
class gl_panel(bpy.types.Panel):
    bl_label = "GLSL Manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PBNPR'

    def draw(self, context):
        layout = self.layout
        SETTINGS = context.scene.settings

        box = layout.box()
        row = box.row(align=True)
        row.operator(ID_OP_ADD_TEMP_MOD, icon='NEWFOLDER', text='New Template')
        row.operator(ID_OP_ADD_MOD_FROM_DIR, icon='FILE_NEW', text='Import')

        row = box.row()
        row.prop(SETTINGS, "selected_type")

        for i, INST in enumerate(context.scene.gl_stack):
            box = layout.box()
            row = box.row(align=True)
            
            row.prop(INST, "expanded", 
                icon='TRIA_DOWN' if INST.expanded else 'TRIA_RIGHT',
                icon_only=True, emboss=False
            )
            row.label(text=INST.shaderType, icon='SHADING_RENDERED')
            row.prop(INST, "enabled", text="")
            
            op = row.operator(ID_OP_REMOVE, text="", icon='X')
            op.index_i = i 

            if INST.expanded:
                custom_params = getattr(INST, INST.shaderType, None)
                if custom_params:
                    col = box.column(align=True)
                    for prop in custom_params.bl_rna.properties:
                        if not prop.is_readonly: # Skip internal RNA props
                            col.prop(custom_params, prop.identifier)

#===========================================================
classes = (
    gl_instance_sk, 
    gl_mainSettings,
    gl_OP_remove_instance,
    gl_OP_Export_templateMOD,
    gl_OP_import_shaderMOD,
    gl_panel
)

def register():
    for cl in classes:
        bpy.utils.register_class(cl)
    
    bpy.types.Scene.settings = bpy.props.PointerProperty(type=gl_mainSettings)
    bpy.types.Scene.gl_stack = bpy.props.CollectionProperty(type=gl_instance_sk)

    # Register initial stream shaders
    if hasattr(bpy, "gl_stream"):
        for pair in bpy.gl_stream.values():
            desc = pair[0]
            if not hasattr(gl_instance_sk, desc.NAME):
                bpy.utils.register_class(desc.PARAMS)
                setattr(gl_instance_sk, desc.NAME, bpy.props.PointerProperty(type=desc.PARAMS))

def unregister():
    # Properly remove handlers before closing
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
    del bpy.types.Scene.settings
    del bpy.types.Scene.gl_stack