from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
import numpy as np


class NODE_RGBA_DISPLAY(BASE.NODE_INTERFACE):
    NODE_NAME = "RGBA Display"
    CATEGORY = "Output"

    def __init__(self):
        super().__init__()
        self.I_rgba = self.add_input("Pixels", type=t.RGBA)
        self.O_rgba = self.add_output("Pixels", type=t.RGBA)

        self.overlay = t.NativeNumpyOverlay(parent=self.view, width=200, height=200)

    def on_stream(self):
        self.on_sync_port_values()
        pixels = self.I_rgba.val

        if pixels is None or not isinstance(pixels, np.ndarray):
            return

        # Correct unpacking: (Height, Width, Channels)
        if pixels.ndim == 3:
            h, w, c = pixels.shape
        elif pixels.ndim == 2:
            h, w = pixels.shape
        else:
            return

        self.overlay.prepareGeometryChange()
        # QRectF expects (x, y, Width, Height)
        self.overlay._rect = t.QRectF(0, 0, w, h)

        self.overlay.set_image(pixels)

        self.O_rgba.val = pixels
