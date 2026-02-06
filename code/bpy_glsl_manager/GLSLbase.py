import bpy

def assign_shader(py):
    """
    1.Loads to the stream
    2.Calls shader's register()
    """
    bpy.gl_stream[py.SHADER_NAME]    = [py.DESCRIPTION,None] # Deploy dict[i]
    #Pause
    bpy.gl_stream[py.SHADER_NAME][1] =  py.DESCRIPTION.CALL_REG() # Deploy compiled obj + reg_class
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