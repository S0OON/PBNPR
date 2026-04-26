from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLineEdit

PRESISTANT = "saved_str_value"


class NODE_STRING(BASE.NODE_INTERFACE):
    NODE_NAME = "String"
    CATEGORY = "String"

    def __init__(self):
        super().__init__()
        self.O_str = self.add_output(name="String", type=t.STR)
        self.reset()

    def on_gui(self):
        self.line = QLineEdit()
        self.line.textChanged.connect(lambda v: self.set(PRESISTANT, v))
        return self.line

    def reset(self, v=None):
        if self.has(PRESISTANT):
            self.line.setText(self.get(PRESISTANT))
        else:
            self.add(PRESISTANT, self.line.text())

    def on_stream(self):
        self.O_str.val = self.get(PRESISTANT)

    def on_graph_load(self):
        self.reset()
