import bpy
from gl_studio.ui import dpg_node_editor
import dearpygui.dearpygui as dpg

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
            if dpg.is_dearpygui_running():
                dpg.render_dearpygui_frame()
                if dpg_node_editor.dag:
                    try: 
                        dpg_node_editor.dag.start()
                        dpg_node_editor.on_after_frame_callbacks()
                    except Exception as e:
                        print(f"Dag error: {e}")
            else:
                self.cancel(context)
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def execute(self, context):
        if not dpg_node_editor.dpg_internals.cfg.been_registererd:
            dpg_node_editor.dpg_internals.INIT()
            dpg_node_editor.dpg_internals.THEME()
            dpg_node_editor.dpg_internals.WIN_CREATE()
            dpg_node_editor.dpg_internals.VIEWPORT()
            dpg_node_editor.register()
        dpg_node_editor.dpg_internals.cfg.been_registererd = True
        
        self._timer = context.window_manager.event_timer_add(self._FPS, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}
    
    def cancel(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
        dpg_node_editor.unregister()

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
    dpg_node_editor.unregister()
    dpg_node_editor.dpg_internals.SHUTDOWN()