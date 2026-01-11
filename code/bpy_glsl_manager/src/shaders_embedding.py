# WILL be added bpy.gl dict.
# keys are 'descs' *sub KEYS from each shader.py
# 'GPUobj','ui_classes'
import bpy
import importlib


def Reload(): 
    import Default.Default_glsl as GLSL_DEF
    import Paint_ActiveOBJ.Paint_ActiveOBJ_glsl as GLSL_PAINT
    libs = [GLSL_DEF,GLSL_PAINT]
    for mod in libs:
        try:
            importlib.reload(mod)
        except Exception as e:
            print(f"Failed reloading {mod}: {e}")
    
    bpy.gl_descs = {
        GLSL_DEF.Desc.NAME:GLSL_DEF.Desc,
        GLSL_PAINT.Desc.NAME:GLSL_PAINT.Desc
    }
        
