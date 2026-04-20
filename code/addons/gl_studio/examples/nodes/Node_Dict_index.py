from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QComboBox, QVBoxLayout, QWidget


class NODE_DICT_GETTER(BASE.NODE_INTERFACE):
    NODE_NAME = "Dict index"
    CATEGORY = "Containers"

    def __init__(self):
        super(NODE_DICT_GETTER, self).__init__()
        self.I_dict = self.add_input("dictionary", type=t.ANY)
        self.O_val = self.add_output("value", type=t.ANY)
        self.reset()

    def on_gui(self):
        self.combo_keys = QComboBox()
        return self.combo_keys

    def reset(self):
        self.I_dict.value = None
        self.O_val.value = None
        self.combo_keys.clear()

    def on_stream(self):
        self.on_sync_port_values()
        data = self.I_dict.value

        if not isinstance(data, dict):
            print("Not a dict")
            return

        self.combo_keys.clear()
        self.combo_keys.addItems(data.keys())

    def on_graph_save(self):
        self.reset()
