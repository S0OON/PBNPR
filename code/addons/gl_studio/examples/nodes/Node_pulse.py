# Node_pulse.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import time
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE


class NODE_INTERFACE(BASE_NODE):
    LABEL = "Pulse Trigger"

    def __init__(self, parent):
        super().__init__(parent)

        self.EXECUTE=False
        self.CRAWL = True

        self.I_branch_socket = t.NodeSocket(dpg.generate_uuid(),t.NONE,'<- Crawl',value=5.0)
        self.last_pulse_time = time.time() 
                
        self._resgister_IO(input_sockets=[self.I_branch_socket])

    def on_gui(self):
        super().on_gui()

        float_time = self._create_input_attr(self.I_branch_socket)
        dpg.add_drag_float(label="Interval (s)", callback=self.on_float_change, 
                            default_value=self.I_interval.value, speed=0.05, width=100)


# --- Execution Logic ---
    def on_enable_change(self, sender, app_data):
        self.ENABLE = app_data
        if self.ENABLE:
            self.last_pulse_time = time.time() 

    def on_float_change(self, sender, app_data):
        self.I_interval.value = max(0.016, app_data) # 0.016 is roughly 60fps

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
        
    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB():
            self.on_execute()
    