import dearpygui.dearpygui as dpg
import shutil
import os,sys
import importlib
from importlib.util import spec_from_file_location,module_from_spec
from typing import cast
from collections import defaultdict

from gl_studio.ui import dpg_internals
from gl_studio.examples.nodes import Node_template
# ---------------------------------------
class DPG_INTERFACE:
    win_label='Node editor'
    
    def INIT(self):
        self.win_tag  = dpg_internals.cfg.win1_id
        self.editor_tag = dpg.generate_uuid()
        self.editor_menuDirs = dpg.generate_uuid()
        self.editor_menuTypes= dpg.generate_uuid()
        self.editor_map = False
        self.editor_map_loc = dpg.mvNodeMiniMap_Location_BottomRight
    
    dirs  = {}
    module_registry = {}
    nodes = {}

cfg = DPG_INTERFACE()

class PAG:
    """Pull-based Access Graph"""
    def start(self):
        self.queue = []
        self.visited = set()

        for obj in cfg.nodes.values():
            if obj.SHOULD_CRAWL_CB():
                self.evaluate(obj)

        self.execute_queue()

    def evaluate(self, obj):
        if not obj or obj in self.visited: return
        self.visited.add(obj)
        
        for out_id in obj.PINS['CRAWLERS']:
            node_out = dpg.get_item_parent(out_id)
            obj_out = cfg.nodes.get(node_out)
            self.evaluate(obj_out)

        if obj.SHOULD_EXEC_CB():
            self.queue.append(obj)

    def execute_queue(self):
        self.queue.reverse()
        for obj in self.queue:
            obj.EXEC_ON_CRAWLER_CB()

pag = PAG()
# ---------------------------------------

def on_node_types_reload():
    global cfg
    dpg.delete_item(cfg.editor_menuTypes,children_only=True)
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
                    if module in cfg.module_registry.values():
                        importlib.reload(module)
                        continue
                    try:
                        node_interface = getattr(module,'NODE_INTERFACE')
                        if not node_interface: return
                        
                        def node_creation(sender,app_data):
                            node_obj = cast(Node_template.NODE_INTERFACE,
                                            node_interface(parent=cfg.editor_tag))
                            cfg.nodes[node_obj.ID]=node_obj
                            node_obj.EXEC_GUI_CB()

                        dpg.add_menu_item(label=node_interface.LABEL,
                                          callback=node_creation,
                                          parent=cfg.editor_menuTypes)

                        cfg.module_registry[module_name] = module
                    except Exception as e: 
                        print(f"FAILED TO IMPORT {module_name}, EXCEPTION: {e}")

def on_directory_change(sender,app_data):
    cfg.dirs[sender]=dpg.get_value(sender)

def on_add_directory():
    dpg.add_input_text(label="Directory",parent=cfg.editor_menuDirs,callback=on_directory_change)

def on_after_frame_callbacks():
    for node in cfg.nodes.values():
        node = cast(Node_template.NODE_INTERFACE,node)
        if node.SHOULD_BE_ACTIVE():
            node.EXEC_ON_LOOP_CB()

def link_callback(sender, app_data):
    out_id, in_id = app_data
        
    #input node
    node_in = dpg.get_item_parent(in_id)
    obj_in = cast(Node_template.NODE_INTERFACE,cfg.nodes.get(node_in))
    if not obj_in: return
    #output node
    node_out = dpg.get_item_parent(out_id)
    obj_out = cast(Node_template.NODE_INTERFACE,cfg.nodes.get(node_out))
    if not obj_out: return

    link_id = dpg.add_node_link(out_id, in_id, parent=sender, user_data=(out_id, in_id))
    obj_in.LINKS.add(link_id)
    obj_out.LINKS.add(link_id)

    if in_id == obj_in.CRAWLER:
        obj_in.PINS['CRAWLERS'].add(out_id)

        # Track in your custom config
        #if out_id not in cfg.active_links:
        #    cfg.active_links[out_id] = set()
        #cfg.active_links[out_id].add(in_id)

def delink_callback(sender, app_data):
    link_id = app_data
    link_info = dpg.get_item_user_data(link_id)
    
    if link_info:
        out_id, in_id = link_info
        #input node
        node_in = dpg.get_item_parent(in_id)        
        obj_in = cast(Node_template.NODE_INTERFACE,cfg.nodes.get(node_in))
        if not obj_in: return
        #output node
        node_out = dpg.get_item_parent(out_id)        
        obj_out = cast(Node_template.NODE_INTERFACE,cfg.nodes.get(node_out))
        if not obj_out: return

        obj_in.LINKS.discard(link_id)
        obj_out.LINKS.discard(link_id)

        if in_id == obj_in.CRAWLER:
            obj_in.PINS['CRAWLERS'].discard(out_id)
        
        dpg.delete_item(link_id)
        #if out_id in cfg.active_links:
        #    cfg.active_links[out_id].discard(in_id)
        #    if not cfg.active_links[out_id]:
        #        del cfg.active_links[out_id]

def register():
    cfg.INIT()
    with dpg.menu_bar(parent=cfg.win_tag):
            with dpg.menu(label="Nodes stream"):
                dpg.add_button(label="Update node types from directories",
                               callback=on_node_types_reload)
                dpg.add_button(label="Add directory",
                               callback=on_add_directory)
            
            with dpg.menu(label="Add Node",tag=cfg.editor_menuTypes):
                pass

    with dpg.node_editor(
            tag=cfg.editor_tag,
            parent=cfg.win_tag,
            callback=link_callback,          # Called when link created
            delink_callback=delink_callback, # Called when link deleted
            minimap=cfg.editor_map,
            minimap_location=cfg.editor_map_loc):
        pass
    
    base_path  = os.path.dirname(__file__)
    nodes_path = os.path.abspath(os.path.join(base_path, "..", "examples", "nodes"))
    cfg.dirs["DEFAULT"] = nodes_path
    on_node_types_reload()

def unregister():
    cfg.dirs.clear()
    cfg.module_registry.clear()
    cfg.nodes.clear()
