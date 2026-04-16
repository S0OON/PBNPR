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
        self.I_width.value = 512.0
        self.I_height.value = 512.0

        # Output (Pass-through)
        self.O_rgba = self.add_output("rgba_data", type=t.ANY)

        # Internal state
        self.current_data = None

    def build_ui(self):
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

    def on_execute_crawler(self):
        # 1. Grab data
        self.current_data = self.I_rgba.value

        # 2. Pass it directly to output
        self.O_rgba.value = self.current_data

        # 3. Update UI
        if self.current_data is not None:
            self.status_label.setText("Status: Data Ready")
            self.status_label.setStyleSheet("color: #55FF55;")
        else:
            self.status_label.setText("Status: No Data")
            self.status_label.setStyleSheet("color: #AAA;")

    def on_view_clicked(self):
        data = self.current_data

        if data is None:
            print("No data to view! Run the graph first.")
            return

        try:
            # Smart Check 1: If user plugged in the whole render_maps dict, grab 'combined'
            if isinstance(data, dict) and "combined" in data:
                data = data["combined"]

            if not isinstance(data, np.ndarray):
                print(f"Cannot view data of type: {type(data)}")
                return

            # Smart Check 2: Convert float32 [0.0 - 1.0] to uint8 [0 - 255]
            if data.dtype == np.float32 or data.dtype == np.float64:
                img_data = (np.clip(data, 0.0, 1.0) * 255).astype(np.uint8)
            else:
                img_data = data.astype(np.uint8)

            w = int(self.I_width.value)
            h = int(self.I_height.value)

            # Smart Check 3: Reshape if it's a flat array
            if len(img_data.shape) == 1:
                # PIL expects (Height, Width, Channels)
                img_data = img_data.reshape((h, w, 4))

            # Create PIL Image
            img = Image.fromarray(img_data, "RGBA")

            # Smart Check 4: OpenGL renders bottom-up. Flip it so it looks right.
            img = ImageOps.flip(img)

            # Show the image using the default OS image viewer
            img.show()

        except Exception as e:
            print(f"Viewer Error: {e}")
