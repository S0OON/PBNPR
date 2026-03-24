import bpy
from gl_studio.ui import dpg_main
# ---------------------------------------
ID_OP_EXEC_WINDOW = "wm.open_gl_studio"

# ---------------------------------------
class OPEN_OT_gl_studio(bpy.types.Operator):
    bl_idname = ID_OP_EXEC_WINDOW
    bl_label = "Open DPG Studio"
    _timer = None
    _FPS = (1/30)

    def modal(self, context, event):
        if event.type == 'TIMER':
            if dpg_main.check_state(): 
                dpg_main.render_a_frame()
            else:
                self.cancel(context)
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        dpg_main.register()
        self._timer = context.window_manager.event_timer_add(self._FPS, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        dpg_main.unregister()
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)

class gl_PT(bpy.types.Panel):
    bl_label = "gl manager"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'PBNPR'

    def draw(self, context):
        layout = self.layout
        row = layout.row(align=True)
        row.operator(ID_OP_EXEC_WINDOW)

# ---------------------------------------
cls = (
   OPEN_OT_gl_studio, 
   gl_PT
)

def register():
    for cl in cls:
        bpy.utils.register_class(cl)

def unregister():
    for cl in cls:
        bpy.utils.unregister_class(cl)
    dpg_main.unregister()