# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2024 S00N
bl_info = {
    "name": "PBNPR: GLSL Manager",
    "author": "S00N",
    "version": (1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > N-Panel > PBNPR",
    "description": "High-performance GLSL viewport manager and baker",
    "category": "Render",
}

import importlib
from . import GLSLbase
from . import ui_
from . import gpu_types as t
#============================================================
def register():
    # Handle reloads during development 
    if "bpy" in locals():
        importlib.reload(t)
        importlib.reload(GLSLbase)
        importlib.reload(ui_)

    GLSLbase.register()
    ui_.register()

def unregister():
    ui_.unregister()
    GLSLbase.unregister()

if __name__ == "__main__":
    register()
