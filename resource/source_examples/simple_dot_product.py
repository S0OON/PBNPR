# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
#========================WARNING=================================
#Important!: This file is a template for shader integration.
# the name of this file (shaderNameMe.py) must be changed to the desired shader name when copied.
# MUST BE UNIQUE TO NOT INTERFIER WITH PYTHON MODULES AND OTHER SHADERS IN THE STREAM.
# BE AWARE all python files have the same access to any thing in bpy module, so name collisions may occur.
#========================IMPORTS=================================
import os
import numpy as np
import bpy
import gpu
import mathutils
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type
from bpy_glsl_manager import gpu_types as t
from bpy_glsl_manager.GLSLbase import _get_mesh_data_for_gpu,UBO
#=====================__FILE__ CONSTANTS===========================
BASE_DIR     = os.path.dirname(__file__)
ABS_DIR      = os.path.abspath(__file__)
SHADER_NAME  = os.path.splitext(os.path.basename(ABS_DIR))[0]
V            = os.path.join(BASE_DIR, t.SHADER_V)
F            = os.path.join(BASE_DIR, t.SHADER_F)
DRAW_REGION  = t.SHADER_DRAW_REGION_WINDOW
DRAW_TYPE    = t.SHADER_DRAW_TYPE_POST_VIEW
DRAW_PRIMITIVE_METHOD = t.PRIM_TRIS

#=====================UI EXPOSURE===========================
def bake_toggle(self, context):
    if not self.bake:
        return
    try:
        img = self.target_img
        if not img: return

        W, H   = img.size
        # Access the stream (assuming it was initialized in your manager)
        desc, shader = bpy.gl_stream[SHADER_NAME]
        
        batch  = desc.CALL_BATCH(shader, self)
        offscreen = gpu.types.GPUOffScreen(W, H) 

        with offscreen.bind():
            gpu.state.viewport_set(0, 0, W, H)
            # Clear is recommended in 5.0.1 to avoid artifacts
            fbo = gpu.state.active_framebuffer_get()
            fbo.clear(color=(0.0, 0.0, 0.0, 0.0))
            
            desc.CALL_EXEC(shader, batch, self)
            buffer = fbo.read_color(0, 0, W, H, 4, 0, 'FLOAT')

        buffer.dimensions = W * H * 4 
        img.pixels.foreach_set(buffer) 
        img.update() 
        
        offscreen.free()
    except Exception as e:
        print(f"[SHADER OFFSCREEN BAKING REPORT]: failed at {SHADER_NAME} : Message: {e}")
    self.bake = False
class shader_params(bpy.types.PropertyGroup):
    #Customs
    Colour : bpy.props.FloatVectorProperty(
        name="Color",subtype='COLOR', default=(0.0, 0.0, 0.0, 1.0), min=0.0, max=1.0,
        description="Color to use in the shader", size=4
    ) # pyright: ignore[reportInvalidTypeForm]
    Source: bpy.props.FloatVectorProperty(
        subtype="XYZ",size=3
    ) # pyright: ignore[reportInvalidTypeForm]
    target_obj: bpy.props.PointerProperty(
        name="",
        type=bpy.types.Object,
        description="Pick an object to use its coordinates in the shader"
    ) # pyright: ignore[reportInvalidTypeForm]
    # Sarder params
    bake : bpy.props.BoolProperty(default=False,update=bake_toggle) # pyright: ignore[reportInvalidTypeForm]
    target_img: bpy.props.PointerProperty(
        name="Target Image",
        type=bpy.types.Image
    ) # pyright: ignore[reportInvalidTypeForm]
    expand_sets: bpy.props.BoolProperty(default=True) # pyright: ignore[reportInvalidTypeForm]
    alwyas_on_top: bpy.props.BoolProperty(
        name="Always on Top (X-Ray)", 
        default=False, 
        description="Disable depth testing to see through solids"
    ) # pyright: ignore[reportInvalidTypeForm]
    blend_mode: bpy.props.EnumProperty(
        name="Blend Mode",
        items=[
            (t.BLEND_NONE,      "Opaque",         "Solid object"),
            (t.BLEND_ALPHA,     "Alpha Blend",    "Standard transparency"),
            (t.BLEND_ADD,       "Additive",       "Glowing/Hologram style"),
            (t.BLEND_ADD_ALPHA, "Additive Alpha", "Additive but respects alpha"),
            (t.BLEND_MULTIPLY,  "Multiply",       "Darkening, good for shadows")
        ],
        default=t.BLEND_NONE
    ) # pyright: ignore[reportInvalidTypeForm]
    depth_mode: bpy.props.EnumProperty(
        name="Depth Mode",
        items=[
            (t.DEPTH_NONE,    "None",       "No depth testing, draw on top of everything"),
            (t.DEPTH_ALWAYS,  "Always",     "Draw regardless of depth, but still write to depth buffer"),
            (t.DEPTH_LESS,    "Less",       "Standard: Draw if closer than existing pixels"),
            (t.DEPTH_LEQUAL,  "Less Equal", "Draw if closer or equal (Default)"),
            (t.DEPTH_GREATER, "Greater",    "Draw if further away than existing pixels"),
            (t.DEPTH_GEQUAL,  "Greater Equal","Draw if further or equal")
        ],
        default=t.DEPTH_LEQUAL
    ) # pyright: ignore[reportInvalidTypeForm]
    cull_mode: bpy.props.EnumProperty(
        name="Cull Mode",
        items=[
            (t.CULL_NONE,   "None",   "No culling"),
            (t.CULL_FRONT,  "Front",  "Cull front faces"),
            (t.CULL_BACK,   "Back",   "Cull back faces (Default)")
        ],
        default=t.CULL_BACK
    ) # pyright: ignore[reportInvalidTypeForm]

def specify_ui_in_panel(
        panel : bpy.types.Panel, 
        ui : shader_params
    ):
    box = panel.layout.box()
    col = box.column(align=True)
    # List all of the shader_params items, the ui is also customized

    col.prop(ui, "Colour")
    col.prop(ui, "Source")
    col.prop(ui, "target_obj")
    row = box.row()
    row.prop(ui,"bake",icon='SCENE',text='')
    row.prop(ui,"target_img",icon_only=True)
    col = box.column(align=True)
    col.prop(ui, "expand_sets", 
        icon='TRIA_DOWN' if ui.expand_sets else 'TRIA_RIGHT',
        text="settings"
    )
    if ui.expand_sets:
        col.prop(ui, "alwyas_on_top")
        col.prop(ui, "blend_mode")
        col.prop(ui, "depth_mode")
        col.prop(ui, "cull_mode")
#======================LOCALE SHADER INTERFACE==============================
i_interface = 'i_Interface'
iOUT_N = 'vNormal'
fDota = 'Dota'
#======================COMPILE INTERFACE==============================
def createInfo():
    info = gpu.types.GPUShaderCreateInfo()
#Glob
    info.push_constant(t.VEC4, t.ATTR_COLOR)
    info.push_constant(t.VEC3, t.ATTR_POINT)
    info.push_constant(t.MAT4, t.ATTR_VIEW_MAT)

#vertex
    info.vertex_in(0, t.VEC3, t.ATTR_POS   )
    info.vertex_in(1, t.VEC3, t.ATTR_NORMAL)
    inter = gpu.types.GPUStageInterfaceInfo(i_interface)
    inter.flat(t.VEC3, iOUT_N)
    info.vertex_out(inter)
    
    v = (
        "void main(){"
        
        f"{iOUT_N} = {t.ATTR_NORMAL};"

        f"{t.ATTR_OUT_V} = {t.ATTR_VIEW_MAT} * vec4({t.ATTR_POS},1.0);"
        
        "}"
    )
    info.vertex_source(v)

#Frag
    info.fragment_out(0, t.VEC4, t.ATTR_OUT_FRAG_COLOR)

    info.fragment_source(
        "void main() {"

        f"float {fDota} = dot(normalize({iOUT_N}), normalize({t.ATTR_POINT}));"

        f"fragColor = vec4( {t.ATTR_COLOR}.rgb * {fDota}, {t.ATTR_COLOR}.a );"
        "}"
    )
    
# out
    #with open(F, "r", encoding="utf-8") as f:
    #    frag_src = f.read()
    #with open(V, "r", encoding="utf-8") as f: 
    #    vert_src = f.read()
    return info

#======================FUNCTIONALITY================================
def uniforms_bind(
        shader: gpu.types.GPUShader, 
        ui: shader_params
    ):
    # ================== CONST =====================
    shader.uniform_float(t.ATTR_COLOR,ui.Colour)
    shader.uniform_float(t.ATTR_POINT,ui.Source)

    # ================== UBO_VIEW ===================
    obj  = ui.target_obj
    if not obj: return
    cam  = bpy.context.scene.camera
    if not cam: return
    deps = bpy.context.evaluated_depsgraph_get()
    w,h  = [bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y]

    m_world = np.array(obj.matrix_world.transposed(),                      dtype=np.float32)#.flatten()
    m_view  = np.array(cam.matrix_world.inverted().transposed(),           dtype=np.float32)#.flatten()
    m_proj  = np.array(cam.calc_matrix_camera(deps,x=w,y=h).transposed(),  dtype=np.float32)#.flatten()
    # ===============
    mat = (m_world @ m_view @ m_proj).astype(np.float32) 
    flat = mat.flatten()
    
    shader.uniform_float(t.ATTR_VIEW_MAT, flat)

    return

def batch_make(
        shader: gpu.types.GPUShader, 
        ui: shader_params
    ):
    
    i,P,N = _get_mesh_data_for_gpu(ui.target_obj)
    
    return batch_for_shader(
        shader, DRAW_PRIMITIVE_METHOD, 
        {
            t.ATTR_POS   : P,
            t.ATTR_NORMAL: N
        }
    )

def safe_exec(
        shader: gpu.types.GPUShader, 
        batch: gpu.types.GPUBatch, 
        ui: shader_params
    ):
    gpu.state.blend_set(ui.blend_mode)
    gpu.state.depth_test_set(ui.depth_mode)
    gpu.state.face_culling_set(ui.cull_mode)

    shader.bind()
    uniforms_bind(shader, ui)
    batch.draw(shader)
    
    gpu.state.blend_set(t.BLEND_NONE)
    gpu.state.depth_test_set(t.DEPTH_NONE)
    gpu.state.face_culling_set(t.CULL_NONE)

#=================== 5.0.1 REGISTRATION (CreateInfo) =============================
def register():
    info = createInfo()

    try:
        shader = gpu.shader.create_from_info(info)
    except Exception as e:
        print(f"[ERORR AT COMPILING SHADER FROM INFO] at {SHADER_NAME}: {e}]")
    
    bpy.utils.register_class(shader_params)
        
    return shader

def unregister():
    global UBO_1
    UBO_1 = None # Explicitly release UBO
    bpy.utils.unregister_class(shader_params)

#===========================================================
@dataclass
class ShaderDesc:
    NAME: str
    PATH_VERT: str
    PATH_FRAG: str
    DRAW_REGION: str
    DRAW_TYPE: str
    DRAW_PRIMITIVE_METHOD:str
    CALL_UNI: Callable
    CALL_BATCH: Callable
    CALL_EXEC: Callable
    CALL_REG:Callable
    CALL_UNREG:Callable
    UI: Type
    CALL_UI_SPEC:Callable
DESCRIPTION = ShaderDesc(
    NAME                  = SHADER_NAME,
    PATH_VERT             = V,
    PATH_FRAG             = F,
    DRAW_REGION           = DRAW_REGION, 
    DRAW_TYPE             = DRAW_TYPE, 
    DRAW_PRIMITIVE_METHOD = DRAW_PRIMITIVE_METHOD,
    CALL_UNI              = uniforms_bind,
    CALL_BATCH            = batch_make,
    CALL_EXEC             = safe_exec,
    CALL_REG              = register,
    CALL_UNREG            = unregister,
    UI                    = shader_params,
    CALL_UI_SPEC          = specify_ui_in_panel
)