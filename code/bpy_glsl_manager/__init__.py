bl_info = {
    "name": "PBNPR: GLSL Manager",
    "author": "KIJAKER",
    "version": (1, 0),
    "blender": (3, 6, 0),
    "location": "View3D > N-Panel > PBNPR",
    "description": "High-performance GLSL viewport manager and baker",
    "category": "Render",
}

import bpy
import importlib
# List your modules in order of dependency
# (Base logic first, UI last)
from .bpy_gl import GLSLbase
from .bpy_ui import ui_
modules = [
    GLSLbase,
    ui_
]
# XXXX

#============================================================
def register():
    # Handle reloads during development
    # If the addon was already loaded, reload modules to apply code changes
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
