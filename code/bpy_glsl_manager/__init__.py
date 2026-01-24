bl_info = {
    "name": "PBNPR: GLSL Manager",
    "author": "S00N",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N-Panel > PBNPR",
    "description": "High-performance GLSL viewport manager and baker",
    "category": "Render",
}

import importlib
from . import GLSLbase
from . import ui_
from .src_template import template as GL_TEMPLATE
modules = [
    GL_TEMPLATE,
    GLSLbase,
    ui_
] 

#============================================================
def register():
    # Handle reloads during development 
    if "bpy" in locals():
        for mod in modules:
            importlib.reload(mod)

    GLSLbase.register()
    ui_.register()
    
    print("PBNPR: Registered successfully")

def unregister():
    ui_.unregister()
    GLSLbase.unregister()

    print("PBNPR: Unregistered")

if __name__ == "__main__":
    register()
