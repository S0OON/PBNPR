# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
import bpy,gpu
import numpy as np
from bpy_glsl_manager import gpu_types as t
# ============================================================
class UBO:
    """Helper class to manage UBO data and buffer, consist of Name,type_name, buffer_object"""
    def __init__(self, name,type_name):
        self.name      = name
        self.type_name = type_name
        self.buf       = None

def _get_mesh_data_for_gpu(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj  = obj.evaluated_get(depsgraph)
    mesh      = eval_obj.to_mesh()
    mesh.calc_loop_triangles()
    
    tris_count = len(mesh.loop_triangles)
    
    # 1. Get the Loop Indices (The specific corners of every triangle)
    loops_indices = np.empty((tris_count * 3), dtype=np.int32)
    mesh.loop_triangles.foreach_get("loops", loops_indices)

    # 2. Get Vertex Indices (Which vertex does each corner point to?)
    vertex_indices = np.empty((tris_count * 3), dtype=np.int32)
    mesh.loop_triangles.foreach_get(t.bl_verts, vertex_indices)

    # --- A. Collect Positions ---
    # Get all unique positions, then map them to our triangle corners
    all_pos = np.empty((len(mesh.vertices), 3), dtype=np.float32)
    mesh.vertices.foreach_get(t.bl_Co, all_pos.reshape(-1))
    
    # Create the final flat array of positions (3 for every triangle)
    final_pos = all_pos[vertex_indices]

    # --- B. Collect Normals ---
    # Get normals from LOOPS (This preserves Sharp Edges and Custom Split Normals, like bleeding)
    all_normals = np.empty((len(mesh.loops), 3), dtype=np.float32)
    mesh.loops.foreach_get(t.bl_normal, all_normals.reshape(-1))
    
    # final flat array of normals
    final_normals = all_normals[loops_indices]

    eval_obj.to_mesh_clear() # Clean up (safe in 4.0/5.0 context depending on usage)
    
    return None, final_pos, final_normals

def assign_shader(py):
    """
    1.Loads to the stream
    2.Calls shader's register()

    returns the stream
    """
    try:
        bpy.gl_stream[py.SHADER_NAME] = [
            py.DESCRIPTION,
            py.DESCRIPTION.CALL_REG()
        ]
        
        return bpy.gl_stream[py.SHADER_NAME]
    
    except Exception as e:
        print(f"[SHADER ASSIGNING TO STREAM/reg REPORT]: at [{py.SHADER_NAME}]: '{e}'")
#===========================================================
def register():
    # Init streams,
    if not hasattr(bpy,"gl_stream"):
        bpy.gl_stream = {} 

#===========================================================
def unregister():
    for i,h in enumerate(bpy.gl_Hs):
        if h != None: 
            try:
                bpy.types.SpaceView3D.draw_handler_remove(h,'WINDOW')
            except Exception as e: 
                print(f"[GLSL HANDLER UNREGESTRATION REPORT] at [{i}]: '{e}'")

    for pair in bpy.gl_stream.values():
        if pair != None: 
            try:
                pair[0].CALL_UNREG()
            except Exception as e: 
                print(f"[GLSL SHADER UNREGESTRATION REPORT]: [{pair[0].NAME}]: '{e}'")

    del bpy.gl_stream
    del bpy.gl_Hs