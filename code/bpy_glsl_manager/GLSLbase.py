import bpy
from .src_template import template as GL_T
def assign_shader(shader_py):
    """
    1.Loads to the stream
    2.Calls shader's register()
    """
    bpy.gl_stream[shader_py.SHADER_NAME]    = [shader_py.DESCRIPTION,None]
    bpy.gl_stream[shader_py.SHADER_NAME][1] =  shader_py.DESCRIPTION.CALL_REG()
#===========================================================
def register():
    # Init streams,
    if not hasattr(bpy,"gl_stream"):
        bpy.gl_stream = {} 
    if not hasattr(bpy,"gl_Hs"):
        bpy.gl_Hs = []
    assign_shader(GL_T)

#===========================================================
def unregister():
    for h in bpy.gl_Hs:
        if h != None: 
            try:
                bpy.types.SpaceView3D.draw_handler_remove(h,'WINDOW')
            except: 
                pass
        
    for pair in bpy.gl_stream:
        if pair != None: 
            try:
                pair[0].CALL_UNREG()
            except Exception as e: 
                print(f"[GLSL SHADER UNREGESTRATION REPORT]: failed to remove shader [{pair[0].NAME}]: {e}")

    del bpy.gl_stream
    del bpy.gl_Hs