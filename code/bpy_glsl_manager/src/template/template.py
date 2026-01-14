import os
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type

SHADER_NAME = "TEMPLATE"
V = "vert.glsl"
F = "frag.glsl"
BASE_DIR = os.path.dirname(__file__)
# ------------------ ------------------ -----------
#typical changes to:
# these 4 dudes under.

class UI_table(bpy.types.PropertyGroup):
    intensity: bpy.props.FloatProperty(default=1.0)

def uniforms_bind(shader: gpu.types.GPUShader,block:UI_table):
    shader.bind()
    shader.uniform_float("u_f", block.intensity)

def batch_make(shader: gpu.types.GPUShader, drawShape: str = "TRIS"):
    coords = [ 
        (-0.5, -0.5), 
        ( 0.5, -0.5), 
        ( 0.0, 0.5)
        ]
    return batch_for_shader(shader, drawShape, {"pos": coords})

def exec(shader: gpu.types.GPUShader, batch: gpu.types.GPUBatch,block:UI_table):
    #Provided that, shader+batch
    shader.bind()
    uniforms_bind(shader,block)
    batch.draw(shader)

#-------------------------------------

def register():
    with open(Desc.PATH_VERT, "r", encoding="utf-8") as f: vert_src = f.read()
    with open(Desc.PATH_FRAG, "r", encoding="utf-8") as f: frag_src = f.read()
    shader = gpu.types.GPUShader(vert_src, frag_src)
    
    bpy.gl_descs[SHADER_NAME] = [Desc, shader]

def unregister():
    try:
        bpy.types.SpaceView3D.draw_handler_remove(
                bpy.gl_descs[Desc.NAME][2],
                Desc.DRAW_REGION
            )
    except: pass
    try:
        del bpy.gl_descs[Desc.NAME]
    except: pass

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
    UI_DATA: Type
    CALL_REG:Callable
Desc = ShaderDesc(
    NAME=SHADER_NAME,
    PATH_VERT=os.path.join(BASE_DIR, V),
    PATH_FRAG=os.path.join(BASE_DIR, F),
    DRAW_REGION = "WINDOW", 
    DRAW_TYPE = "POST_VIEW", 
    DRAW_PRIMITIVE_METHOD = "TRIS",
    CALL_UNI =uniforms_bind,
    CALL_BATCH =batch_make,
    CALL_EXEC =exec,
    UI_DATA =UI_table,
    CALL_REG=register
)
