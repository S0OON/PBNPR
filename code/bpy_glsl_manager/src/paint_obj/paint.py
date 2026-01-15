import os
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type
import numpy as np
from mathutils import Matrix

BASE_DIR = os.path.dirname(__file__)
SHADER_NAME = "PAINT_OBJ_SHADER"
V = "vert.glsl"
F = "frag.glsl"
DRAW_REGION = "WINDOW"
DRAW_TYPE = "POST_VIEW"
DRAW_PRIMITIVE_METHOD = "TRIS"
# ------------------ ------------------ -----------
#typical changes to:
# these 4 dudes under.

class UI_table(bpy.types.PropertyGroup):
    cam_name: bpy.props.StringProperty(default="Camera")
    obj_name: bpy.props.StringProperty(default="PaintObject")
    Point_name: bpy.props.StringProperty(default="Point")
    color: bpy.props.FloatVectorProperty( 
        name="Color", 
        subtype='COLOR', 
        size=4, min=0.0, max=1.0, 
        default=(0.2, 0.6, 1.0, 1.0) 
        ) 
    

def uniforms_bind(shader: gpu.types.GPUShader, block):
    shader.bind()
    # Use the depsgraph from the viewport context passed to the handler if available
    dep = bpy.context.evaluated_depsgraph_get() 
    obj = bpy.data.objects[block.obj_name]
    obj_eval = obj.evaluated_get(dep)
    cam = bpy.data.objects[block.cam_name]

    matObj = obj_eval.matrix_world
    matCam = cam.matrix_world.inverted()

    # Projection Matrix logic
    if cam and cam.type == 'CAMERA':
        width  = bpy.context.region.width if bpy.context.region else 1.0
        height = bpy.context.region.height if bpy.context.region else 1.0
        proj   = cam.calc_matrix_camera(dep, x=width, y=height)
    else:
        proj = Matrix.Identity(4)

    shader.uniform_float("uModel", matObj)
    shader.uniform_float("uView",  matCam)
    shader.uniform_float("uProj",  proj)
    
    obj_eval.to_mesh_clear()
    #PointLight-----------------------------------------------------------------
    shader.uniform_float("uLight", bpy.data.lights[block.Point_name].energy)
    shader.uniform_float("uLightPos", bpy.data.objects[block.Point_name].location)
    #col -----------------------------------------------------------------------
    x = [block.color[0], block.color[1], block.color[2]]
    shader.uniform_float("uColor", x)

def batch_make(shader, block, drawShape:str="TRIS"):
    if block.obj_name not in bpy.data.objects:
        # Fallback 2D Triangle
        coords = np.array([
                (-0.5, -0.5, 0.0), 
                (0.5, -0.5, 0.0), 
                (0.0, 0.5, 0.0)], 
                dtype=np.float32
            )
        return batch_for_shader(shader, drawShape, {"pos": coords})
    
    deps = bpy.context.evaluated_depsgraph_get()
    obj = bpy.data.objects[block.obj_name]
    obj_eval = obj.evaluated_get(deps)
    mesh = obj_eval.to_mesh()
    mesh.calc_loop_triangles()

    # Get Vertices
    vertices = np.empty((len(mesh.vertices), 3), 'f')
    mesh.vertices.foreach_get("co", vertices.reshape(-1))

    # Get Triangle Indices (Crucial for a Cube)
    indices = np.empty((len(mesh.loop_triangles), 3), 'i')
    mesh.loop_triangles.foreach_get("vertices", indices.reshape(-1))

    obj_eval.to_mesh_clear()
    
    # Pass both pos and indices to the batch
    return batch_for_shader(shader, drawShape, {"pos": vertices}, indices=indices)

def exec(shader: gpu.types.GPUShader, batch: gpu.types.GPUBatch,block):
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
    DRAW_REGION = DRAW_REGION, 
    DRAW_TYPE = DRAW_TYPE, 
    DRAW_PRIMITIVE_METHOD = DRAW_PRIMITIVE_METHOD,
    CALL_UNI =uniforms_bind,
    CALL_BATCH =batch_make,
    CALL_EXEC =exec,
    UI_DATA =UI_table,
    CALL_REG=register
)
