import os
import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type
import numpy as np
from mathutils import Matrix

BASE_DIR = os.path.dirname(__file__)
SHADER_NAME = "PAINT_OBJ"
V = "vert.glsl"
F = "frag.glsl"
DRAW_REGION = "WINDOW"
DRAW_TYPE = "POST_VIEW"
DRAW_PRIMITIVE_METHOD = "TRIS"
# ------------------ ------------------ ----------- 
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
    cam_name: bpy.props.StringProperty(default="Camera")
    obj_name: bpy.props.StringProperty(default="Cube")
    Point_name: bpy.props.StringProperty(default="Point")
    color: bpy.props.FloatVectorProperty( 
        name="Color", 
        subtype='COLOR', 
        size=4, min=0.0, max=1.0, 
        default=(0.2, 0.6, 1.0, 1.0) 
        ) 
    image : bpy.props.StringProperty(default="GLSL_layer",update=toggle)

def uniforms_bind(
        shader: gpu.types.GPUShader,
        block:shader_params
    ):
    shader.bind()

    dep = bpy.context.evaluated_depsgraph_get() 
    obj = bpy.data.objects[block.obj_name]
    obj_eval = obj.evaluated_get(dep)
    cam = bpy.data.objects[block.cam_name]

    matObj = obj_eval.matrix_world
    matCam = cam.matrix_world.inverted()

    # Projection Matrix logic
    width  = bpy.context.region.width if bpy.context.region else 1.0
    height = bpy.context.region.height if bpy.context.region else 1.0
    proj   = cam.calc_matrix_camera(dep, x=width, y=height)

    shader.uniform_float("uModel", matObj)
    shader.uniform_float("uView",  matCam)
    shader.uniform_float("uProj",  proj)
    
    obj_eval.to_mesh_clear()
    #PointLight-----------------------------------------------------------------
    shader.uniform_float("uLight", bpy.data.lights[block.Point_name].energy)
    shader.uniform_float("uLightPos", bpy.data.objects[block.Point_name].location)
    #col -----------------------------------------------------------------------
    x = [block.color[0], block.color[1], block.color[2], block.color[3]]
    shader.uniform_float("uColor", x)
    
def batch_make(
        shader: gpu.types.GPUShader,
        block:shader_params, 
        drawShape: str = DRAW_PRIMITIVE_METHOD
    ):
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
