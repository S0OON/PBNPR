import bpy
import importlib


from src.template import template as GLSL_TEMP
from src.paint_obj import paint as GLSL_PAINTobj
libs = [GLSL_TEMP, GLSL_PAINTobj]
#-----------------------------------------------------
def reload_shaders():
    if not hasattr(bpy, "gl_descs"):
        bpy.gl_descs = {}

    bpy.gl_descs.clear()
    
    for i in libs:
        importlib.reload(i)
        i.register()
        
        
