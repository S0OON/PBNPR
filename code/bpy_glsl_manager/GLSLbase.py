# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
import bpy

def assign_shader(py):
    """
    1.Loads to the stream
    2.Calls shader's register()
    """
    try:
        bpy.gl_stream[py.SHADER_NAME] = [
            py.DESCRIPTION,
            py.DESCRIPTION.CALL_REG()
            ]
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