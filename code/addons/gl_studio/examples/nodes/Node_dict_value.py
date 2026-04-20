from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6 import QtWidgets

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
        self.line = QtWidgets.QLineEdit()
        self.line.textChanged.connect(self.on_text_change)
        return self.line

    def on_text_change(self, data):
        self.reset()

    def reset(self):
        if not self.has_property(STATIC):
            self.create_property(STATIC, self.line.text())
        else:
            self.set_property(STATIC, self.line.text())

    def on_stream(self):
        self.on_sync_port_values()
        self.O_dict.value = {self.line.text(): self.I_val.value}

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        self.line.setText(self.get_property(STATIC))
