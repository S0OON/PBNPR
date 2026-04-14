from gl_studio.ui.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6 import QtWidgets


class NODE_STRING(BASE.NODE_INTERFACE):
    NODE_NAME = "String"
    CATEGORY = "Str"

    def __init__(self):
        super(NODE_STRING, self).__init__()
        self.O_text = self.add_output(type=t.STR, default_value="helloWorld")

    def build_ui(self):
        widget = QtWidgets.QWidget()
        lay = QtWidgets.QVBoxLayout()
        widget.setLayout(lay)

        self.line = QtWidgets.QLineEdit()
        self.line.textChanged.connect(self.on_text_change)
        lay.addWidget(self.line)

        return widget

    def on_text_change(self, data):
        self.O_text.value = data
