from gl_studio.ui.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6 import QtWidgets


class NODE_FOLAT(BASE.NODE_INTERFACE):
    NODE_NAME = "float"
    CATEGORY = "Float"

    def __init__(self):
        super(NODE_FOLAT, self).__init__()
        self.O_float = self.add_output(type=t.F, default_value=0.0)

    def build_ui(self):
        widget = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout()
        widget.setLayout(lay)

        self.slider = QtWidgets.QDoubleSpinBox()
        self.slider.valueChanged.connect(self.on_change_float)
        lay.addWidget(self.slider)

        return widget

    def on_change_float(self, data):
        self.O_float.value = data
