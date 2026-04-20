from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6 import QtWidgets

STATIC = "Value_Dict_Key"


class NODE_DICT_JOIN(BASE.NODE_INTERFACE):
    NODE_NAME = "Dict join"
    CATEGORY = "Containers"

    def __init__(self):
        super().__init__()
        self.I_dicts = self.add_input("Dicts", type=t.DICT)
        self.O_dict = self.add_output("Dict", type=t.DICT)
        self.reset()

    def on_stream(self):
        self.on_sync_port_values()
        self.O_dict.value = {self.line.text(): self.I_val.value}

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        self.reset()
