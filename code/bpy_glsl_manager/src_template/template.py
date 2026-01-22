import os
import bpy
import gpu
import struct
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type

BASE_DIR = os.path.dirname(__file__)
SHADER_NAME = "TEMPLATE"
V = "vert.glsl"
F = "frag.glsl"
DRAW_REGION = "WINDOW"
DRAW_TYPE = "POST_VIEW"
DRAW_PRIMITIVE_METHOD = "TRIS"
#===========================================================
UBO_1 = None
#===========================================================
def toggle(self,context):
    img = bpy.data.images.get(self.image)
    if not img: return

    W, H = img.size
    pair = bpy.gl_stream[SHADER_NAME]
    desc = pair[0]
    shader = pair[1]
    batch = desc.CALL_BATCH(shader,self)
    offscreen = gpu.types.GPUOffScreen(W, H) 
 
    with offscreen.bind():
        gpu.state.viewport_set(0, 0, W, H)
        desc.CALL_EXEC(shader,batch,self)
        buffer = gpu.state.active_framebuffer_get().read_color(0, 0, W, H, 4, 0, 'FLOAT')

    buffer.dimensions = W * H * 4 
    img.pixels.foreach_set(buffer) 
    img.update() 
    
    offscreen.free() 
class shader_params(bpy.types.PropertyGroup):
    image : bpy.props.StringProperty(default="GLSL_layer",update=toggle) #Bake on update the name
    intensity: bpy.props.FloatProperty(default=1.0)


import gpu
import struct

def uniforms_bind(
        shader: gpu.types.GPUShader,
        block:  shader_params
):
    #For simples:
    # shader.bind()
    # shader.uniform_float('name',float)
    # . . .
    # return

    #For complex performance depending thingies we bundle data:     
    #'f' is a 4-byte float. We add padding to reach 16 bytes for std140 alignment.
    Data = struct.pack('ffff', block.intensity, 0.2, 0.5, 0.7)
    
    # Uniform Buffer Object (UBO) 
    global UBO_1
    UBO_1 = gpu.types.GPUUniformBuf(data=Data)# aka bundled data
    
    shader.bind()
    shader.uniform_block("MyShaderParams", UBO_1)

def batch_make(
        shader: gpu.types.GPUShader,
        block:  shader_params
):
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
    if not shader or not batch:
        return
        
    try:
        shader.bind()
        uniforms_bind(shader,block)
        batch.draw(shader)
    except Exception as e:
        # If it fails once, we stop drawing it to prevent a loop of errors
        print(f"Drawing Error in {shader}: {e}")
        # Option: context.scene.gl_stack[active_index].enabled = False
#===========================================================
def compile_n_register():
    """
    Compiles a shader, saves tp bpy.gl_stream[1] after refreshing the whole key-value
    """
    #Getter
    pair = bpy.gl_stream.get(SHADER_NAME)
    if pair is None:
        print(f"gl_stream, SHDAER: {SHADER_NAME} FAILED TO COMPILE DUE ABSENCE OF gl_Stream key (None)\n")
        return
    if pair[1] is not None:
        print(f"gl_stream: SHADER {SHADER_NAME} Stopped compiliation due presance on another object at gl_stream[{SHADER_NAME}][1]")
        return #already compiled
    Desc = pair[0]

    #Compile
    with open(Desc.PATH_VERT, "r", encoding="utf-8") as f: 
        vert_src = f.read()
    with open(Desc.PATH_FRAG, "r", encoding="utf-8") as f:
        frag_src = f.read()
    shader = gpu.types.GPUShader(vert_src, frag_src)
    
    #Assign
    pair[1] = shader

    return shader

def unregister():
    bpy.gl_descs.pop(SHADER_NAME)

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
    PARAMS: Type
    CALL_REG:Callable
    CALL_UNREG:Callable
DESCRIPTION = ShaderDesc(
    NAME                  = SHADER_NAME,
    PATH_VERT             = os.path.join(BASE_DIR, V),
    PATH_FRAG             = os.path.join(BASE_DIR, F),
    DRAW_REGION           = DRAW_REGION, 
    DRAW_TYPE             = DRAW_TYPE, 
    DRAW_PRIMITIVE_METHOD = DRAW_PRIMITIVE_METHOD,
    CALL_UNI              = uniforms_bind,
    CALL_BATCH            = batch_make,
    CALL_EXEC             = safe_exec,
    PARAMS                = shader_params,
    CALL_REG              = compile_n_register,
    CALL_UNREG            = unregister
)
