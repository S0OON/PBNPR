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
    """nodes = {node_id:node_obj}"""
    win_label='Node editor'
    
    def INIT(self):
        self.win_tag  = dpg_internals.cfg.win_main_id
        self.editor_tag = dpg.generate_uuid()
        self.editor_menuDirs = dpg.generate_uuid()
        self.editor_menuTypes= dpg.generate_uuid()
        self.editor_map = False
        self.editor_map_loc = dpg.mvNodeMiniMap_Location_BottomRight
    
    dirs  = {}
    module_registry = {}
    nodes = {}        
    active_links = {}  # link_id : (in , out)

cfg = DPG_INTERFACE()

class node_helper:
    def node_from_socket(self,socket_id):
        return cast(Node_template.NODE_INTERFACE,
                    dpg.get_item_parent(socket_id))
    
    def node_adjacnet_from_input(self,input_socket_id):
        """ID of the node that is connected to an input"""
        output = cfg.active_links.get(input_socket_id)
        return cast(Node_template.NODE_INTERFACE, 
                    self.node_from_socket(output))


nh = node_helper()

class PAG:
    """Pull-based Access Graph - WITH DATA FLOW"""
    queue   = []
    visited = []
    sorted_matrix=[] # [int] = [Output_id,input,input...etc]

    def reset(self):
        self.queue.clear()
        self.visited.clear()
        self.sorted_matrix.clear()

    def start(self): 
        for node_id, node_obj in cfg.nodes.items(): 
            node_obj = cast(Node_template.NODE_INTERFACE, node_obj)
            if node_obj.SHOULD_CRAWL_CB():
                self.reset()
                self.order(node_obj)
                self.execs()

    def order(self, node_obj):
        # recursion guard 
        if not node_obj or node_obj.ID in self.visited: 
            return 
        self.visited.append(node_obj.ID)
        
        obj_curnt = cast(Node_template.NODE_INTERFACE, node_obj)
        links_for_this_node = []

        if hasattr(obj_curnt, 'inputs'):
            for input_pin_id in obj_curnt.inputs:
                outer_pin_id = cfg.active_links.get(input_pin_id)
                if outer_pin_id:
                    links_for_this_node.append([outer_pin_id, input_pin_id])
                    adj_node_id = dpg.get_item_parent(outer_pin_id)
                    self.order(cfg.nodes.get(adj_node_id))

        if links_for_this_node:
            self.sorted_matrix.append(links_for_this_node)


    def execs(self):
        for link_group in self.sorted_matrix:
            # link_group is a list of [output_id, input_id] 
            for o_pin, i_pin in link_group:
                sender_node = cfg.nodes.get(dpg.get_item_parent(o_pin))
                receiver_node = cfg.nodes.get(dpg.get_item_parent(i_pin))
                
                if not sender_node or not receiver_node: continue

                crawl_results = sender_node.EXEC_ON_CRAWLER_CB() 

                send_pin_dict = sender_node.outputs.get(o_pin)
                rec_pin_dict = receiver_node.inputs.get(i_pin)

                if send_pin_dict and rec_pin_dict:
                    # 3. Transfer the value if types match (or 'any')
                    if rec_pin_dict['type'] == send_pin_dict['type'] or rec_pin_dict['type'] == 'any':
                        rec_pin_dict['value'] = send_pin_dict['value']

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
    link_id = dpg.add_node_link(out_id, in_id, parent=sender, user_data=(out_id, in_id))
    cfg.active_links[in_id] = out_id

def delink_callback(sender, app_data):
    link_id = app_data
    link_info = dpg.get_item_user_data(link_id)
    
    if link_info:
        out_id, in_id = link_info
        cfg.active_links.pop(in_id, None)


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
