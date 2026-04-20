import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PIL import Image, ImageOps
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class NODE_RGBA_VIEWER(BASE.NODE_INTERFACE):
    NODE_NAME = "RGBA Viewer"
    CATEGORY = "Output"

    def __init__(self):
        super().__init__()

        # Inputs
        self.I_rgba = self.add_input("rgba_data", type=t.ANY)
        self.I_width = self.add_input("width", type=t.F)
        self.I_height = self.add_input("height", type=t.F)

        # Default resolutions
        self.I_width.val = t.RES_W
        self.I_height.val = t.RES_H

        # Output (Pass-through)
        self.O_rgba = self.add_output("rgba_data", type=t.ANY)
        self.O_mock = self.add_output("Mock output", type=t.NONE)

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        lay.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(lay)

        self.status_label = QLabel("Status: No Data")
        self.status_label.setStyleSheet("color: #AAA;")
        lay.addWidget(self.status_label)

        btn_view = QPushButton("View Image (PIL)")
        btn_view.setStyleSheet(
            "background-color: #2b5c8f; color: white; font-weight: bold; padding: 5px;"
        )
        btn_view.clicked.connect(self.on_view_clicked)
        lay.addWidget(btn_view)

        return widget

    def on_stream(self):
        self.on_sync_port_values()
        # 1. Grab data
        self.current_data = self.I_rgba.val

        # 2. Pass it directly to output
        self.O_rgba.val = self.current_data

        # 3. Update UI
        if self.current_data is not None:
            self.status_label.setText("Status: Data Ready")
            self.status_label.setStyleSheet("color: #55FF55;")
        else:
            self.status_label.setText("Status: No Data")
            self.status_label.setStyleSheet("color: #AAA;")

    def on_view_clicked(self):
        data = self.I_rgba.val

        # Safer check: 'not any(data)' can throw errors on large byte arrays or numpy arrays
        if not data:
            print("No data to view!")
            return

        try:
            w = int(self.I_width.val)
            h = int(self.I_height.val)

            # 1. Feed the raw fbo.read() bytes directly into PIL.
            # PIL expects size as a tuple (w, h).
            # "RGB" matches components=3.
            image = Image.frombytes("RGB", (w, h), data)

            # 2. ModernGL's origin is bottom-left, PIL's is top-left.
            # We must flip it vertically so it doesn't display upside down.
            image = image.transpose(Image.FLIP_TOP_BOTTOM)

            # 3. Show it using the default system image viewer
            image.show()

        except Exception as e:
            print(f"Viewer Error: {e}")

    def reset(self):
        self.I_rgba.val = None
        self.O_rgba.val = None

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        self.reset()
