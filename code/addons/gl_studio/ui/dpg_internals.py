import dearpygui.dearpygui as dpg
from dataclasses import dataclass

class DPG_INTERFACE:
    been_registererd = False
    win_label = "gl studio"
    win_size = (800,600)
    def INIT(self):    
        self.win_main_id = dpg.generate_uuid()
        self.win1_id = dpg.generate_uuid() # used bpy dpg_node_editor.py
        self.win2_id = dpg.generate_uuid() # future debugger

cfg = DPG_INTERFACE()



def INIT():
    dpg.create_context()
    cfg.INIT()

def SHUTDOWN():
    cfg.been_registererd = False
    dpg.stop_dearpygui()
    dpg.destroy_context()

def THEME():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
    dpg.bind_theme(global_theme)
    
def WIN_close(sender,app_data):pass

def WIN_MAIN_CLOSE(sender,app_data):
    SHUTDOWN()

def WIN_CREATE():
    W,H = cfg.win_size
    with dpg.window(tag=cfg.win_main_id,on_close=WIN_close):pass
    #with dpg.window(tag=cfg.win1_id,on_close=WIN_close):pass
    #with dpg.window(tag=cfg.win2_id,on_close=WIN_close):pass

def VIEWPORT():
    W,H = cfg.win_size
    dpg.create_viewport(title=cfg.win_label, width=W, height=H)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window(cfg.win_main_id, True)
