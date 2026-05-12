import bpy
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget, QCheckBox

PRESISTANT = "img_name"
NAMED_AS = "named_as"
FLIP_V = "flip_v"
IMG_FLOAD_FORMAT = "f4"


class NODE_IMG_DATA(BASE.NODE_INTERFACE):
    NODE_NAME = "Image Data"
    CATEGORY = "Blender"

    def __init__(self):
        super().__init__()
        self.O_pixels = self.add_output(name="Pixels", type=t.RGBA)
        self.O_w = self.add_output(name="Width", type=t.F)
        self.O_h = self.add_output(name="Height", type=t.F)
        self.O_Channels = self.add_output(name="Channels", type=t.F)
        self.O_pkg = self.add_output("Packed data", type=t.DICT)
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.line = QLineEdit()
        self.line.setPlaceholderText("Source Image Name...")
        self.line.textChanged.connect(lambda v: self.set(PRESISTANT, v))
        lay.addWidget(self.line)

        self.line_named = QLineEdit()
        self.line_named.setPlaceholderText("Named as (Optional)...")
        self.line_named.textChanged.connect(lambda v: self.set(NAMED_AS, v))
        lay.addWidget(self.line_named)

        self.flip_check = QCheckBox("Flip Vertical")
        self.flip_check.stateChanged.connect(lambda v: self.set(FLIP_V, self.flip_check.isChecked()))
        self.flip_check.setStyleSheet("color: white;")
        lay.addWidget(self.flip_check)

        self.status_label = QLabel()
        lay.addWidget(self.status_label)

        return widget

    def reset(self, v=None):
        if self.has(PRESISTANT):
            self.line.setText(self.get(PRESISTANT))
        else:
            self.add(PRESISTANT, self.line.text())

        if self.has(NAMED_AS):
            self.line_named.setText(self.get(NAMED_AS))
        else:
            self.add(NAMED_AS, self.line_named.text())

        if self.has(FLIP_V):
            self.flip_check.setChecked(self.get(FLIP_V))
        else:
            self.add(FLIP_V, False)

        self.status_label.setText("No image linked")
        self.status_label.setStyleSheet(t.RED)
        self.O_pixels.val = 0
        self.O_w.val = 0
        self.O_h.val = 0
        self.O_Channels.val = 0
        self.O_pkg.val = {}

    def on_stream(self):
        img_name = self.line.text()
        img = bpy.data.images.get(img_name)
        if not img:
            self.status_label.setText(f"Missing: {img_name}")
            self.status_label.setStyleSheet(t.RED)
            self.O_pixels.val = 0
            return

        self.status_label.setText(f"Linked: {img.name}")
        self.status_label.setStyleSheet(t.GREEN)

        w, h = img.size
        channels = img.channels

        # 1. Pre-allocate (1D flat array)
        result = np.empty(w * h * channels, dtype=np.float32)

        # 2. Fast copy
        img.pixels.foreach_get(result)

        # 3. Reshape (Must be Height first, then Width)
        result = result.reshape((h, w, channels))

        # 4. Vertical Flip if requested
        if self.get(FLIP_V):
            result = np.flipud(result)

        # 5. Determine the key for the output dictionary
        pkg_key = self.line_named.text() if self.line_named.text() else img_name

        self.O_pixels.val = result
        self.O_w.val = w
        self.O_h.val = h
        self.O_Channels.val = channels
        self.O_pkg.val = {
            pkg_key: result
        }

    def on_graph_load(self):
        self.reset()
