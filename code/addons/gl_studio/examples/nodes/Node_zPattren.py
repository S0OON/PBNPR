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

            on_execute() -> called when user clicks execute button

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
        
        use it to tell PAG this is a root node in a node tree

        
        # (OPTIONAL) thses have also 2 phases / 2 uses; 1.Init  2.Runtime:

        EXECUTE= False   - Button; ui only (manual)

        ENABLE = False   - Chechbox; should it execute based on the checkbox state

        ACTIVE = False   - Chechbox; should it execute after frame based on the checkbox state

        CRAWL  = False   - Chechbox; should it execute crawler based on the checkbox state

        1.Changed at __init__: to tell on_gui that you want to show the execute button and checkboxes

        2.Changed by on_change methods: by You
        """
        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
        self.EXEC_GUI_CB        = self.on_gui
        self.EXEC_CB            = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        
        self.SHOULD_CRAWL_CB    = self.on_should_crawl
        
        # thses have 2 uses;
        # 1. Changed at __init__         : to tell on_gui that you want to show the execute button and checkboxes
        # 2. Changed by on_change methods:Used by node itself to decide if it should execute or not, based on the checkboxes state
        self.EXECUTE= False
        self.ENABLE = False
        self.ACTIVE = False
        self.CRAWL  = False
        
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

    def _create_input_attr(self, socket:t.NodeSocket):
        id = dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, parent=self.ID, tag=socket.ID)
        return id

    def _create_output_attr(self, socket:t.NodeSocket):
        id = dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, parent=self.ID, tag=socket.ID)
        return id

    def on_gui(self):
        """
        THE UI NODE TAG IS SAME AS ID.

        The Base class Function does:-

        
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
        
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                if self.EXECUTE:
                    dpg.add_button(label="Execute",  callback=self.EXEC_CB)
                if self.ENABLE:
                    dpg.add_checkbox(label="Enable", callback=self.on_enable_change)
                if self.ACTIVE:
                    dpg.add_checkbox(label="Active", callback=self.on_active_change)
                if self.CRAWL:
                    dpg.add_checkbox(label="Crawl",  callback=self.on_crawl_change)
        
        """
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            # Static 
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                if self.EXECUTE:
                    dpg.add_button(label="Execute",  callback=self.EXEC_CB)
                if self.ENABLE:
                    dpg.add_checkbox(label="Enable", callback=self.on_enable_change)
                if self.ACTIVE:
                    dpg.add_checkbox(label="Active", callback=self.on_active_change)
                if self.CRAWL:
                    dpg.add_checkbox(label="Crawl",  callback=self.on_crawl_change)

# Changers
    def on_change_enable(self, sender, app_data):
        self.ENABLE = app_data
    
    def on_change_active(self, sender, app_data):
        self.ACTIVE = app_data
        
    def on_change_crawl(self, sender, app_data):
        self.CRAWL = app_data
# Executions behavior
    def on_should_crawl(self):  return None
    
    def on_execute(self):"""Called when user clicks execute button"""
    def on_execute_crawler(self, input_data=None): """Called by PAG system when the node is connected to a crawler branch node"""
    def on_execute_after_frame(self):"""Execution after frame rendering"""
