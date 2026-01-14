import bpy
import importlib


#-----------------------------------------------------
from src.template import template as GLSL_TEMP

libs = [GLSL_TEMP]

def reload_shaders():
    if not hasattr(bpy, "gl_descs"):
        bpy.gl_descs = {}

    bpy.gl_descs.clear()
    
    for i in libs:
        importlib.reload(i)
        i.register()
        
        
