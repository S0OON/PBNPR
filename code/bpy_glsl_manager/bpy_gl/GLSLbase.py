import bpy


#===========================================================
def register(template):
    # Init streams,
    if not hasattr(bpy,"gl_stream"):
        bpy.gl_stream = {} 
    if not hasattr(bpy,"gl_Hs"):
        bpy.gl_Hs = []

    bpy.gl_stream[template.SHADER_NAME] = [template.DESCRIPTION,None]

def unregister():
    try:
        for h in bpy.gl_Hs:
            if h == None: 
                continue
            else:
                bpy.types.SpaceView3D.draw_handler_remove(
                    h,'WINDOW'
                )
    except: pass

    del bpy.gl_stream
    del bpy.gl_Hs