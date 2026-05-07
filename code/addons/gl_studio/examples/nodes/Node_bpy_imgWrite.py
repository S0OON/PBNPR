import bpy
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget, QCheckBox


PRESISTANT = "img_name"
FLIP_V = "flip_v"

class NODE_IMG_WRITE(BASE.NODE_INTERFACE):
    NODE_NAME = "Image Write"
    CATEGORY = "Blender"

    def __init__(self):
        super().__init__()
        self.I_pixels = self.add_input(name="Pixels", type=t.RGBA)
        self.O_pixels = self.add_output("Pixels", type=t.RGBA)
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.line = QLineEdit()
        self.line.setPlaceholderText("Target Image Name...")
        self.line.textChanged.connect(lambda v: self.set(PRESISTANT, v))
        lay.addWidget(self.line)

        self.flip_check = QCheckBox("Flip Vertical")
        self.flip_check.stateChanged.connect(lambda v: self.set(FLIP_V, self.flip_check.isChecked()))
        lay.addWidget(self.flip_check)

        self.status_label = QLabel()
        lay.addWidget(self.status_label)

        return widget

    def reset(self, v=None):
        if self.has(PRESISTANT):
            self.line.setText(self.get(PRESISTANT))
        else:
            self.add(PRESISTANT, self.line.text())

        if self.has(FLIP_V):
            self.flip_check.setChecked(self.get(FLIP_V))
        else:
            self.add(FLIP_V, False)

        self.status_label.setText("No target image")
        self.status_label.setStyleSheet(t.RED)

    def on_stream(self):
        self.on_sync_port_values()
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
        self.O_pixels.val = pixels_data

        # Check if input has valid data
        if pixels_data is None or (isinstance(pixels_data, (int, float)) and pixels_data == 0):
            self.status_label.setText("Waiting for pixels...")
            self.status_label.setStyleSheet(t.RED)
            return

        try:
            # 1. Ensure it's a Numpy Array
            if not isinstance(pixels_data, np.ndarray):
                pixels_data = np.array(pixels_data)

            # 2. Handle Normalization if uint8
            if pixels_data.dtype == np.uint8:
                pixels_data = pixels_data.astype(np.float32) / 255.0
            elif pixels_data.dtype != np.float32:
                pixels_data = pixels_data.astype(np.float32)

            # 3. Shape Validation
            # Expected shape in (Height, Width, Channels) or (Height, Width)
            target_h, target_w = img.size[1], img.size[0]
            target_c = img.channels

            # If it's a flat array, we can only check total size
            if pixels_data.ndim > 1:
                in_h, in_w = pixels_data.shape[0], pixels_data.shape[1]
                in_c = pixels_data.shape[2] if pixels_data.ndim > 2 else 1

                if in_h != target_h or in_w != target_w or in_c != target_c:
                    self.status_label.setText(f"Shape Mismatch: {pixels_data.shape} vs ({target_h}, {target_w}, {target_c})")
                    self.status_label.setStyleSheet(t.RED)
                    return

            # 4. Vertical Flip if requested
            if self.get(FLIP_V) and pixels_data.ndim >= 2:
                pixels_data = np.flipud(pixels_data)

            # 5. Final Flatten and Write
            pixels_flat = pixels_data.ravel()

            expected_size = target_w * target_h * target_c
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
