# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
import bpy
import numpy as np
from bpy_glsl_manager import gpu_types as t

def _get_mesh_data_for_gpu(obj):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj  = obj.evaluated_get(depsgraph)
    mesh      = eval_obj.to_mesh()
    mesh.calc_loop_triangles()
    
    # --- A. Collect Indices ---
    loop_tri_count = len(mesh.loop_triangles)
    indices        = np.empty((loop_tri_count, 3), dtype=np.int32)
    mesh.loop_triangles.foreach_get(t.bl_verts, indices.reshape(-1))

    # --- B. Collect Positions ---
    v_count = len(mesh.vertices)
    pos     = np.empty((v_count, 3), dtype=np.float32)
    mesh.vertices.foreach_get(t.bl_Co, pos.reshape(-1))

    # --- C. Collect Normals ---
    normals = np.empty((v_count, 3), dtype=np.float32)
    mesh.vertices.foreach_get(t.bl_normal, normals.reshape(-1))

    eval_obj.to_mesh_clear()# Clean up
    
    return indices,pos, normals

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
        # now print the 'module' or .py in console to confirm registration
        print(f"[SHADER REGISTRATION REPORT]: '{py.SHADER_NAME}' assigned.")

        return bpy.gl_stream[py.SHADER_NAME]
    
    except Exception as e:
        print(f"[SHADER ASSIGNING TO STREAM/reg REPORT]: at [{py.SHADER_NAME}]: '{e}'")
#===========================================================
def register():
    # Init streams,
    if not hasattr(bpy,"gl_stream"):
        bpy.gl_stream = {} 
    if not hasattr(bpy,"gl_Hs"):
        bpy.gl_Hs = []

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