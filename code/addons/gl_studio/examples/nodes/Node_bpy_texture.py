# Node_bpy_texture.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import numpy as np

try:
    import bpy
except ImportError:
    bpy = None

class NODE_INTERFACE(BASE_NODE):
    CATEGORY = 'Evaluate'
    LABEL = 'Blender Image to Texture'
    
    def __init__(self, parent):
        super().__init__(parent)
        

        self.I_name = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- Image Name', 'Render Result')

        self.O_texture_data = t.NodeSocket(dpg.generate_uuid(), t.OB, 'Texture Data (dict) ->')
        
        self._resgister_IO([self.I_name], 
                           [self.O_texture_data])
        
    def on_gui(self):
        Id = super().on_gui()

        statics = self._create_static_attr()
        dpg.add_input_text(label="Image Name", default_value=self.I_name.value,
                          callback=self._on_change, parent=statics, width=150)
        

        self._create_input_attr(self.I_name)
        
        self._create_output_attr(self.O_texture_data)
        

    def _on_change(self, s, a, u): self.I_name.value = a
    
    def on_execute(self):
        if not bpy:
            return
            
        b_img = bpy.data.images.get(self.I_name.value)
        if not b_img:
            print(f"[{self.LABEL}] Image '{self.I_name.value}' not found")
            self.O_texture_data.value = { 
                'size': (1, 1),
                'channels': 4,
                'data': np.array([1.0, 1.0, 1.0, 1.0], dtype=np.float32).tobytes(),
                'dtype': 'f4'
            }
            return
        
        # Convert Blender float pixels to bytes
        pixels = np.array(b_img.pixels, dtype=np.float32)
        
        self.O_texture_data.value = {
            'size': (b_img.size[0], b_img.size[1]),
            'channels': 4,
            'data': pixels.tobytes(),
            'dtype': 'f4'
        }
        print(f"[{self.LABEL}] Converted '{self.I_name.value}' {b_img.size[0]}x{b_img.size[1]}")

    def on_execute_crawler(self, input_data=None):
        self.on_execute()