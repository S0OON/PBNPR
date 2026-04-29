import bpy
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget


PRESISTANT = "img_name"

class NODE_IMG_WRITE(BASE.NODE_INTERFACE):
    NODE_NAME = "Image Write"
    CATEGORY = "Blender"

    def __init__(self):
        super().__init__()
        self.I_pixels = self.add_input(name="Pixels", type=t.RGBA)
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.line = QLineEdit()
        self.line.setPlaceholderText("Target Image Name...")
        self.line.textChanged.connect(lambda v: self.set(PRESISTANT, v))
        lay.addWidget(self.line)

        self.status_label = QLabel()
        lay.addWidget(self.status_label)

        return widget

    def reset(self, v=None):
        if self.has(PRESISTANT):
            self.line.setText(self.get(PRESISTANT))
        else:
            self.add(PRESISTANT, self.line.text())

        self.status_label.setText("No target image")
        self.status_label.setStyleSheet(t.RED)

    def on_stream(self):
        img_name = self.line.text()
        if not img_name:
            self.status_label.setText("Enter image name")
            self.status_label.setStyleSheet(t.RED)
            return

        img = bpy.data.images.get(img_name)
        if not img:
            self.status_label.setText(f"Missing: {img_name}")
            self.status_label.setStyleSheet(t.RED)
            return

        pixels_data = self.I_pixels.val

        # Check if input has valid data
        if pixels_data is None or (isinstance(pixels_data, (int, float)) and pixels_data == 0):
            self.status_label.setText("Waiting for pixels...")
            self.status_label.setStyleSheet(t.RED)
            return

        try:
            if not isinstance(pixels_data, np.ndarray):
                pixels_data = np.array(pixels_data, dtype=np.float32)

            # Flatten to 1D as required by Blender's foreach_set
            pixels_flat = pixels_data.ravel()

            # Verify dimensions match
            expected_size = img.size[0] * img.size[1] * img.channels

            if len(pixels_flat) != expected_size:
                self.status_label.setText(f"Size Error: {len(pixels_flat)} vs {expected_size}")
                self.status_label.setStyleSheet(t.RED)
                return

            img.pixels.foreach_set(pixels_flat)
            img.update()

            self.status_label.setText(f"Updated: {img.name}")
            self.status_label.setStyleSheet(t.GREEN)

        except Exception as e:
            self.status_label.setText(f"Error: {str(e)}")
            self.status_label.setStyleSheet(t.RED)

    def on_graph_load(self):
        self.reset()
