import dearpygui.dearpygui as dpg
import shutil
import os,sys
import importlib
from importlib.util import spec_from_file_location,module_from_spec
from typing import cast
from collections import defaultdict

from gl_studio.ui import dpg_internals
from gl_studio.examples.nodes import Node_template
from gl_studio.util import util_types as t
import time,math
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

#===============
class ThemeManager:
    active_theme = None
    color_tag = None
    default_theme = None
    
    @classmethod
    def setup(cls):
        # 1. Create the default "inactive" gray theme
        with dpg.theme() as cls.default_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvNodeCol_Link, (150, 150, 150, 255))
                dpg.add_theme_style(dpg.mvNodeStyleVar_LinkThickness, 2.0)

        # 2. Create the "pulsing" theme
        cls.color_tag = dpg.generate_uuid()
        with dpg.theme() as cls.active_theme:
            with dpg.theme_component(dpg.mvAll):
                # We tag this color so we can manipulate it directly in the loop!
                dpg.add_theme_color(dpg.mvNodeCol_Link, (255, 50, 50, 255), tag=cls.color_tag)
                dpg.add_theme_style(dpg.mvNodeStyleVar_LinkThickness, 4.0)
#==============

class PAG:
    def __init__(self):
        self.queue = []
        self.visited = set()
        self.exec_order = []
        self.active_ui_links = set()

    def reset(self):
        self.queue.clear()
        self.visited.clear()
        self.exec_order.clear()
        self.active_ui_links.clear()

    def start(self): 
        for node_id, node_obj in cfg.nodes.items(): 
            node_obj = cast(Node_template.NODE_INTERFACE, node_obj)
            if node_obj.SHOULD_CRAWL_CB():
                self.reset()
                self.order(node_obj)
                self.execs()
                node_obj.EXEC_ON_CRAWLER_CB()
                #self.animate_active_graph()

    def order(self, node_obj):
        if not node_obj or node_obj.ID in self.visited: 
            return 
        self.visited.add(node_obj.ID)
        
        if hasattr(node_obj, 'inputs'):
            for input_pin_id in node_obj.inputs:
                outer_pin_id = cfg.active_links.get(input_pin_id)
                if outer_pin_id:
                    ui_link_uuid = cfg.ui_links.get(input_pin_id) # valid dependency path; Save the UI link.
                    if ui_link_uuid:
                        self.active_ui_links.add(ui_link_uuid)

                    adj_node_id = dpg.get_item_parent(outer_pin_id)
                    adj_node = cfg.nodes.get(adj_node_id)
                    self.order(adj_node)
        
        self.exec_order.append(node_obj)

    def execs(self):
        for node in self.exec_order:
            if hasattr(node, 'inputs'):
                for input_pin_id, in_pin_socket in node.inputs.items():
                    outer_pin_id = cfg.active_links.get(input_pin_id)
                    
                    if outer_pin_id:
                        sender_node = cfg.nodes.get(dpg.get_item_parent(outer_pin_id))
                        if sender_node and hasattr(sender_node, 'outputs'):
                            send_pin_socket = sender_node.outputs.get(outer_pin_id)
                            I = cast(t.NodeSocket,in_pin_socket)
                            O = cast(t.NodeSocket,send_pin_socket)
                            if send_pin_socket:
                                # Clone the value if types match (or 'any')
                                if I.data_type == O.data_type or I.data_type.lower() == 'any':
                                    I.value = O.value

            # 2. Execute the node itself (now that inputs are populated)
            node.EXEC_ON_CRAWLER_CB()

    def animate_active_graph(self):
        pag_instance = self
        # 1. Math: Create a heartbeat wave between 0.0 and 1.0
        current_time = time.time()
        intensity = (math.sin(current_time * 8.0) + 1.0) / 2.0 
        
        # Calculate glowing color (e.g., Deep Cyan to Bright White)
        r = int(50 + (150 * intensity))
        g = int(200 + (55 * intensity))
        b = 255
        
        # 2. Inject the calculated color instantly into the Theme's memory
        if ThemeManager.color_tag:
            dpg.set_value(ThemeManager.color_tag, [r, g, b, 255])

        # 3. Apply themes based on PAG's knowledge
        if hasattr(cfg, 'ui_links'):
            for link_uuid in cfg.ui_links.values():
                if link_uuid in pag_instance.active_ui_links:
                    # This link is Give it the glowing theme.
                    dpg.bind_item_theme(link_uuid, ThemeManager.active_theme)
                else:
                    # This link is dead/inactive. Revert to standard gray.
                    dpg.bind_item_theme(link_uuid, ThemeManager.default_theme)

pag = PAG()
# ---------------------------------------
def Node_initlizer(node_interface):
    def node_creation(sender, app_data,user_data):
        node_obj = cast(Node_template.NODE_INTERFACE,
                        node_interface(parent=cfg.editor_tag))
                        
        cfg.nodes[node_obj.ID] = node_obj
        node_obj.EXEC_GUI_CB()
    return node_creation

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

                        dpg.add_menu_item(label=node_interface.LABEL,
                                          callback=Node_initlizer(node_interface),
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

# In dpg_node_editor.py
def link_callback(sender, app_data):
    out_id, in_id = app_data
    link_id = dpg.add_node_link(out_id, in_id, parent=sender, user_data=(out_id, in_id))
    
    cfg.active_links[in_id] = out_id
    
    if not hasattr(cfg, 'ui_links'): cfg.ui_links = {}
    cfg.ui_links[in_id] = link_id  # Map input socket ID to the UI link

def delink_callback(sender, app_data):
    link_id = app_data
    link_info = dpg.get_item_user_data(link_id)
    
    if link_info:
        out_id, in_id = link_info
        
        cfg.active_links.pop(in_id, None)
        
        if hasattr(cfg, 'ui_links'): 
            cfg.ui_links.pop(in_id, None)
            
    dpg.delete_item(link_id)


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
    ThemeManager.setup()
    base_path  = os.path.dirname(__file__)
    nodes_path = os.path.abspath(os.path.join(base_path, "..", "examples", "nodes"))
    cfg.dirs["DEFAULT"] = nodes_path
    on_node_types_reload()

def unregister():
    cfg.dirs.clear()
    cfg.module_registry.clear()
    cfg.nodes.clear()
