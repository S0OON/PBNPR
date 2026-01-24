import os
import bpy
import gpu
import struct
from gpu_extras.batch import batch_for_shader
from dataclasses import dataclass
from typing import Callable, Type
import numpy as np
#===========================================================
BASE_DIR = os.path.dirname(__file__)
SHADER_NAME = "Cross"
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
 
    # 
    with offscreen.bind():
        gpu.state.viewport_set(0, 0, W, H)
        
        # THE FIX: Clear the color AND the depth buffer!
        fbo = gpu.state.active_framebuffer_get()
        fbo.clear(color=(0.0, 0.0, 0.0, 0.0), depth=1.0) 
        
        desc.CALL_EXEC(shader,batch,self)
        buffer = gpu.state.active_framebuffer_get().read_color(0, 0, W, H, 4, 0, 'FLOAT')

    buffer.dimensions = W * H * 4 
    img.pixels.foreach_set(buffer) 
    img.update() 
    
    offscreen.free() 
class shader_params(bpy.types.PropertyGroup):
    image : bpy.props.StringProperty(default="GLSL_layer",update=toggle) #Bake on update the name
    Object_name:bpy.props.StringProperty(default="Cube")
    color : bpy.props.FloatVectorProperty(
        subtype='COLOR',
        size=4, min=0.0, max=1.0, 
        default=(0.2, 0.6, 1.0, 1.0) 
        )
    vector: bpy.props.FloatVectorProperty(
        subtype="XYZ",size=4
    )

def uniforms_bind(
        shader: gpu.types.GPUShader,
        block:  shader_params
):
    cam  = bpy.context.scene.camera
    obj  = bpy.data.objects[block.Object_name]
    deps = bpy.context.evaluated_depsgraph_get()
    w,h  = [bpy.context.scene.render.resolution_x,bpy.context.scene.render.resolution_y]
    
    m_world = np.array(obj.matrix_world.transposed(),                     dtype=np.float32).flatten()
    m_view  = np.array(cam.matrix_world.inverted().transposed(),          dtype=np.float32).flatten()
    m_proj  = np.array(cam.calc_matrix_camera(deps,x=w,y=h).transposed(), dtype=np.float32).flatten()
    u_col   = np.array(block.color,       dtype=np.float32).flatten() 
    u_point = np.array(block.vector,      dtype=np.float32).flatten() 
    # =======================================

    # =======================================
    Data = np.concatenate([m_world, m_view, m_proj, u_col, u_point])
    # =======================================
    
    global UBO_1
    if UBO_1 is None:
        UBO_1 = gpu.types.GPUUniformBuf(data=Data)
    else:
        UBO_1.update(Data)

    shader.bind()
    shader.uniform_block("MyShaderParams", UBO_1)

def batch_make(
        shader: gpu.types.GPUShader,
        block:  shader_params
):
    deps = bpy.context.evaluated_depsgraph_get()
    obj = bpy.data.objects[block.Object_name]
    obj_eval = obj.evaluated_get(deps)
    mesh = obj_eval.to_mesh()
    mesh.calc_loop_triangles()

    # Get Vertices
    vertices = np.empty((len(mesh.vertices), 3), dtype=np.float32)
    mesh.vertices.foreach_get("co", vertices.reshape(-1))

    # Get Triangle Indices
    indices = np.empty((len(mesh.loop_triangles), 3), 'i')
    mesh.loop_triangles.foreach_get("vertices", indices.reshape(-1))

    # Get Normals
    normals = np.empty((len(mesh.vertices), 3), dtype=np.float32)
    mesh.vertices.foreach_get("normal", normals.reshape(-1))

    obj_eval.to_mesh_clear()
    
    # Pass both pos and indices to the batch
    return batch_for_shader(shader, DRAW_PRIMITIVE_METHOD, 
                            {"pos": vertices,
                             "normal":normals}, 
        indices=indices
    )

def safe_exec(
        shader: gpu.types.GPUShader,
        batch:  gpu.types.GPUBatch,
        block:  shader_params
):
    if not shader or not batch:
        return
        
    try:
        shader.bind()
        uniforms_bind(shader, block)

        # THE FIX: Tell the GPU to respect the Z-axis
        gpu.state.depth_test_set('LESS_EQUAL')
        gpu.state.depth_mask_set(True) 
        
        batch.draw(shader)
        
        # Reset to Blender's default to avoid UI glitches
        gpu.state.depth_mask_set(False)
    except Exception as e:
        print(f"Drawing Error: {e}")

#===========================================================
def compile_n_register():
    """
    Compiles a shader, saves to bpy.gl_stream[1] after refreshing the whole key-value
    """
    #Getter
    pair = bpy.gl_stream.get(SHADER_NAME)
    if pair is None:
        print(f"gl_stream, SHDAER: {SHADER_NAME} FAILED TO COMPILE DUE ABSENCE OF gl_Stream key (None)\n")
        return
    #if pair[1] is not None:
    #    print(f"gl_stream: SHADER {SHADER_NAME} Stopped compiliation due presance on another object at gl_stream[{SHADER_NAME}][1]")
    #    return #already compiled
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
    global UBO_1
    if UBO_1 is not None:
        del UBO_1 
    bpy.gl_stream.pop(SHADER_NAME)

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
