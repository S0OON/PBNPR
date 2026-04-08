import dearpygui.dearpygui as dpg
import os,importlib
from importlib.util import spec_from_file_location,module_from_spec
from typing import cast

from gl_studio.ui import dpg_internals
from gl_studio.examples.nodes import Node_zPattren as Node_template
from gl_studio.util import util_types as t

# ---------------------------------------
class NODE_EDITOR_INTERFACE:
    """nodes = {node_id:node_obj}"""
    win_label='Node editor'
    
    def INIT(self):
        self.win_tag          = dpg_internals.cfg.win_main_id
        self.editor_tag       = dpg.generate_uuid()
        self.editor_menuDirs  = dpg.generate_uuid()
        self.editor_menuTypes = dpg.generate_uuid()
        self.editor_map       = False
        self.editor_map_loc   = dpg.mvNodeMiniMap_Location_BottomRight
    
    dirs  = {}
    module_registry = {}
    nodes = {}        
    active_links = {}  # { Input_socket_id : Output_socket_id }
   
    def delete_selected_nodes(self):
        """Delete all currently selected nodes in the editor."""
        # get
        selected = dpg.get_selected_nodes(self.editor_tag)
        # delete
        for node_id in list(selected):
            self._delete_node(node_id)
        # clear
        dpg.clear_selected_nodes(self.editor_tag)
    
    def _delete_node(self, node_id):
        """
        Safely delete a node and all its connected links.
        Must delete links BEFORE deleting the node to avoid errors.
        """
# 1. Find all links connected to this node
        links_to_delete = []
        for input_id, output_id in list(self.active_links.items()):
            parent_i = dpg.get_item_parent(input_id)
            parent_o = dpg.get_item_parent(output_id)
            
            if parent_i == node_id or parent_o == node_id:
                links_to_delete.append((input_id, output_id))
        
# 2. Delete all connected links first (CRITICAL: before deleting node)
        for input_id, output_id in links_to_delete:
            if input_id in self.active_links:
                del self.active_links[input_id]
            
            # Find and delete the actual DPG link item
            self._delete_link_by_attributes(input_id, output_id)
        
        # 3. Now safe to delete the node
        if dpg.does_item_exist(node_id):
            dpg.delete_item(node_id)
        
        # 4. Remove from our nodes dict
        if node_id in self.nodes:
            del self.nodes[node_id]

    def _delete_link_by_attributes(self, input_id, output_id):
        """Find and delete a DPG link item by its connected attribute IDs."""
        if not dpg.does_item_exist(self.editor_tag):
            return
        
        children = dpg.get_item_children(self.editor_tag)
        if not children:
            return
        
        # Links are in slot 1 of the node editor children
        link_items = children[1] if len(children) > 1 else []
        
        for link_id in link_items:
            try:
                link_info = dpg.get_item_user_data(link_id)
                if link_info:
                    out_id, in_id = link_info
                    if out_id == output_id and in_id == input_id:
                        dpg.delete_item(link_id)
                        return
            except Exception:
                continue

cfg = NODE_EDITOR_INTERFACE()

class node_helper:
    def node_from_socket(self,socket_id):
        return cast(Node_template.NODE_INTERFACE,
                    dpg.get_item_parent(socket_id))
    
    def node_connected_to_input(self,input_socket_id):
        """ID of the node that is connected to an input"""
        output = cfg.active_links.get(input_socket_id)
        return self.node_from_socket(output)

nh = node_helper()

#===============
Node = Node_template.NODE_BASE_INTERFACE
Pin  = t.NodeSocket
class ThemeManager:
    pass
#==============
class PAG:
    def __init__(self):
        self.queue = []
        self.visited = set()
        self.exec_order = []
        self.active_ui_links = set()

    def Clear(self):
        self.queue.clear()
        self.visited.clear()
        self.exec_order.clear()
        self.active_ui_links.clear()

    def run(self): 
        for node_id, node_obj in cfg.nodes.items(): 
            n = cast(Node, node_obj)

            if n.SHOULD_CRAWL_CB():
                self.Clear()
                self.order(n)
                self.execs_order()
                self._reset_nodes()
               
                #TODO self.animate_active_graph()

    def order(self, terminal_node_branch_obj):
        n = cast(Node, terminal_node_branch_obj)

        if not n or n.ID in self.visited: return 
        self.visited.add(n.ID)
        
        if hasattr(n, 'inputs'): 
            for i in n.inputs:   # i/o = input_id/ouptput_id 
                o = cfg.active_links.get(i)
                if o:
                    adj_node_id = dpg.get_item_parent(o)
                    adj_node = cfg.nodes.get(adj_node_id)
                    self.order(adj_node)
        
        self.exec_order.append(n)

    def execs_order(self):
        for node in self.exec_order:
            node = cast(Node, node)
            
            if hasattr(node, 'inputs'):
                self._propagate_inputs(node)
            
            if not node.CACHE:
                node.EXEC_ON_CRAWLER_CB()# Execute the node after inputs's-checkings

    def _propagate_inputs(self, node: Node):
        """
            Copy values from connected output pins to input pins if types match.
        """
        for input_pin_id, input_socket in node.inputs.items():
            # IN
            input_pin = cast(Pin, input_socket)
            
            # OUT
            # Find the connected output pin
            output_pin_id = cfg.active_links.get(input_pin_id)
            if not output_pin_id:
                continue
            
            # Get the sender node and its output pin
            sender_node = cfg.nodes.get(dpg.get_item_parent(output_pin_id))
            if not sender_node or not hasattr(sender_node, 'outputs'):
                continue
            
            output_socket = sender_node.outputs.get(output_pin_id)
            if not output_socket:
                continue
            
            output_pin = cast(Pin, output_socket)
            
            # CLONE at match types
            if (input_pin.data_type == output_pin.data_type or input_pin.data_type.lower() == 'any'):
                input_pin.value = output_pin.value

    def _reset_nodes(self):
        for node in cfg.nodes.values():
            node = cast(Node, node)
            node.CACHE = False

pag = PAG()
# ---------------------------------------
def Node_initlizer(node_interface):
    def node_creation(sender, app_data,user_data):
        node_obj = cast(Node,node_interface(parent=cfg.editor_tag))
        #CFG <- INTERFACE
        cfg.nodes[node_obj.ID] = node_obj
        #UI <- INTERACE
        node_obj.EXEC_GUI_CB()
        #RETURN FACTORY
    return node_creation

def on_node_types_reload():
    #UI - FORMAT 'ADD NODE'
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
                    # CFG <- MODULE
                    if module in cfg.module_registry.values():
                        importlib.reload(module)
                        continue
                    try:
                        cfg.module_registry[module_name] = module
                        # UI <- INTERFACE            
                        node_interface = getattr(module,'NODE_INTERFACE')
                        if not node_interface: return

                        dpg.add_menu_item(label=node_interface.LABEL,
                                          callback=Node_initlizer(node_interface),
                                          parent=cfg.editor_menuTypes) # Adds 'add ABC' item to 'add node' menu
                    except Exception as e: 
                        print(f"FAILED TO IMPORT {module_name}, EXCEPTION: {e}")

def on_directory_change(sender,app_data):
    cfg.dirs[sender]=dpg.get_value(sender)

def on_add_directory():
    dpg.add_input_text(label="Directory",parent=cfg.editor_menuDirs,callback=on_directory_change)

def on_after_frame_callbacks():
    for node in cfg.nodes.values():
        node.EXEC_ON_LOOP_CB()

# In dpg_node_editor.py
def link_callback(sender, app_data):
    out_id, in_id = app_data
    #CFG
    cfg.active_links[in_id] = out_id
    #UI - ID=(O,I)
    link_id = dpg.add_node_link(out_id, in_id, parent=sender, 
                                user_data=(
                                    out_id, 
                                    in_id))

def delink_callback(sender, app_data):
    link_id = app_data
    link_info = dpg.get_item_user_data(link_id)
    # CFG
    if link_info:
        out_id, in_id = link_info        
        cfg.active_links.pop(in_id, None)
    #UI
    dpg.delete_item(link_id)

def register():
    cfg.INIT()
    
    with dpg.handler_registry():
        dpg.add_key_down_handler(key=dpg.mvKey_Delete, callback=lambda s,a,u: cfg.delete_selected_nodes())

    with dpg.menu_bar(parent=cfg.win_tag):
            with dpg.menu(label="Nodes stream"):
                dpg.add_button(label="Update node types from directories",
                               callback=on_node_types_reload)
                dpg.add_button(label="Add directory",
                               callback=on_add_directory)
            
            with dpg.menu(label="Add Node",tag=cfg.editor_menuTypes):
                pass

    with dpg.node_editor(tag=cfg.editor_tag,
                         parent=cfg.win_tag,
                         callback=link_callback,          # Called when link created
                         delink_callback=delink_callback, # Called when link deleted
                         minimap=cfg.editor_map,
                         minimap_location=cfg.editor_map_loc): pass
    
    base_path  = os.path.dirname(__file__)
    nodes_path = os.path.abspath(os.path.join(base_path, "..", "examples", "nodes"))
    cfg.dirs["DEFAULT"] = nodes_path
    on_node_types_reload()

def run():
    try: 
        pag.run()
    except Exception as e: 
        print(f"Pag error: {e}")
    on_after_frame_callbacks()

def unregister():
    global cfg
    del cfg