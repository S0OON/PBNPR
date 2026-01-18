import os
import bpy
import gpu
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
# ------------------ ------------------ -----------

class shader_params(bpy.types.PropertyGroup):
    intensity: bpy.props.FloatProperty(default=1.0)

def uniforms_bind(
        shader: gpu.types.GPUShader,
        block:shader_params
    ):
    shader.bind()
    shader.uniform_float("u_f", block.intensity)

def batch_make(
        shader: gpu.types.GPUShader,
        block:shader_params, 
        drawShape: str = DRAW_PRIMITIVE_METHOD
    ):
    coords = [ 
        (-0.5, -0.5), 
        ( 0.5, -0.5), 
        ( 0.0, 0.5)
        ]
    return batch_for_shader(shader, drawShape, {"pos": coords})

def exec(
        shader: gpu.types.GPUShader,
        batch: gpu.types.GPUBatch,
        block:shader_params
    ):
    #Provided that, shader+batch
    shader.bind()
    uniforms_bind(shader,block)
    batch.draw(shader)

#-------------------------------------

def compile_n_register():
    """
    Compiles a shader, saves tp bpy.gl_stream[1] after refreshing the whole key-value
    """
    stream = bpy.gl_stream[SHADER_NAME]
    if stream[1] is not None:
        return #already compiled
    Desc = stream[0]

    with open(Desc.PATH_VERT, "r", encoding="utf-8") as f: 
        vert_src = f.read()
    with open(Desc.PATH_FRAG, "r", encoding="utf-8") as f:
        frag_src = f.read()
    shader = gpu.types.GPUShader(vert_src, frag_src)
    
    bpy.gl_stream[SHADER_NAME][1] = shader

def unregister():
    bpy.gl_descs.pop(SHADER_NAME)

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
    NAME                  =SHADER_NAME,
    PATH_VERT             =os.path.join(BASE_DIR, V),
    PATH_FRAG             =os.path.join(BASE_DIR, F),
    DRAW_REGION           = DRAW_REGION, 
    DRAW_TYPE             = DRAW_TYPE, 
    DRAW_PRIMITIVE_METHOD = DRAW_PRIMITIVE_METHOD,
    CALL_UNI              =uniforms_bind,
    CALL_BATCH            =batch_make,
    CALL_EXEC             =exec,
    PARAMS                =shader_params,
    CALL_REG              =compile_n_register,
    CALL_UNREG            =unregister
)
