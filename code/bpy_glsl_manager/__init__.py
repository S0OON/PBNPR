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
from .bpy_gl import GLSLbase
from .bpy_ui import ui_
modules = [
    GLSLbase,
    ui_
]

#============================================================
def register():
    # Handle reloads during development 
    if "bpy" in locals():
        for mod in modules:
            importlib.reload(mod)

    from .src_template import template
    GLSLbase.register(template)
    ui_.register()
    
    print("PBNPR: Registered successfully")

def unregister():
    for mod in reversed(modules):
        mod.unregister()

    print("PBNPR: Unregistered")

if __name__ == "__main__":
    register()
