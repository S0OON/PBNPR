from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t


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

        w,h,c = pixels.shape
        self.overlay.prepareGeometryChange()
        self.overlay._rect = t.QRectF(0,0,w,h)

        self.overlay.set_image(pixels)

        self.O_rgba.val = pixels
