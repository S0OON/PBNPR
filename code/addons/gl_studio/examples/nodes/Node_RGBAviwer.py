# Node_image_viewer.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import numpy as np
from PIL import Image
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'RGBA viewer'

    def __init__(self, parent):
        super().__init__(parent)

        self.EXECUTE = True
        self.ENABLE  = True

        self.I_RGBA_pixels = t.NodeSocket(dpg.generate_uuid(),t.RGBA,'<- RGBA viewer')

        self._resgister_IO(
            output_sockets=[self.I_RGBA_pixels],
        )

    def on_gui(self):
        super().on_gui()

        pixels = self._create_input_attr(self.I_RGBA_pixels)
        

    def on_should_execute(self): return self.ENABLE

    def on_execute_crawler(self, input_data=None): self.on_execute()

    def on_execute(self):
        pixels = self.I_RGBA_pixels.value
        
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
