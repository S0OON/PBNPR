# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2026 S00N
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
from .gl      import modrenGL_lib   as mgl
from .gl      import shader_pattren as mgl_pt
from .gl.util import util_types     as t
from .bpy_ui  import ui
#============================================================
def register():
    if "bpy" in locals():
        importlib.reload(mgl)
        importlib.reload(mgl_pt)
        importlib.reload(t)
        importlib.reload(ui)
    ui.register()

def unregister():
    return

if __name__ == "__main__":
    register()
