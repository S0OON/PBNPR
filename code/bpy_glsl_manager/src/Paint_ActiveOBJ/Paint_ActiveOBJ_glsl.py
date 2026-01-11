import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import numpy as np 

from dataclasses import dataclass
from typing import Callable, Type


# This is the "Blueprint" for one modifier block
class ShaderBlock(bpy.types.PropertyGroup):
    # 1. Which shader logic to use? (Points to your 'Shader_desc')
    shader_type: bpy.props.EnumProperty(
            name="Type",
            items=[
                ('PAINT', "Paint Shader", ""),
                ('SIMPLE', "Simple Circle", ""),
            ]
        ) 
    is_enabled: bpy.props.BoolProperty(name="Active", default=True)

# ------------------

def uniforms(shader: gpu.types.GPUShader):
    shader.bind()
    
    # Use evaluated data for accuracy if modifiers are present
    depsgraph = bpy.context.evaluated_depsgraph_get()
    scene = bpy.context.scene
    
    obj = bpy.context.active_object
    cam = scene.camera

    if not obj or not cam: return

    # Matrix World of the object (Model Matrix)
    obj_mat = obj.matrix_world
    
    # Inverted Camera Matrix (View Matrix)
    cam_m = cam.matrix_world.inverted()

    # Projection Matrix
    proj = cam.calc_matrix_camera(
        depsgraph,
        x=scene.render.resolution_x,
        y=scene.render.resolution_y
    )

    # Pass them to the shader
    shader.uniform_float("u_objM", obj_mat)
    shader.uniform_float("u_camM", cam_m)
    shader.uniform_float("u_projM", proj)

def batch(shader: gpu.types.GPUShader): 
    obj = bpy.context.active_object
    axies = 3
    
    if not obj or obj.type != 'MESH':
        # Fallback to a single triangle if the Cube is missing
        coords = [(0, 0, 0), (1, 0, 0), (0, 1, 0)]
        return batch_for_shader(shader, 'TRIS', {"pos": coords})
  
    mesh = obj.data 
    
    vertices = np.zeros(len(mesh.vertices)*axies,dtype=np.float32) 

    mesh.vertices.foreach_get("co",vertices) 
    return batch_for_shader(shader, 'TRIS', {"pos": vertices})

def batch_draw(shader:gpu.types.GPUShader,batch: gpu.types.GPUBatch):
    shader.bind()
    uniforms(shader)
    batch.draw(shader)

# -----------------------------

@dataclass
class ShaderDesc:
    NAME: str
    PATH_VERT: str
    PATH_FRAG: str
    CALL_UNI: Callable
    CALL_BATCH: Callable
    CALL_DRAW: Callable
    UI_DATA: Type

Desc = ShaderDesc (
    NAME="Paint_ActiveOBJ",
    PATH_VERT  = r"D:/soon/projects/06_pythonShaders/code/src/Default/Default_vert.glsl",
    PATH_FRAG  = r"D:/soon/projects/06_pythonShaders/code/src/Default/Default_frag.glsl",
    CALL_UNI   = uniforms,
    CALL_BATCH = batch,
    CALL_DRAW  = batch_draw,
    UI_DATA    = ShaderBlock,
)
