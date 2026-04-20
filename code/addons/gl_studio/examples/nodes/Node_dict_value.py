from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLineEdit

STATIC = "Value_Dict_Key"


class NODE_VALUE_DICT(BASE.NODE_INTERFACE):
    NODE_NAME = "Value Dict"
    CATEGORY = "Containers"

    def __init__(self):
        super().__init__()
        self.I_val = self.add_input("Value", type=t.ANY)
        self.O_dict = self.add_output("Dict", type=t.DICT)
        self.reset()

    def on_gui(self):
        self.line = QLineEdit()
        self.line.textChanged.connect(lambda v: self.set(STATIC, v))
        return self.line

    def reset(self):
        if not self.has(STATIC):
            self.add(STATIC, self.line.text())
        else:
            self.line.setText(self.get(STATIC))

    def on_stream(self):
        self.on_sync_port_values()
        self.O_dict.val = {self.get(STATIC): self.I_val.val}

    def on_graph_load(self):
        self.reset()
