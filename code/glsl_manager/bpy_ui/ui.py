# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2026 S00N

import bpy
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
import importlib.util
import shutil
import sys
import os 
from glsl_manager.gl.example import gl_shader_template as GLSL_DEFAULT
#------------------------------------------------------------- 
PT_OP_ADD_MOD = 'gl.mod_add_shader_py'
PT_OP_EXPORT  = 'gl.mod_export'
ID_OP_REMOVE  = "gl.remove_shader_type_instance"
ID_OP_RENDER_STILL = 'gl.render_still_shader'
shaders ={}

def safe_import_mod(filepath):
    """
    Dynamically imports a Python file into Blender.
    Ensures the module is reloaded fresh for debugging.
    """
    try:
        mod_path = os.path.abspath(filepath)  # 1. Get Absolute Path and Name
        mod_name = os.path.basename(os.path.splitext(filepath)[0])
        
        if mod_name in sys.modules:  # 2. FORCE RELOAD
            del sys.modules[mod_name]

        spec = importlib.util.spec_from_file_location(mod_name, mod_path)  # 3. Create the Spec

        if spec is None or spec.loader is None:
            print('ERROR', f"Import Failed at spec checker: invalid spec or loader for {mod_name}")
            return None

        ext_mod = importlib.util.module_from_spec(spec)  # 4. Load and Execute
        sys.modules[mod_name] = ext_mod  # register in system
    
        try:
            spec.loader.exec_module(ext_mod)
        except Exception as e:
            if mod_name in sys.modules:
                del sys.modules[mod_name]
            print(f"Import Failed during module execution, report: {e}")
            return None
        return ext_mod
    
    except Exception as e:
        print('ERROR', f"Import Failed at absolute, report: {e}")
        return None

class gl_shader_unit_instance(bpy.types.PropertyGroup):
    shader_type : bpy.props.StringProperty(default='NULL')  # pyright: ignore[reportInvalidTypeForm]
    Enable : bpy.props.BoolProperty(default=False)  # pyright: ignore[reportInvalidTypeForm]
    Expand : bpy.props.BoolProperty(default=False)  # pyright: ignore[reportInvalidTypeForm]

def _get_available_shaders_add(self,context):
    items = [("Select", "Add a shader...", "")]
    for key in shaders.keys():
        items.append((key, key, ""))
    return items
def _get_available_shaders_remove(self,context):
    items = [("Select", "Remove a shader type...", "")]
    for key in shaders.keys():
        items.append((key, key, ""))
    return items

def tog_shType_add(self, context):
    target = self.selected_type_add 
    if target == "Select": 
        return
    STACK = bpy.context.scene.gl_Shader_units_stack

    new_i = STACK.add()
    new_i.shader_type = target

    target = "Select" 

def tog_shType_remove(self, context):
    target = self.selected_type_remove
    if target == "Select": 
        return
    # Clear the target relatives
    STACK = bpy.context.scene.gl_Shader_units_stack
    for i,j in enumerate(STACK):
        if j.shader_type == target:
            j.Enable = False
            STACK.remove(i)
    delattr(
        gl_shader_unit_instance,target)
    # remove shader type key in gl_stream
    shaders.pop(target)
    if target in sys.modules:
        del sys.modules[target]
    target = "Select"

# -------------------------------------------------------
class gl_PT_Header_settings(bpy.types.PropertyGroup):
    selected_type_add: bpy.props.EnumProperty(
        update=tog_shType_add, 
        items =_get_available_shaders_add
    ) # pyright: ignore[reportInvalidTypeForm]
    selected_type_remove: bpy.props.EnumProperty(
        update=tog_shType_remove, 
        items=_get_available_shaders_remove
    ) # pyright: ignore[reportInvalidTypeForm]

class gl_OP_Export_templateMOD(bpy.types.Operator, ExportHelper): # Use ExportHelper for folders
    bl_idname    = PT_OP_EXPORT
    bl_label     = "Create New Shader Project"
    filename_ext = "" 
    directory:   bpy.props.StringProperty(subtype='DIR_PATH') # pyright: ignore[reportInvalidTypeForm]

    def invoke(self, context, event):
        # We force the file selector to open
        # For folders, we ensure the directory property is used
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        template_src = os.path.dirname(GLSL_DEFAULT.__file__)
        target_dir   = os.path.join(self.directory, "new_shader")
        try:
            shutil.copytree(template_src, target_dir)
            self.report({'INFO'}, f"Template created: {target_dir}")
        except Exception as e:
            self.report({'ERROR'}, f"Export Failed, report: {str(e)}")
        return {'FINISHED'}

class gl_OP_import_shaderMOD(bpy.types.Operator, ImportHelper):
    bl_idname = PT_OP_ADD_MOD
    bl_label = "Load Shader Script"

    filter_glob: bpy.props.StringProperty(default="*.py", options={'HIDDEN'}) # pyright: ignore[reportInvalidTypeForm]
    def invoke(self, context, event):
        # This ensures the window pops up even if called from a script
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

    def execute(self, context):
        ext_mod = safe_import_mod(self.filepath)
        if ext_mod:
            mod_name = os.path.basename(os.path.splitext(ext_mod.__file__)[0])
            cl_ui = ext_mod.DESCRIPTION.UI
            bpy.utils.register_class(cl_ui)
            setattr(gl_shader_unit_instance,mod_name,
                    bpy.props.PointerProperty(type=cl_ui))
            shaders[mod_name]=ext_mod
            return {'FINISHED'}

        self.report({'ERROR'}, "Import failed, ext_mod is None, Check Console.")
        return {'CANCELLED'}

class gl_OP_Remove_stack_index(bpy.types.Operator):
    bl_idname = ID_OP_REMOVE
    bl_label = ""
    index_i : bpy.props.IntProperty(default=-1) # pyright: ignore[reportInvalidTypeForm]
    
    def execute(self, context):
        STACK = bpy.context.scene.gl_Shader_units_stack
        if self.index_i < len(STACK):
            STACK[self.index_i].enabled = False # Triggers toggle() to remove handler
            STACK.remove(self.index_i)
        return {'FINISHED'}

#----------------------------------------------
class gl_PT(bpy.types.Panel): 
    bl_label       = "GLSL Manager"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'PBNPR'

    def draw(self, context):
        layout   = self.layout
        STACK    = context.scene.gl_Shader_units_stack
        SETTINGS = context.scene.gl_PT_header_settings

        box = layout.box()

        row = box.row(align=True)
        row.scale_y=2.0
        j=row.operator(PT_OP_EXPORT,icon='NEWFOLDER') # Header Type operators
        i=row.operator(PT_OP_ADD_MOD,icon='FILE_NEW')
        row = box.row(align=True)
        row.prop(SETTINGS,'selected_type_remove',text='')
        row = box.row(align=True)
        row.prop(SETTINGS,'selected_type_add',text='')

        for i,j in enumerate(STACK):
            #j=gl_shader_unit_instance
            box = layout.box()
            row = box.row(align=True)
            
            row.prop(j, "Expand", 
                icon='TRIA_DOWN' if j.Expand else 'TRIA_RIGHT',
                icon_only=True)
            
            row.label(text=j.shader_type, icon='SHADING_RENDERED')

            row.prop(j, "Enable", text="")
            
            op         = row.operator(ID_OP_REMOVE, text="", icon='X')
            op.index_i = i 

            if j.Expand:
                j_ui = getattr(j, j.shader_type)
                if j_ui is None:
                    print(f'ERROR NONE UI CLASS IN DRAW() shader_type={j.shader_type}')
                    return
                j_ui.draw_self_to_panel_canvas(box)

#----------------------------------------------
css = (
    gl_shader_unit_instance,
    gl_PT_Header_settings,
    gl_OP_Export_templateMOD,
    gl_OP_import_shaderMOD,
    gl_OP_Remove_stack_index,
    gl_PT
)
def register():
    for cl in css:
        bpy.utils.register_class(cl)
    bpy.types.Scene.gl_Shader_units_stack = bpy.props.CollectionProperty(type=gl_shader_unit_instance)
    bpy.types.Scene.gl_PT_header_settings = bpy.props.PointerProperty(type=gl_PT_Header_settings) 
