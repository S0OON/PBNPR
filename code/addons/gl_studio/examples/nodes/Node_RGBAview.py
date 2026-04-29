import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PIL import Image, ImageOps
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget
from PySide6.QtGui import QImage, QPixmap




class NODE_RGBA_VIEWER(BASE.NODE_INTERFACE):
    NODE_NAME = "RGBA Viewer"
    CATEGORY = "Output"

    def __init__(self):
        super().__init__()

        self.I_rgba = self.add_input("RGBA pixels", type=t.RGBA)
        self.I_w = self.add_input("width", type=t.F)
        self.I_h = self.add_input("height", type=t.F)

        self.O_rgba = self.add_output("rgba_data", type=t.RGBA)
        self.O_mock = self.add_output("Mock output", type=t.NONE)
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.image_label = QLabel()
        self.image_label.setScaledContents(False)
        self.image_label.setFixedSize(100,100)
        lay.addWidget(self.image_label)

        self.status_label = QLabel()
        lay.addWidget(self.status_label)

        btn_view = QPushButton("View Image (PIL)")
        btn_view.setStyleSheet(
            "background-color: #2b5c8f; color: white; font-weight: bold; padding: 5px;"
        )
        btn_view.clicked.connect(self.on_view_clicked)
        lay.addWidget(btn_view)

        return widget

    def reset(self, txt="No Data"):
        self.I_w.val = t.RES_W
        self.I_h.val = t.RES_H
        self.I_rgba.val = None
        self.O_rgba.val = None
        self.status_label.setText(txt)
        self.status_label.setStyleSheet(t.RED)

    def on_stream(self):
        self.on_sync_port_values()

        current_pixels = self.I_rgba.val

        self.O_rgba.val = current_pixels

        # 3. Update UI
        if current_pixels is not None:
            self.status_label.setText("Status: Data Ready")
            self.status_label.setStyleSheet(t.GREEN)
        else:
            self.reset()
            return

        # Assuming 'img_array' is an np.array of shape (H, W, 4) of type uint8
        height, width, channels = current_pixels.shape
        bytes_per_line = channels * width

        # Convert numpy array to QImage
        q_img = QImage(current_pixels.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
        self.image_label.setPixmap(QPixmap.fromImage(q_img))

    def on_view_clicked(self):
        data = self.I_rgba.val

        # Safer check: 'not any(data)' can throw errors on large byte arrays or numpy arrays
        if not any(data):
            self.reset("No data to view!")
            return

        try:
            w = int(self.I_w.val)
            h = int(self.I_h.val)

            # 1. Feed the raw fbo.read() bytes directly into PIL.
            # PIL expects size as a tuple (w, h).
            # "RGB" matches components=3.
            image = Image.
            image = Image.frombytes("RGB", (w, h), data)

            # 2. ModernGL's origin is bottom-left, PIL's is top-left.
            # We must flip it vertically so it doesn't display upside down.
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

            # 3. Show it using the default system image viewer
            image.show()

        except Exception as e:
            print(f"Viewer Error: {e}")
            self.reset("Error viweing")


    def on_graph_load(self):
        self.reset()
