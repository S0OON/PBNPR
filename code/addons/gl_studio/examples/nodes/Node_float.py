from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QDoubleSpinBox

PRESISTANT = "saved_float_value"


class NODE_FOLAT(BASE.NODE_INTERFACE):
    NODE_NAME = "float"
    CATEGORY = "Float"

    def __init__(self):
        super().__init__()
        self.O_float = self.add_output(name="Float", type=t.F)
        self.reset()

    def on_gui(self):
        self.slider = QDoubleSpinBox()
        self.slider.setRange(-9999, 9999)
        self.slider.valueChanged.connect(
            lambda v: self.set(PRESISTANT, self.slider.value())
        )
        return self.slider

    def reset(self, v=None):
        if self.has(PRESISTANT):
            self.slider.setValue(self.get(PRESISTANT))
        else:
            self.add(PRESISTANT, self.slider.value())

    def on_stream(self):
        self.O_float.val = self.get(PRESISTANT)

    def on_graph_load(self):
        self.reset()
