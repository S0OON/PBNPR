import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget, QDoubleSpinBox, QCheckBox

COMPONENTS = "components"
PAD_VAL = "pad_val"

class NODE_NP_ARRAY_EDIT(BASE.NODE_INTERFACE):
    NODE_NAME = "Array Edit (Numpy)"
    CATEGORY = "Containers"

    def __init__(self):
        super().__init__()
        # Ports
        self.I_arr = self.add_input("Array", type=t.RGBA)
        self.O_arr = self.add_output("Array", type=t.RGBA)
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.comp_slider = QDoubleSpinBox()
        self.comp_slider.setRange(0, 4)
        self.comp_slider.setDecimals(0)
        self.comp_slider.setPrefix("Target Channels: ")
        self.comp_slider.valueChanged.connect(lambda v: self.set(COMPONENTS, v))
        lay.addWidget(self.comp_slider)

        self.pad_check = QCheckBox("Pad with 1.0 (Alpha)")
        self.pad_check.stateChanged.connect(lambda v: self.set(PAD_VAL, self.pad_check.isChecked()))
        self.pad_check.setStyleSheet("color: white;")
        lay.addWidget(self.pad_check)

        self.status_label = QLabel()
        self.status_label.setStyleSheet(t.WHITE)
        lay.addWidget(self.status_label)

        return widget

    def reset(self, v=None):
        if self.has(COMPONENTS):
            self.comp_slider.setValue(self.get(COMPONENTS))
        else:
            self.add(COMPONENTS, 4.0)
            self.comp_slider.setValue(4.0)

        if self.has(PAD_VAL):
            self.pad_check.setChecked(self.get(PAD_VAL))
        else:
            self.add(PAD_VAL, True)
            self.pad_check.setChecked(True)

        self.status_label.setText("Ready")

    def on_stream(self):
        self.on_sync_port_values()
        arr = self.I_arr.val
        
        if arr is None:
            self.safe_set_status("Waiting for input...", t.WHITE)
            return

        if not isinstance(arr, np.ndarray):
            try:
                arr = np.array(arr)
            except Exception as e:
                self.safe_set_status("Invalid Input Type", t.RED)
                return

        target_c = int(self.get(COMPONENTS))
        if target_c <= 0:
            self.O_arr.val = arr
            self.safe_set_status(f"Pass-through: {arr.shape}", t.WHITE)
            return

        shape = arr.shape
        # Handle (H, W) -> (H, W, 1)
        if len(shape) == 2:
            h, w = shape
            curr_c = 1
            arr = arr[:, :, np.newaxis]
        elif len(shape) == 3:
            h, w, curr_c = shape
        else:
            self.safe_set_status(f"Unsupported shape: {shape}", t.RED)
            return

        if curr_c == target_c:
            self.O_arr.val = arr
            self.safe_set_status(f"Keep: {arr.shape}", t.GREEN)
            return

        if target_c < curr_c:
            # Slice channels
            result = arr[:, :, :target_c]
        else:
            # Pad channels
            pad_val = 1.0 if self.get(PAD_VAL) else 0.0
            padding_shape = (h, w, target_c - curr_c)
            padding = np.full(padding_shape, pad_val, dtype=arr.dtype)
            result = np.concatenate([arr, padding], axis=2)

        self.O_arr.val = result
        self.safe_set_status(f"Reshaped: {curr_c} -> {target_c} {result.shape}", t.GREEN)

    def on_graph_load(self):
        self.reset()
