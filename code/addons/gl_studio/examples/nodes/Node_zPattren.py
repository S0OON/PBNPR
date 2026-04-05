# Node_template_advanced.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t


class NODE_BASE_INTERFACE:
    LABEL = "BASE EMPTY NODE"
    
    def __init__(self, parent):
        """
        base node class methods are 2 types / 2 phases Init and Runtime:

        - on_gui -> for drawing the node ui

        - Behavior methods: EACH makes nothing unless overriden

            on_execute() -> Utlity method for u <3

            on_execute_crawler(input_data) -> called by PAG system when the node is connected to a crawler branch node

            on_execute_after_frame() -> called by PAG system when the node is active and after frame rendering.

        CACHE = False, this is turned on by the PAG class so it wont execute twice in the same frame if its connected to multiple nodes, but you can also use it to make your node execute only once and cache the result for the next executions in the same frame. You can reset it by setting it to False again.

            
        x------------------------------------x

        Base Class Provides:
        
        x------------------------------------x

        PARENT = parent (paramter passed at init)

        ID = dpg.generate_uuid()
    
        EXEC_GUI_CB        = self.on_gui

        EXEC_ON_CRAWLER_CB = self.on_execute_crawler

        EXEC_CB            = self.on_execute

        EXEC_ON_LOOP_CB    = self.on_execute_after_frame
    
        
        inputs = {} 
    
        outputs = {}
    
        # PAG CALLBACK:

        -SHOULD_CRAWL_CB    = self.on_should_crawl 
        
        Tells PAG this is a root node in a node tree

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
        return dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Static, parent=self.ID, tag=dpg.generate_uuid(),label=label)

    def _create_input_attr(self, socket:t.NodeSocket,pin_shape=dpg.mvNode_PinShape_CircleFilled):
        return dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input,
                                      parent=self.ID, tag=socket.ID, 
                                      shape=pin_shape)

    def _create_output_attr(self, socket:t.NodeSocket,pin_shape=dpg.mvNode_PinShape_CircleFilled):
        return dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Output, 
                                      parent=self.ID, tag=socket.ID,
                                      shape=pin_shape)


    def on_gui(self):
        """
        creates a node and return ID (Same as self.ID)
        """
        return dpg.add_node(label=self.LABEL, parent=self.PARENT, tag=self.ID)

# Executions behavior
    def on_should_crawl(self):"""Return True if this node is a root for PAG crawler execution"""
    def on_execute(self):"""Called when user clicks execute button"""
    def on_execute_crawler(self, input_data=None): """Called by PAG system when the node is connected to a crawler branch node"""
    def on_execute_after_frame(self):"""Execution after frame rendering"""
