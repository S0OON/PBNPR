from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QDoubleSpinBox


class NODE_FOLAT(BASE.NODE_INTERFACE):
    NODE_NAME = "float"
    CATEGORY = "Float"

    def __init__(self):
        super().__init__()
        self.O_float = self.add_output(name="float out", type=t.F, default_value=5.0)
        self.reset()

    def build_ui(self):
        self.slider = QDoubleSpinBox()
        self.slider.setRange(-9999, 9999)
        self.slider.valueChanged.connect(self.on_ui_change)

        return self.slider

    def on_ui_change(self, v):
        self.O_float.value = v

    def reset(self):
        self.slider.setValue(self.O_float.value)

    def on_graph_load(self):
        self.reset()
