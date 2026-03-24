import dearpygui.dearpygui as dpg
from gl_studio.ui import dpg_internals
from gl_studio.ui import dpg_node_editor

def register():
    if not dpg_node_editor.dpg_internals.cfg.been_registererd:
        dpg_node_editor.dpg_internals.INIT()
        dpg_node_editor.dpg_internals.THEME()
        dpg_node_editor.dpg_internals.WIN_CREATE()
        dpg_node_editor.dpg_internals.VIEWPORT()
        dpg_node_editor.register()
    dpg_node_editor.dpg_internals.cfg.been_registererd = True

def unregister():
      dpg_node_editor.unregister()
      dpg_internals.SHUTDOWN()

def check_state():
    return dpg.is_dearpygui_running()

def render_a_frame():
    dpg.render_dearpygui_frame()
    if dpg_node_editor.pag:
        try: 
            dpg_node_editor.pag.start()
        except Exception as e:
            print(f"Dag error: {e}")
    dpg_node_editor.on_after_frame_callbacks()

