# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
import bpy 
from bpy_extras.io_utils import ImportHelper
from bpy_extras.io_utils import ExportHelper
import importlib.util
import shutil
import sys
import os
from .src_template import shaderNameMe as GLSL_DEFAULT

#===========================================================
def _get_streamKeys(self, context):
    items = [("Select", "Select Shader...", "")]
    for key in bpy.gl_stream.keys():
        items.append((key, key, ""))
    return items

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
                custom_params = getattr(INST, f"ptr_{INST.shaderType}", None)
                col = box.column(align=True)
                for prop in custom_params.bl_rna.properties:
                    if not prop.is_readonly: # Skip internal RNA props
                        col.prop(custom_params, prop.identifier)

#====================INSTANCE===============================
def tog_inst_H(self, context):
    if self.enabled and self.handler_id == -1: # Enabled but inActive 
        STACK = bpy.context.scene.gl_stack
        for i,j in enumerate(STACK):
            if self == j: # address level comparision
                self.handler_id = i
                break
        
        while bpy.gl_Hs.__len__() <= self.handler_id: # size checker
            bpy.gl_Hs.append(None)

        pair   = bpy.gl_stream[self.shaderType]
        desc   = pair[0]
        shader = pair[1]
        ui     = getattr(
            self, 
            f"ptr_{self.shaderType}", 
            None
        )
        batch  = desc.CALL_BATCH(shader,ui)

        args = (
            shader,
            batch,
            ui
        )
        handler = bpy.types.SpaceView3D.draw_handler_add(
            desc.CALL_EXEC,   args,
            desc.DRAW_REGION, desc.DRAW_TYPE
        )

        bpy.gl_Hs[self.handler_id]=handler
    
    elif not self.enabled and self.handler_id != -1: # Disabled but active
        pair = bpy.gl_stream[self.shaderType]
        desc = pair[0]

        bpy.types.SpaceView3D.draw_handler_remove(
            bpy.gl_Hs[self.handler_id], 
            desc.DRAW_REGION
        )
        bpy.gl_Hs[self.handler_id] = None
        self.handler_id = -1
class gl_instance_sk(bpy.types.PropertyGroup):
    enabled:     bpy.props.BoolProperty(default=False, update=tog_inst_H)
    expanded:    bpy.props.BoolProperty(default=True)
    shaderType:  bpy.props.StringProperty(default="")
    handler_id : bpy.props.IntProperty(default=-1)

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
    #=====
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

class gl_mainSettings(bpy.types.PropertyGroup):
    selected_type_add: bpy.props.EnumProperty(
        name="", update=tog_shType_add, 
        items =_get_streamKeys
    )
    selected_type_remove: bpy.props.EnumProperty(
        name="", update=tog_shType_remove, 
        items=_get_streamKeys
    )

class gl_OP_remove_instance(bpy.types.Operator):
    bl_idname = ID_OP_REMOVE
    bl_label = ""
    index_i : bpy.props.IntProperty(default=-1)

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
    directory:   bpy.props.StringProperty(subtype='DIR_PATH')

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

    filter_glob: bpy.props.StringProperty(default="*.py", options={'HIDDEN'})

    def execute(self, context):
        ext_mod = safe_import_mod(self.filepath)
        
        if ext_mod:
            from .GLSLbase import assign_shader
            assign_shader(ext_mod)
            
            desc = ext_mod.DESCRIPTION
            
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
    gl_instance_sk,
    gl_OP_remove_instance,
    gl_mainSettings,
    gl_OP_Export_templateMOD,
    gl_OP_import_shaderMOD,
    gl_panel
)

def register():
    for cl in classes: 
        bpy.utils.register_class(cl)
    
    bpy.types.Scene.gl_settings = bpy.props.PointerProperty(type=gl_mainSettings)
    bpy.types.Scene.gl_stack    = bpy.props.CollectionProperty(type=gl_instance_sk)

    from .GLSLbase import assign_shader
    assign_shader(GLSL_DEFAULT)
    py = GLSL_DEFAULT.DESCRIPTION
    if not hasattr(gl_instance_sk, f"ptr_{py.NAME}"):
        setattr(
            gl_instance_sk, f"ptr_{py.NAME}", 
            bpy.props.PointerProperty(type=py.UI)
        )

def unregister():
    for cl in reversed(classes):
        bpy.utils.unregister_class(cl)
    del bpy.types.Scene.gl_settings
    del bpy.types.Scene.gl_stack
    