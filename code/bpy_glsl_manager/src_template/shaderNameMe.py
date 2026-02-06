# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
import os
import bpy
import gpu
import struct
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type
#========================WARNING=================================
#Important!: This file is a template for shader integration.
# the name of this file (shaderNameMe.py) must be changed to the desired shader name when copied.
# MUST BE UNIQUE TO NOT INTERFIER WITH PYTHON MODULES AND OTHER SHADERS IN THE STREAM.
# BE AWARE all python files have the same access to any thing in bpy module, so name collisions may occur.
#=====================__FILE__ CONSTANTS===========================
BASE_DIR     = os.path.dirname(__file__)
ABS_DIR      = os.path.abspath(__file__)
SHADER_NAME  = os.path.splitext(os.path.basename(ABS_DIR))[0]
V            = os.path.join(BASE_DIR, "vert.glsl")
F            = os.path.join(BASE_DIR, "frag.glsl")
DRAW_REGION  = "WINDOW"
DRAW_TYPE    = "POST_VIEW"
DRAW_PRIMITIVE_METHOD = "TRIS"

#======================LOCALE OBJECTS==============================
UBO_1 = None

#========================FUNCTIONALITY===============================
def toggle(self, context):
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

class shader_params(bpy.types.PropertyGroup):
    target_img: bpy.props.PointerProperty(
        name="Target Image",
        type=bpy.types.Image,
        update=toggle
    )
    intensity: bpy.props.FloatProperty(name="Intensity", default=1.0)

def uniforms_bind(shader: gpu.types.GPUShader, block: shader_params):
    """Binds data using std140 alignment required by 5.0.1"""
    # 16-byte alignment (4 floats)
    Data = struct.pack('ffff', block.intensity, 0.2, 0.5, 0.7)
    
    global UBO_1
    if UBO_1 is None:
        UBO_1 = gpu.types.GPUUniformBuf(data=Data)
    else:
        UBO_1.update(Data)

    shader.bind()
    # Name must match the uniform_buf name in CreateInfo
    shader.uniform_block("u_params", UBO_1)

def batch_make(shader: gpu.types.GPUShader, block: shader_params):
    coords = [(-0.5, -0.5), (0.5, -0.5), (0.0, 0.5)]
    # Attribute name 'pos' must be registered in CreateInfo
    return batch_for_shader(shader, DRAW_PRIMITIVE_METHOD, {"pos": coords})

def safe_exec(shader: gpu.types.GPUShader, batch: gpu.types.GPUBatch, block: shader_params):
    if not shader or not batch: return
    try:
        shader.bind()
        uniforms_bind(shader, block)
        batch.draw(shader)
    except Exception as e:
        print(f": Drawing Error in: {e}")

#=================== 5.0.1 REGISTRATION (CreateInfo) =============================
def register():
    # 1. Initialize CreateInfo
    info = gpu.types.GPUShaderCreateInfo()
    
    # 2. Declare Interface (Vulkan/Metal requirement)
    info.vertex_in(0, 'VEC3', "pos")
    
    # Register fragment output (Location, Type, Name)
    info.fragment_out(0, 'VEC4', "fragCol")
    
    # Register UBO (Slot, TypeName, InstanceName)
    # std140 struct definition
    info.typedef_source("struct MyParams { float u_intensity; float u_R; float u_G; float u_B; };")
    info.uniform_buf(0, "MyParams", "u_params")
    
    # 3. Load Clean Source (No manual declarations in strings)
    with open(V, "r", encoding="utf-8") as f: 
        vert_src = f.read()
    with open(F, "r", encoding="utf-8") as f:
        frag_src = f.read()
    
    info.vertex_source(vert_src)
    info.fragment_source(frag_src)
    
    # 4. Compile via the new API
    shader = gpu.shader.create_from_info(info)
    
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
    UI                    = shader_params
)