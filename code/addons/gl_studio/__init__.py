# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2026 S00N

bl_info = {
    "name": "PBNPR: GL studio",
    "author": "S00N",
    "version": (0, 5),
    "blender": (5, 0, 1),
    "location": "View3D > N-Panel > PBNPR",
    "description": "PySide6 framework for better Rapid Prototyping",
    "category": "Render",
}
from .ui.bpy import ui_bpy

def register():
    ui_bpy.register()

def unregister():
    ui_bpy.unregister()
