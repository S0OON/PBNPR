import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import numpy as np
import bpy

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'MGL Texture'
    
    def __init__(self, parent):
        super().__init__(parent)

        self.I_name = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- Blender Image Name')
        self.O_tex =  t.NodeSocket(dpg.generate_uuid(), t.OB, 'Texture RGBA ->')
        
        self._tex = None
        self._last_hash = None  # For change detection
        
    def on_execute(self):
        if not bpy: 
            return
        
        b_img = bpy.data.images.get(self.I_name.value)
        if not b_img: 
            print(f"Texture '{self.I_name.value}' not found")
            return
            
        # Detect changes (Blender images update pixels in-place)
        current_hash = hash(b_img.pixels[:100])  # Sample check
        if current_hash == self._last_hash and self._tex:
            return  # No change, reuse
            
        ctx = GLctx.get()
        if self._tex: 
            self._tex.release()
        
        pixels = np.array(b_img.pixels, dtype=np.float32)
        self._tex = ctx.texture((b_img.size[0], b_img.size[1]), 4, pixels.tobytes(), dtype='f4')
        self._last_hash = current_hash
        self.O_tex.value = self._tex