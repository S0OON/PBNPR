import bpy,sys
from gl_studio.ui.ui_window import GLStudioWindow,QtWidgets,global_studio_window,global_qt_app

OP_EXEC_WINDOW = "wm.open_gl_studio"
# =========================================

class OPEN_OT_gl_studio(bpy.types.Operator):
    """The Blender Operator that launches the UI"""
    bl_idname = OP_EXEC_WINDOW
    bl_label = "Open GL Studio"

    _timer = None

    def modal(self, context, event):
        global global_qt_app, global_studio_window
        
        if event.type == 'TIMER':
            if global_qt_app:
                global_qt_app.processEvents()
                
            if global_studio_window and not global_studio_window.isVisible(): # if hidden/closed, stop the timer
                self.cancel(context)
                return {'CANCELLED'}
                
        return {'PASS_THROUGH'}

    def execute(self, context):
        global global_qt_app, global_studio_window
        
        global_qt_app = QtWidgets.QApplication.instance()
        if not global_qt_app:
            global_qt_app = QtWidgets.QApplication(sys.argv)
            
        if global_studio_window is None:
            global_studio_window = GLStudioWindow()
            
        global_studio_window.show()
        
        self._timer = context.window_manager.event_timer_add(0.01, window=context.window)
        context.window_manager.modal_handler_add(self)
        
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        print("Window WIdget Operator had called Cancel.")

class gl_PT(bpy.types.Panel): 
    bl_label       = "GLSL Manager"
    bl_space_type  = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category    = 'PBNPR'

    def draw(self, context):
        layout   = self.layout
        row = layout.row(align=True)
        row.operator(OP_EXEC_WINDOW)

cls = (
    OPEN_OT_gl_studio,
    gl_PT,
)

def register():
    for cl in cls:
        bpy.utils.register_class(cl)
