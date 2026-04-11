# Node_template_advanced.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.gl.ModernOpenGL import GLctx as GL


class NODE_BASE_INTERFACE:
    CATEGORY = 'NONE'
    LABEL = "BASE EMPTY NODE"
    
    def __init__(self, parent):
        """
        base node class methods are 2 types / 2 phases Init and Runtime:

        - on_gui -> for drawing the node ui

        - Behavior methods: EACH does nothing unless overriden

            on_execute() -> Utlity method for u <3

            on_execute_crawler() -> called by PAG system when the node is connected to a root node (output node)

            on_execute_after_frame() -> called by PAG system when the node is active and after frame rendering.

        CACHE = False, 
        
        this is turned on by the PAG class so it wont execute twice in the same frame if its connected to multiple nodes, 
        You can reset it by setting it to False again if more than one execution is needed.


        x------------------------------------x

        # Base Class Provides:
        
        x------------------------------------x

        - PARENT = parent (paramter passed at init)

        - ID = dpg.generate_uuid()
    
        - EXEC_GUI_CB        = self.on_gui

        - EXEC_ON_CRAWLER_CB = self.on_execute_crawler

        - EXEC_CB            = self.on_execute

        - EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        

    
        x------------------------------------x

        # PAG SYSTEM:
        
        x------------------------------------x

        - self.inputs = {} 
    
        - self.outputs = {}

            These are used so the PAG knows the scokets and overrite their values from connceted nodes.

            Both are handeled with this helper:

            - _register_IO(
                            [Node_socket...], #inputs
                            [Node_socket...]  #outputs
                            )

        - SHOULD_CRAWL_CB    = self.on_should_crawl 
        
        Tells PAG this is a root node aka output node in a node tree, meaning it will execute all connected nodes

        """
        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
        self.EXEC_GUI_CB        = self.on_gui
        self.EXEC_CB            = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        
        self.SHOULD_CRAWL_CB    = self.on_should_crawl
        
        self.CACHE = False

        # Node sockets:
        # PLUGIN inputs/outputs system
        self.inputs = {} 
        self.outputs = {}


        self.GL = GL.get()  # Access the shared ModernGL context

    def _resgister_IO(self, 
                      input_sockets:list[t.NodeSocket]=None, 
                      output_sockets:list[t.NodeSocket]=None):
        if input_sockets:
            for sock in input_sockets:
                self.inputs[sock.ID] = sock

        if output_sockets:
            for sock in output_sockets:
                self.outputs[sock.ID] = sock

    def _create_static_attr(self, label=None):
        return dpg.add_node_attribute(parent=self.ID, tag=dpg.generate_uuid(),attribute_type=dpg.mvNode_Attr_Static, label=label)

    def _create_input_attr(self, socket: t.NodeSocket, pin_shape=dpg.mvNode_PinShape_CircleFilled, use_name=True, color=None):
        Id = dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input,
                                    parent=self.ID, tag=socket.ID, 
                                    shape=pin_shape)

        if use_name:
            dpg.add_text(socket.name, parent=Id)
            
        # Check dictionary, but catch mismatches with a debug print
        pin_color = color if color else t.SOCKET_COLORS.get(socket.data_type)
        if not pin_color:
            print(f"[{self.LABEL}] Theme Warning: Unmatched socket type '{socket.data_type}'. Defaulting to Grey.")
            pin_color = (160, 160, 160)
            
        self._apply_pin_color(Id, pin_color)

        return Id

    def _create_output_attr(self, socket: t.NodeSocket, pin_shape=dpg.mvNode_PinShape_CircleFilled, use_name=True, color=None):
        Id = dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Output, 
                                    parent=self.ID, tag=socket.ID,
                                    shape=pin_shape)
        
        if use_name:
            dpg.add_text(socket.name, parent=Id)
            
        # Check dictionary, but catch mismatches with a debug print
        pin_color = color if color else t.SOCKET_COLORS.get(socket.data_type)
        if not pin_color:
            print(f"[{self.LABEL}] Theme Warning: Unmatched socket type '{socket.data_type}'. Defaulting to Grey.")
            pin_color = (160, 160, 160)

        self._apply_pin_color(Id, pin_color)
        return Id


    def _apply_pin_color(self, attr_id, color_tuple):
        with dpg.theme() as T:
            # 0 = dpg.mvAll. Bypasses DPG's strict component bug.
            with dpg.theme_component(0): 
                # Safely unpack just the RGB and enforce 255 alpha
                r, g, b = color_tuple[:3]
                dpg.add_theme_color(dpg.mvNodeCol_Pin, (r, g, b, 255), category=dpg.mvThemeCat_Nodes)
                
                # Bonus: Add a hover state
                #dpg.add_theme_color(dpg.mvNodeCol_PinHovered, (min(r+50, 255), min(g+50, 255), min(b+50, 255), 255), category=dpg.mvThemeCat_Nodes)
                
        dpg.bind_item_theme(attr_id, T)


    def on_gui(self):
        """
        creates a node and return ID (Same as self.ID)
        """
        return dpg.add_node(label=self.LABEL, parent=self.PARENT, tag=self.ID)
# Execution behaviors
    def on_should_crawl(self):"""Return True if this node is a root for PAG crawler execution"""
    def on_execute(self):"""Called when user clicks execute button"""
    def on_execute_crawler(self, input_data=None): """Called by PAG system when the node is connected to a crawler branch node"""
    def on_execute_after_frame(self):"""Execution after frame rendering"""
