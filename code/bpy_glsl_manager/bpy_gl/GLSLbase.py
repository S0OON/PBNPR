import bpy

#Hot~
def load_modules()->list:
    from src.template import template as GLSL_TEMP
    from src.paint_obj import paint as GLSL_PAINT_OBJ
    
    return[
        GLSL_TEMP,
        GLSL_PAINT_OBJ
    ]

def init_stream():
    if not hasattr(
            bpy,"gl_stream"
        ):
        bpy.gl_stream = {}

def load_mods_to_stream():
    from importlib import reload
    mods = load_modules()
    for mod in mods:
        reload(mod)
        bpy.gl_stream[mod.SHADER_NAME]=[
            mod.DESCRIPTION,None
        ]

def load_shader(name:str):
    bpy.gl_stream[name][0].CALL_REG()

def register():
    init_stream()
    load_mods_to_stream()