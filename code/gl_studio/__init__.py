# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2026 S00N
bl_info = {
    "name": "PBNPR: GL studio",
    "author": "S00N",
    "version": (1, 0),
    "blender": (5, 0, 1),
    "location": "View3D > N-Panel > PBNPR",
    "description": "High-performance GLSL viewport manager and baker",
    "category"   : "Render",
}

# ============================================================
if __name__ == '__main__':
    from .ui import dpg_ui
    dpg_ui.register()

