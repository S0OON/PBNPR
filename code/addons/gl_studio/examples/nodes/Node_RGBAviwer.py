# Node_image_viewer.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import numpy as np
from PIL import Image

class NODE_INTERFACE:
    LABEL = "RGBA Viewer"
    
    def __init__(self, parent):
        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
        # --- Socket Setup ---
        self.I_pixels = t.NodeSocket(dpg.generate_uuid(), t.RGBA, '<- RGBA Pixels')
        self.O_out = t.NodeSocket(dpg.generate_uuid(),    t.NONE, 'Unused Output ->') # Placeholder to connect to a pulse node
        
        # --- Standard Callbacks ---
        self.EXEC_GUI_CB        = self.on_gui
        self.EXEC_CB            = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        
        self.SHOULD_EXEC_CB     = self.on_should_execute
        self.SHOULD_CRAWL_CB    = self.on_should_crawl
        self.SHOULD_BE_ACTIVE   = self.on_should_active
        
        # This is an endpoint node, so it doesn't need to enable/crawl downstream
        self.ENABLE = True
        self.ACTIVE = False
        self.CRAWL  = False
        
        self.inputs = {
            self.I_pixels.ID : self.I_pixels
        } 
        self.outputs = {}

    def on_gui(self):
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="View Image (PIL)", callback=self.on_view_button)

            # Input Socket
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_pixels.ID):
                dpg.add_text(self.I_pixels.name)

            #otuputs
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_out.ID):
                dpg.add_text(self.O_out.name)

    # --- Execution Callbacks ---
    def on_view_button(self, sender, app_data):
        pixels = self.I_pixels.value
        
        if pixels is None or not isinstance(pixels, np.ndarray):
            print(f"[{self.LABEL}] Error: No valid pixel data found. Execute the render node first!")
            return
            
        try:
            # OpenGL framebuffers are read bottom-up. 
            # We flip it vertically so it looks correct in PIL.
            flipped_pixels = np.flipud(pixels)
            
            # Convert Numpy array to PIL Image and show it
            img = Image.fromarray(flipped_pixels, 'RGBA')
            img.show()
            
            print(f"[{self.LABEL}] Opened image in default viewer.")
        except Exception as e:
            print(f"[{self.LABEL}] Failed to open image: {e}")

    # Standard boilerplate returning safe defaults
    def on_should_execute(self): return False
    def on_should_crawl(self): return False
    def on_should_active(self): return False
    def on_execute(self): pass
    
    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB():
            self.on_execute()
        
    def on_execute_after_frame(self): pass