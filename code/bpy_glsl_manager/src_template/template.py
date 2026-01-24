import os
import bpy
import gpu
import struct
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type

#===========================================================
BASE_DIR              = os.path.dirname(__file__)
SHADER_NAME           = os.path.basename(BASE_DIR)
V                     = os.path.join(BASE_DIR,"vert.glsl")
F                     = os.path.join(BASE_DIR,"frag.glsl")
DRAW_REGION           = "WINDOW"
DRAW_TYPE             = "POST_VIEW"
DRAW_PRIMITIVE_METHOD = "TRIS"
#===========================================================
UBO_1 = None
#===========================================================
def toggle(self,context):
    try:
        img = self.target_img

        W, H   = img.size
        pair   = bpy.gl_stream[SHADER_NAME]
        desc   = pair[0]
        shader = pair[1]
        batch  = desc.CALL_BATCH(shader,self)
        offscreen = gpu.types.GPUOffScreen(W, H) 

        with offscreen.bind():
            gpu.state.viewport_set(0, 0, W, H)
            desc.CALL_EXEC(shader,batch,self)
            buffer = gpu.state.active_framebuffer_get().read_color(0, 0, W, H, 4, 0, 'FLOAT')

        buffer.dimensions = W * H * 4 
        img.pixels.foreach_set(buffer) 
        img.update() 
        
        offscreen.free() 
    except Exception as e:
        print(f"[IMG BACKING REPORT]: failed at {SHADER_NAME}: {e}")
class shader_params(bpy.types.PropertyGroup):
    target_img: bpy.props.PointerProperty(
        name="",
        type=bpy.types.Image,
        update=toggle
    )
    intensity: bpy.props.FloatProperty(default=1.0)

def uniforms_bind(
        shader: gpu.types.GPUShader,
        block:  shader_params
):
    """Binds data to the shader"""
    #For simples:
    # shader.bind()
    # shader.uniform_float('name',float)
    # . . .
    # return

    #For complex performance depending thingies we bundle data:     
    #'f' is a 4-byte float. We add padding to reach 16 bytes for std140 alignment.
    Data = struct.pack('ffff', # map
                       block.intensity, 0.2, 0.5, 0.7 #data
    )
    
    # Uniform Buffer Object (UBO) 
    global UBO_1
    if UBO_1 is None:
        UBO_1 = gpu.types.GPUUniformBuf(data=Data)# aka bundled data
    else:
        UBO_1.update(Data)

    shader.bind()
    shader.uniform_block("MyShaderParams", UBO_1)

def batch_make(
        shader: gpu.types.GPUShader,
        block:  shader_params
):
    """Uniform but for mesh data"""
    coords = [ 
        (-0.5, -0.5), 
        ( 0.5, -0.5), 
        ( 0.0, 0.5)
    ]
    return batch_for_shader(shader, DRAW_PRIMITIVE_METHOD, {"pos": coords})

def safe_exec(
        shader: gpu.types.GPUShader,
        batch:  gpu.types.GPUBatch,
        block:  shader_params
):
    """Execute a single drawing shader on screen"""
    try:
        shader.bind()
        uniforms_bind(shader,block)
        batch.draw(shader)
    except Exception as e:
        print(f"[SAFE EXECUTION REPORT]: Drawing Error in [{SHADER_NAME}]: {e}")

#===========================================================
def register():
    """PROVIDED DISCRIPTION in gl_stream"""
    # Compile
    with open(V, "r", encoding="utf-8") as f: 
        vert_src = f.read()
    with open(F, "r", encoding="utf-8") as f:
        frag_src = f.read()
    shader = gpu.types.GPUShader(vert_src, frag_src)
    # Assign
    try:
        bpy.utils.register_class(shader_params)
    except Exception as e:
        print(f"[SHADER [{SHADER_NAME}] CLASS REGISTRATION REPORT]: {e}")
    return shader

def unregister():
    # Locale Data
    global UBO_1
    if UBO_1 is not None:
        UBO_1 = None
    # remove bpy internal
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
