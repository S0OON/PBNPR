import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import numpy as np
from PIL import Image

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'RGBA Viewer'

    def __init__(self, parent):
        super().__init__(parent)
        
        # --- Sockets Setup ---
        self.I_rgba = t.NodeSocket(dpg.generate_uuid(), t.RGBA, '<- Pixels (RGBA)')
        self.O_rgba = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Pixels (RGBA) ->')

        self._resgister_IO(
            [self.I_rgba],
            [self.O_rgba]
        )

    def on_gui(self):
        Id = super().on_gui()

        # Static controls
        statics = self._create_static_attr()
        dpg.add_button(label="VIEW IMAGE (PIL)", callback=self.on_view_image, parent=statics)

        # Inputs / Outputs
        i= self._create_input_attr(self.I_rgba)
        dpg.add_text(self.I_rgba.name, parent=i)
        o= self._create_output_attr(self.O_rgba)
        dpg.add_text(self.O_rgba.name, parent=o)

    def on_execute(self):
        if self.I_rgba.value is not None:
            self.O_rgba.value = self.I_rgba.value
            print(f"[{self.LABEL}] Pixels passed through.")
        else:
            print(f"[{self.LABEL}] Warning: No pixel data received.")
        
        self.on_view_image()

    def on_view_image(self):
        # 1. Grab the pixels from the socket
        pixels = self.I_rgba.value
        
        # 2. Validate
        if pixels is None or not isinstance(pixels, np.ndarray):
            print(f"[{self.LABEL}] Error: No valid Numpy image array to view.")
            return
            
        try:
            # 3. Flip upside-down (OpenGL vs Screen coordinate mismatch fix)
            flipped_pixels = np.flipud(pixels)
            
            # 4. Convert to PIL Image and Pop the Window!
            img = Image.fromarray(flipped_pixels, 'RGBA')
            img.show(title="NodeRivers Render Output")
            print(f"[{self.LABEL}] Image opened in default viewer!")
            
        except Exception as e:
            print(f"[{self.LABEL}] Error displaying image: {e}")
