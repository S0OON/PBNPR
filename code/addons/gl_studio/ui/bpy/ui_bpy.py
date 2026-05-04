# This file belongs to S00N's PBNPR Blender Add-on
# all rights reserved (C) 2026 S00N

from typing import cast

import bpy

from gl_studio.ui.pyside6 import main


# ---------------------------------------
ID_OP_EXEC_WINDOW = "wm.gl_open_gl_studio"


# ---------------------------------------
class gl_PT_main_settings(bpy.types.PropertyGroup):
    fps: bpy.props.FloatProperty(
        name="FPS",
        description="Frames per second for PySide6 rendering",
        default=15.0,
        min=12.0,
        max=120.0,
    )  # pyright: ignore[reportInvalidTypeForm]
    is_running: bpy.props.BoolProperty(name="Running State", default=False)  # pyright: ignore[reportInvalidTypeForm]


class gl_OT_dpg(bpy.types.Operator):
    bl_idname = ID_OP_EXEC_WINDOW
    bl_label = "Open Window"
    _timer = None

    def modal(self, context, event):
        settings = cast(gl_PT_main_settings, context.scene.gl_studio_settings)

        if not settings.is_running:
            self.report({"INFO"}, "settings.is_running is False!")
            self.cancel(context)
            return {"FINISHED"}

        if event.type == "TIMER":
            if main.check_state():
                main.process_frame()
            else:
                self.report({"INFO"}, "Timer event isnt 'TIMER', Canceled.")
                self.cancel(context)
                return {"FINISHED"}
        return {"PASS_THROUGH"}

    def execute(self, context):
        settings = cast(gl_PT_main_settings, context.scene.gl_studio_settings)

        if settings.is_running:
            self.report({"INFO"}, "PySide6 is already running")
            return {"CANCELLED"}

        main.register()

        settings.is_running = True

        self._timer = context.window_manager.event_timer_add(
            time_step=1.0 / settings.fps, window=context.window
        )
        context.window_manager.modal_handler_add(self)

        return {"RUNNING_MODAL"}

    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
        settings = cast(gl_PT_main_settings, context.scene.gl_studio_settings)

        settings.is_running = False

        main.unregister()


class gl_PT_main(bpy.types.Panel):
    bl_label = "gl manager"
    bl_idname = "gl_PT_main_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "PBNPR"

    def draw(self, context):
        layout = self.layout
        settings = cast(gl_PT_main_settings, context.scene.gl_studio_settings)

        col = layout.column(align=True)
        col.prop(settings, "fps", slider=True)

        if not settings.is_running:
            col.operator(ID_OP_EXEC_WINDOW, text="Start PySide6", icon="PLAY")
        else:
            # Shutdown button (Toggles the bool which the modal watches)
            col.prop(
                settings, "is_running", text="Running...", icon="QUIT", toggle=True
            )
            col.label(text="DONT CLICK!")


# ---------------------------------------
cls = (gl_PT_main_settings, gl_OT_dpg, gl_PT_main)


def register():
    for cl in cls:
        bpy.utils.register_class(cl)
    bpy.types.Scene.gl_studio_settings = bpy.props.PointerProperty(
        type=gl_PT_main_settings
    )


def unregister():
    del bpy.types.Scene.gl_studio_settings
    for cl in reversed(cls):
        bpy.utils.unregister_class(cl)
    main.unregister()
