# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
import bpy 
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
import importlib.util
import shutil
import sys
import os
#====================CONSTANT===============================
ID_OP_ADD_MOD_FROM_DIR = "gl.import_shader"
ID_OP_EX_TEMP_MOD      = "gl.export_shader_template"
ID_OP_REMOVE           = "gl.remove_instance"
ID_INST_add_shader_i   = "selected_type_add"
ID_INST_rem_shader_i   = "selected_type_remove"
#====================PANEL===============================
class gl_panel(bpy.types.Panel):
    bl_label       = "GLSL Manager"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'PBNPR'

    def draw(self, context):
        layout   = self.layout
        STACK    = bpy.context.scene.gl_stack
        SETTINGS = bpy.context.scene.gl_settings

        box = layout.box()
        row = box.row(align=True)
        row.operator(ID_OP_EX_TEMP_MOD,     icon='NEWFOLDER',text='Export project')
        row.operator(ID_OP_ADD_MOD_FROM_DIR, icon='FILE_NEW', text='import shader.py')

        row = box.row()
        row.prop(SETTINGS, ID_INST_add_shader_i, text="Add a shader type block")
        row = box.row() 
        row.prop(SETTINGS, ID_INST_rem_shader_i, text="Remove a shader type")

        for i, INST in enumerate(STACK):
            box = layout.box()
            row = box.row(align=True)
            
            row.prop(INST, "expanded", 
                icon='TRIA_DOWN' if INST.expanded else 'TRIA_RIGHT',
                icon_only=True, emboss=False
            )
            row.label(text=INST.shaderType, icon='SHADING_RENDERED')
            row.prop(INST, "enabled", text="")
            
            op         = row.operator(ID_OP_REMOVE, text="", icon='X')
            op.index_i = i 

            if INST.expanded:
                custom_params = getattr(
                    INST, 
                    f"ptr_{INST.shaderType}", 
                    None
                )
                bpy.gl_stream[INST.shaderType][0].CALL_UI_SPEC(self,custom_params)

#====================INSTANCE===============================
class gl_panel_shader_unit(bpy.types.PropertyGroup):
    """A container of the shaderType + its ui constraints."""
    enabled:     bpy.props.BoolProperty(default=False)  # pyright: ignore[reportInvalidTypeForm]
    expanded:    bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    shaderType:  bpy.props.StringProperty(default="") # pyright: ignore[reportInvalidTypeForm]
    view_handler = None

#====================SETTINGS AND OPS===============================
def tog_shType_add(self, context):
    target = self.selected_type_add 
    if target == "Select": 
        return
    STACK = bpy.context.scene.gl_stack

    new_i = STACK.add()
    new_i.shaderType = target

    target = "Select" 
def tog_shType_remove(self, context):
    target = self.selected_type_remove
    if target == "Select": 
        return
    # Clear the target relatives
    STACK = bpy.context.scene.gl_stack
    for i,j in enumerate(STACK):
        if j.shaderType == target:
            j.enabled = False
            STACK.remove(i)
    delattr(
        gl_instance_sk,
        f"ptr_{target}"
    )
    # remove shader type key in gl_stream
    try:
        bpy.gl_stream[target][0].CALL_UNREG()
    except Exception as e:
        print(f"[UI SETTINGS DEL REPORT] Couldnt UNREGISTER this shader type: {target} | error: {e}")
    bpy.gl_stream.pop(target)
    if target in sys.modules:
        del sys.modules[target]
    target = "Select"

class gl_Panel_header_settings(bpy.types.PropertyGroup):
    selected_type_add: bpy.props.EnumProperty(
        name="", update=tog_shType_add, 
        items =_get_streamKeys
    ) # pyright: ignore[reportInvalidTypeForm]
    selected_type_remove: bpy.props.EnumProperty(
        name="", update=tog_shType_remove, 
        items=_get_streamKeys
    ) # pyright: ignore[reportInvalidTypeForm]

class gl_OP_remove_instance(bpy.types.Operator):
    bl_idname = ID_OP_REMOVE
    bl_label = ""
    index_i : bpy.props.IntProperty(default=-1) # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        stack = bpy.context.scene.gl_stack
        if self.index_i < len(stack):
            stack[self.index_i].enabled = False # Triggers toggle() to remove handler
            stack.remove(self.index_i)
        return {'FINISHED'}

#====================PROJECT DIRECTORY MANAGEMENT===============================
class gl_OP_Export_templateMOD(bpy.types.Operator, ExportHelper): # Use ExportHelper for folders
    bl_idname    = ID_OP_EX_TEMP_MOD
    bl_label     = "Create New Shader Project"
    filename_ext = "" 
    directory:   bpy.props.StringProperty(subtype='DIR_PATH') # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        template_src = os.path.dirname(GLSL_DEFAULT.__file__)
        target_dir   = os.path.join(self.directory, "new_shader")
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

def safe_import_mod(filepath):
    """
    Dynamically imports a Python file into Blender.
    Ensures the module is reloaded fresh for debugging.
    """
    try:
        # 1. Get Absolute Path and Name
        mod_path = os.path.abspath(filepath)
        # Use the filename as the module key (e.g., 'my_shader' from '*/my_shader.py')
        mod_name = os.path.splitext(os.path.basename(mod_path))[0]

        # 2. FORCE RELOAD
        if mod_name in sys.modules:
            del sys.modules[mod_name]

        # 3. Create the Spec (idk some perCursor of importyed *.py)
        spec = importlib.util.spec_from_file_location(mod_name,mod_path)
        
        if spec is None or spec.loader is None:
            print(f"Error: Could not find a valid Python spec for {mod_path}")
            return None

        # 4. Load and Execute
        ext_mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = ext_mod # register in system
        spec.loader.exec_module(ext_mod)
        return ext_mod
    except Exception as e:
        print(f"Safe Import Failed: {e}")
        return None
    
class gl_OP_import_shaderMOD(bpy.types.Operator, ImportHelper):
    bl_idname = ID_OP_ADD_MOD_FROM_DIR
    bl_label = "Load Shader Script"

    filter_glob: bpy.props.StringProperty(default="*.py", options={'HIDDEN'}) # pyright: ignore[reportInvalidTypeForm]

    def execute(self, context):
        ext_mod = safe_import_mod(self.filepath)
        
        if ext_mod:
            from .GLSLbase import assign_shader
            m = assign_shader(ext_mod)
            if m == None:
                return
            desc = m[0]
            
            setattr(
                gl_instance_sk, f"ptr_{desc.NAME}", 
                bpy.props.PointerProperty(type=desc.UI)
            )
            
            self.report({'INFO'}, f"Freshly Loaded: {desc.NAME}")
            return {'FINISHED'}
            
        self.report({'ERROR'}, "Import failed. Check Console.")
        return {'CANCELLED'}

    def invoke(self, context, event):
        # This ensures the window pops up even if called from a script
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

#======================STARTUPS==========================
classes = (
    
)

def register():
    for cl in classes: 
        bpy.utils.register_class(cl)
    bpy.types.Scene.gl_settings = bpy.props.PointerProperty(type=gl_Panel_header_settings)
    bpy.types.Scene.gl_stack    = bpy.props.CollectionProperty(type=gl_panel_shader_unit)

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
    del bpy.types.Scene.gl_settings
    del bpy.types.Scene.gl_stack
    