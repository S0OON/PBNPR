# Node_pulse.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import time

class NODE_INTERFACE:
    LABEL = "Pulse Trigger"
    
    def __init__(self, parent):
        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
        # 1. Define Sockets
        self.I_interval = t.NodeSocket(dpg.generate_uuid(), t.F  ,'seconds')
        self.O_trigger  = t.NodeSocket(dpg.generate_uuid(), t.ANY,'time')
        
        # Default to 1 pulse per second
        self.I_interval.value = 1.0  
        
        # The Stopwatch
        self.last_pulse_time = time.time() 
        
        self.EXEC_GUI_CB        = self.on_gui
        self.EXEC_CB            = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        
        self.SHOULD_EXEC_CB     = self.on_should_execute
        self.SHOULD_CRAWL_CB    = self.on_should_crawl
        self.SHOULD_BE_ACTIVE   = self.on_should_active
        
        self.ENABLE = True
        self.ACTIVE = False
        
        self.inputs = {
            self.I_interval.ID : self.I_interval
        } 
        
        self.outputs = {
            self.O_trigger.ID : self.O_trigger
        }

    def on_gui(self):
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            
            # Static Controls
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_checkbox(label="Enable", callback=self.on_enable_change, default_value=self.ENABLE)

            # Interval Float Input
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_interval.ID):
                dpg.add_drag_float(label="Interval (s)", callback=self.on_float_change, 
                                   default_value=self.I_interval.value, speed=0.05, width=100)
            
            # Output Trigger
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_trigger.ID):
                dpg.add_text("Pulse Out ->")

    # --- UI Callbacks ---
    def on_enable_change(self, sender, app_data):
        self.ENABLE = app_data
        if self.ENABLE:
            # Reset the stopwatch the moment they turn it back on
            self.last_pulse_time = time.time() 

    def on_float_change(self, sender, app_data):
        self.I_interval.value = max(0.016, app_data) # 0.016 is roughly 60fps

    # --- Execution Logic ---
    def on_should_execute(self):
        return self.ENABLE
    
    def on_should_crawl(self):
        if not self.ENABLE:
            return False
            
        current_time = time.time()
        
        if current_time - self.last_pulse_time >= self.I_interval.value:
            self.last_pulse_time = current_time
            return True
            
        return False
        
    def on_should_active(self):
        return self.ACTIVE and self.ENABLE
    
    def on_execute(self):
        self.O_trigger.value = time.time()
        
    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB():
            self.on_execute()
    
    def on_execute_after_frame(self):
        pass