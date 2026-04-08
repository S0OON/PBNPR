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
        self.flip   = False
        self.I_rgba = t.NodeSocket(dpg.generate_uuid(), t.RGBA, '<- Pixels (RGBA)')
        self.O_rgba = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Pixels (RGBA) ->')

        self._resgister_IO(
            [self.I_rgba],
            [self.O_rgba]
        )

    def on_gui(self):
        Id = super().on_gui()

        statics = self._create_static_attr()
        dpg.add_button(label="VIEW IMAGE (PIL)", parent=statics, callback=self.on_view_image)
        dpg.add_checkbox(label='Flip',           parent=statics, callback=self._on_change_flip)

        self._create_input_attr(self.I_rgba)
        self._create_output_attr(self.O_rgba)

    def _on_change_flip(self,S,A,U):
        self.flip = A

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
            if self.flip:
                pixels = np.flipud(pixels)

            # 4. Convert to PIL Image and Pop the Window!
            img = Image.fromarray(pixels, 'RGBA')
            img.show(title="NodeRivers Render Output")
            print(f"[{self.LABEL}] Image opened in default viewer!")
            
        except Exception as e:
            print(f"[{self.LABEL}] Error displaying image: {e}")
