from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6 import QtWidgets


class NODE_STRING(BASE.NODE_INTERFACE):
    NODE_NAME = "String"
    CATEGORY = "String"

    def __init__(self):
        super().__init__()
        self.O_text = self.add_output(type=t.STR, default_value="helloWorld")
        self.reset()

    def build_ui(self):
        self.line = QtWidgets.QLineEdit()
        self.line.textChanged.connect(self.on_text_change)

        return self.line

    def on_text_change(self, data):
        self.O_text.value = data

    def reset(self):
        self.line.setText(self.O_text.value)

    def on_graph_load(self):
        self.reset()
