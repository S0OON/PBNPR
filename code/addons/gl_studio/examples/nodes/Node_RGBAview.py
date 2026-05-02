import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PIL import Image
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


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


    def on_view_clicked(self):
        data = self.I_rgba.val  # This is now an np.array

        # 1. Validation check for numpy arrays
        if data is None or data.size == 0:
            self.reset("No data to view!")
            return

        try:
            # Convert float32 (0.0-1.0) to uint8 (0-255)
            A_viz = (data * 255).clip(0, 255).astype(np.uint8)

            # Create the PIL image
            image = Image.fromarray(A_viz)

            # Properly assign the flipped image to a variable
            flipped_image = image.transpose(Image.FLIP_TOP_BOTTOM)

            # 4. Display only the flipped image
            flipped_image.show()

        except Exception as e:
            self.reset(f"Error viewing image: {e}")


    def on_graph_load(self):
        self.reset()
