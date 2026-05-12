import bpy
import numpy as np
import os
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget, QCheckBox, QDoubleSpinBox

SOURCE_IMG = "source_img"
FILE_DIR = "file_dir"
FILE_NAME = "file_name"
NAMED_AS = "named_as"
FLIP_V = "flip_v"
COMPONENTS = "components"

class NODE_IMG_SAVE(BASE.NODE_INTERFACE):
    NODE_NAME = "Image Save"
    CATEGORY = "Blender"

    def __init__(self):
        super().__init__()
        # Inputs
        self.I_name = self.add_input("Name", type=t.STR)
        self.I_pixels = self.add_input("Pixels", type=t.RGBA)
        self.I_w = self.add_input("Width", type=t.F)
        self.I_h = self.add_input("Height", type=t.F)
        self.I_channels = self.add_input("Channels", type=t.F)
        self.I_pkg = self.add_input("Pkg", type=t.DICT)

        # Outputs
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

        self.line_dir = QLineEdit()
        self.line_dir.setPlaceholderText("Directory (e.g. C:/renders/)")
        self.line_dir.textChanged.connect(lambda v: self.set(FILE_DIR, v))
        lay.addWidget(self.line_dir)

        self.line_name = QLineEdit()
        self.line_name.setPlaceholderText("Filename (if Name port empty)")
        self.line_name.textChanged.connect(lambda v: self.set(FILE_NAME, v))
        lay.addWidget(self.line_name)

        self.line_img = QLineEdit()
        self.line_img.setPlaceholderText("Source: Render Result")
        self.line_img.textChanged.connect(lambda v: self.set(SOURCE_IMG, v))
        lay.addWidget(self.line_img)

        self.line_named = QLineEdit()
        self.line_named.setPlaceholderText("Output Key (Optional)...")
        self.line_named.textChanged.connect(lambda v: self.set(NAMED_AS, v))
        lay.addWidget(self.line_named)

        self.comp_slider = QDoubleSpinBox()
        self.comp_slider.setRange(0, 4)
        self.comp_slider.setDecimals(0)
        self.comp_slider.setPrefix("Force Components: ")
        self.comp_slider.valueChanged.connect(lambda v: self.set(COMPONENTS, v))
        lay.addWidget(self.comp_slider)

        self.flip_check = QCheckBox("Flip Vertical")
        self.flip_check.stateChanged.connect(lambda v: self.set(FLIP_V, self.flip_check.isChecked()))
        self.flip_check.setStyleSheet("color: white;")
        lay.addWidget(self.flip_check)

        self.status_label = QLabel()
        lay.addWidget(self.status_label)

        return widget

    def reset(self, v=None):
        if self.has(FILE_DIR):
            self.line_dir.setText(self.get(FILE_DIR))
        else:
            self.add(FILE_DIR, "C:/renders/")
            self.line_dir.setText("C:/renders/")

        if self.has(FILE_NAME):
            self.line_name.setText(self.get(FILE_NAME))
        else:
            self.add(FILE_NAME, "render.png")
            self.line_name.setText("render.png")

        if self.has(SOURCE_IMG):
            self.line_img.setText(self.get(SOURCE_IMG))
        else:
            self.add(SOURCE_IMG, "Render Result")
            self.line_img.setText("Render Result")

        if self.has(NAMED_AS):
            self.line_named.setText(self.get(NAMED_AS))
        else:
            self.add(NAMED_AS, "")

        if self.has(COMPONENTS):
            self.comp_slider.setValue(self.get(COMPONENTS))
        else:
            self.add(COMPONENTS, 0.0)

        if self.has(FLIP_V):
            self.flip_check.setChecked(self.get(FLIP_V))
        else:
            self.add(FLIP_V, False)

        self.status_label.setText("Ready")
        self.status_label.setStyleSheet(t.WHITE)

    def on_stream(self):
        self.on_sync_port_values()
        
        # Determine Directory and Filename
        directory = self.get(FILE_DIR)
        filename = self.I_name.val if self.I_name.val is not None and self.I_name.val != "" else self.get(FILE_NAME)
        
        if not directory or not filename:
            self.safe_set_status("Path components missing", t.RED)
            return

        # Ensure directory ends with slash for join
        if not (directory.endswith("/") or directory.endswith("\\")):
            directory += "/"

        # Combine and sanitize path
        abs_path = os.path.join(directory, filename)
        abs_path = os.path.abspath(bpy.path.abspath(abs_path))
        
        img_name = self.get(SOURCE_IMG)
        img = bpy.data.images.get(img_name)

        if not img:
            self.safe_set_status(f"Missing Source: {img_name}", t.RED)
            return

        try:
            # 1. Prepare Directory
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)

            # 2. Save Logic
            # Note: Blender's save methods overwrite by default if the path is the same.
            if img.type == 'RENDER_RESULT':
                img.save_render(abs_path)
            else:
                img.filepath_raw = abs_path
                img.save()

            # 3. Data Extraction (FROM DISK using PIL)
            from PIL import Image

            if not os.path.exists(abs_path):
                self.safe_set_status("File not found after save", t.RED)
                return

            with Image.open(abs_path) as pil_img:
                w, h = pil_img.size
                result = np.array(pil_img, dtype=np.float32) / 255.0

                if result.ndim == 2:
                    result = result[:, :, np.newaxis]

                img_channels = result.shape[2]

            target_channels = int(self.get(COMPONENTS))
            if target_channels <= 0:
                target_channels = img_channels

            # Component Adjustment
            if target_channels != img_channels:
                if target_channels < img_channels:
                    result = result[:, :, :target_channels]
                else:
                    # Pad with 1.0 (Alpha/White)
                    padding_shape = (h, w, target_channels - img_channels)
                    padding = np.ones(padding_shape, dtype=np.float32)
                    result = np.concatenate([result, padding], axis=2)

            if self.get(FLIP_V):
                result = np.flipud(result)

            # Dictionary Key
            pkg_key = self.line_named.text() if self.line_named.text() else img_name

            # Set outputs from verified disk data
            self.O_pixels.val = result
            self.O_w.val = float(w)
            self.O_h.val = float(h)
            self.O_Channels.val = float(target_channels)
            self.O_pkg.val = {pkg_key: result}

            self.safe_set_status(f"File Saved & Verified: {os.path.basename(abs_path)}", t.GREEN)

        except Exception as e:
            self.safe_set_status(f"Error: {str(e)}", t.RED)

    def on_graph_load(self):
        self.reset()
