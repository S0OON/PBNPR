import dearpygui.dearpygui as dpg
import shutil
import os,sys
import importlib
from importlib.util import spec_from_file_location,module_from_spec
from dataclasses import dataclass
from typing import cast


# ---------------------------------------
@dataclass
class DPG_INTERFACE:
    win_label='gl studio'
    win_tag  = 'main_nodes_window'
    win_size = [800,600]
    win_node_miniMap = False
    node_editor_tag = "node_editor_main"
    nodes_dirs_menu = "node_editor_nodes_dirs_menu"
    nodes_types_menu= "node_editor_nodes_add_menu"
    add_dir_btn = "Add_directory_button_id"
    update_dirs_btn = "update_dirs_btn_ID"
    dirs  = {}
    module_registry = {}
    active_links = {}  # format = { in_id : out_id }
    calls_post_frame={}# {ID : call}

    def link_callback(sender, app_data):
        OUT, IN = app_data

        dpg.add_node_link(OUT, IN, parent=sender)
        
        cfg.active_links[IN] = OUT

    def delink_callback(self,sender, app_data):
        #app_data = link_id being deleted
        link_id = app_data

        OUT = dpg.get_item_user_data(link_id)

        if OUT in cfg.active_links:
            del cfg.active_links[OUT]

        dpg.delete_item(link_id)

cfg = DPG_INTERFACE()

# ---------------------------------------
def _START():
    dpg.create_context()

def _THEME():
    with dpg.theme() as global_theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, (30, 30, 30))
            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
    dpg.bind_theme(global_theme)

def on_dpg_close():
    dpg.stop_dearpygui()

def on_node_types_reLoad():
    global cfg
    for j in cfg.dirs.values():
        if not os.path.isdir(j):
            continue
            
        for filename in os.listdir(j):
            filename=cast(str,filename)
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = filename[:-3]
                file_path = os.path.join(j, filename)
                
                spec = spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = module_from_spec(spec)
                    spec.loader.exec_module(module)
                    try:
                        CFG = getattr(module,'cfg')
                        if not CFG: return
                        
                        dpg.add_menu_item(label   =CFG.label,
                                          callback=CFG.BUILD,
                                          parent=cfg.nodes_types_menu)
                        
                        cfg.calls_post_frame[CFG.ID]=CFG.AFTER_DRAW_CALL

                        cfg.module_registry[module_name] = module
                    except Exception as e: 
                        print(f"FAILED TO IMPORT {module_name}, EXCEPTION: {e}")

def on_directory_change(sender,app_data):
    cfg.dirs[sender]=dpg.get_value(sender)

def on_add_directory():
    dpg.add_input_text(label="Directory",parent=cfg.nodes_dirs_menu,callback=on_directory_change)

def _WIN():
    W,H = cfg.win_size
    with dpg.window(label=cfg.win_label, 
                     tag=cfg.win_tag, 
                     width=W, height=H, on_close=on_dpg_close):
        
        with dpg.menu_bar():

            with dpg.menu(label="Nodes stream",tag=cfg.nodes_dirs_menu):
                dpg.add_button(label="Update node types from directories",callback=on_node_types_reLoad,tag=cfg.update_dirs_btn)
                dpg.add_button(label="Add directory",callback=on_add_directory,tag=cfg.add_dir_btn)

            with dpg.menu(label="Add Node",tag=cfg.nodes_types_menu):pass
        
        with dpg.node_editor(
                tag=cfg.node_editor_tag,
                callback=cfg.link_callback,        # Called when link created
                delink_callback=cfg.delink_callback, # Called when link deleted
                minimap=cfg.win_node_miniMap,
                minimap_location=dpg.mvNodeMiniMap_Location_BottomRight):pass

def _VIEWPORT():
    W,H = cfg.win_size
    dpg.create_viewport(title='GLSL Studio', width=W, height=H)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.set_primary_window(cfg.win_tag, True)

def register():
    _START()
    _THEME()
    _WIN()
    _VIEWPORT()
    base_path = os.path.dirname(__file__)
    nodes_path = os.path.abspath(os.path.join(base_path, "..", "examples", "nodes"))
    cfg.dirs["DEFAULT"] = nodes_path
    on_node_types_reLoad()
    print(cfg.dirs.items())

def unregister():
    dpg.destroy_context()
    DPG_INTERFACE.nodes.clear()
    DPG_INTERFACE.links.clear()

def evaluate_chains(id_in):
    Out = cfg.active_links[id_in]

if __name__ == "__main__":
    register()
    while True:
        dpg.render_dearpygui_frame()
        for i,j in cfg.calls_post_frame.items():
            j()
            evaluate_chains(i)


#+=========================================================================
