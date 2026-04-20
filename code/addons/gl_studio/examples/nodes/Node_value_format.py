from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6 import QtWidgets

STATIC = "Value_format_Key"


class NODE_VALUE_FORMAT(BASE.NODE_INTERFACE):
    NODE_NAME = "Format value"
    CATEGORY = "Containers"

    def __init__(self):
        super().__init__()
        self.I_val = self.add_input("Value", type=t.ANY)
        self.O_frmt = self.add_output("frmt", type=t.ANY)
        self.reset()

    def on_gui(self):
        self.line = QtWidgets.QLineEdit()
        self.line.textChanged.connect(lambda v: self.set(STATIC, v))
        return self.line

    def reset(self):
        if not self.has(STATIC):
            self.add(STATIC, self.line.text())
        else:
            self.line.setText(self.get(STATIC))

    def on_stream(self):
        self.on_sync_port_values()
        self.O_frmt.val = t.formated_data(data=self.I_val.val, fmt=self.line.text())

    def on_graph_load(self):
        self.reset()
