import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PIL import Image
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap


class NODE_RGBA_DISPLAY(BASE.NODE_INTERFACE):
    NODE_NAME = "Pixels Display"
    CATEGORY = "Output"

    _current_qimg = None
    _current_array = None

    def __init__(self):
        super().__init__()
        self.I_rgba = self.add_input("RGBA pixels", type=t.RGBA)
        self.O_rgba = self.add_output("rgba_data", type=t.RGBA)
        self.reset()

    def on_gui(self):
        self.image_label = QLabel()
        self.pixMap = QPixmap()
        self.image_label.setPixmap(self.pixMap)
        return self.image_label

    def on_stream(self):
        self.on_sync_port_values()

        pisexels = self.I_rgba.val
        self.set_image(pisexels)
        self.O_rgba.val = pisexels

    def set_image(self, image_array):
            """ Accepts a numpy array of shape (h, w, c) or (h, w) and updates the widget. """
            if not isinstance(image_array, np.ndarray):
                raise TypeError("Input must be a numpy array")

            # QImage requires uint8 data
            if image_array.dtype != np.uint8:
                # Check if it's a floating point array (0.0 to 1.0)
                if image_array.dtype in [np.float32, np.float64]:
                    # Scale by 255, clip to prevent overflow, and cast to uint8
                    image_array = (np.clip(image_array, 0.0, 1.0) * 255.0).astype(np.uint8)
                else:
                    image_array = image_array.astype(np.uint8)

            # Handle dimensions and channels
            if len(image_array.shape) == 3:
                h, w, channels = image_array.shape
            elif len(image_array.shape) == 2:
                h, w = image_array.shape
                channels = 1
            else:
                raise ValueError("Array must be 2D or 3D")


            bytes_per_line = channels * w

            # Map number of channels to the correct QImage format
            if channels == 1:
                fmt = QImage.Format_Grayscale8
            elif channels == 3:
                fmt = QImage.Format_RGB888
            elif channels == 4:
                fmt = QImage.Format_RGBA8888
            else:
                raise ValueError(f"Unsupported number of channels: {channels}")

            # Store a contiguous copy of the array safely in the class
            self._current_array = np.ascontiguousarray(image_array)

            # Create QImage from the memory buffer
            self._current_qimg = QImage(
                self._current_array.data,
                w,
                h,
                bytes_per_line,
                fmt
            )
            self.pixMap.fromImage(self._current_qimg)
            self.update()
