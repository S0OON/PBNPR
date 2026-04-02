# Node_template_advanced.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import time

class NODE_INTERFACE:
    LABEL = "Template"
    
    def __init__(self, parent):
        self.I_f = t.NodeSocket(dpg.generate_uuid(),t.F)
        self.O_f = t.NodeSocket(dpg.generate_uuid(),t.F)

        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
        self.EXEC_GUI_CB        = self.on_gui
        self.EXEC_CB            = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        
        self.SHOULD_EXEC_CB     = self.on_should_execute
        self.SHOULD_CRAWL_CB    = self.on_should_crawl
        self.SHOULD_BE_ACTIVE   = self.on_should_active
        
        self.ENABLE = False
        self.ACTIVE = False
        self.CRAWL  = False
        
        # Node sockets:
        # PLUGIN inputs/outputs system
        self.inputs = {
            self.I_f.ID : self.I_f} 
        
        self.outputs = {
            self.O_f.ID : self.O_f}

        # previous vars are called from the plugin.
        # util User customization (private)
        self.code_snippet = "result = input_text.upper()"
        self.blender_operation = "None"  # bpy.ops.mesh, etc.

    def on_gui(self):
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            # Static 
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute",  callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable", callback=self.on_enable_change)
                dpg.add_checkbox(label="Active", callback=self.on_active_change)
                dpg.add_checkbox(label="Crawl",  callback=self.on_crawl_change)

            # inputs
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input,tag=self.I_f.ID):
                dpg.add_text(label="<- Input")
                dpg.add_input_float(label='im a float boi',callback=self.on_float_change)
            
            # outs
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output,tag=self.O_f.ID):
                dpg.add_text(label="Output ->")
#Center
    def on_enable_change(self, sender, app_data):
        self.ENABLE = app_data
    
    def on_active_change(self, sender, app_data):
        self.ACTIVE = app_data
        
    def on_crawl_change(self, sender, app_data):
        self.CRAWL = app_data
#Peripheral
    def on_float_change(self, sender, app_data):
        self.I_f.value = app_data
#Center
    def on_should_execute(self):
        return self.ENABLE
    
    def on_should_crawl(self):
        return self.CRAWL
    
    def on_should_active(self):
        return self.ACTIVE and self.ENABLE
    
    def on_execute(self):
        self.O_f.value = self.I_f.value
        print(self.I_f.value, " : ", self.O_f.value)
    
    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB():
            self.on_execute()
    
    def on_execute_after_frame(self):
        pass
    