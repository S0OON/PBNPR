import bpy


#===========================================================
def register(template):
    # Init streams,
    if not hasattr(bpy,"gl_stream"):
        bpy.gl_stream = {} 
    if not hasattr(bpy,"gl_Hs"):
        bpy.gl_Hs = []

    
    bpy.gl_stream[template.SHADER_NAME] = [template.DESCRIPTION,None]
        