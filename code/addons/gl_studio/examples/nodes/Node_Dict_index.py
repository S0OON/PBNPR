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

        self._last_keys = []  # Internal storage to track the last seen dict keys

    def build_ui(self):
        self.combo_keys = QComboBox()
        return self.combo_keys

    def on_execute_crawler(self):
        input_dict = self.I_dict.value

        if not isinstance(input_dict, dict):
            self.O_val.value = None
            return

        current_keys = list(input_dict.keys())
        if current_keys != self._last_keys:
            self.combo_keys.clear()
            self.combo_keys.addItems([str(k) for k in current_keys])
            self._last_keys = current_keys

        selected_key = self.combo_keys.currentText()
        if selected_key in input_dict:
            self.O_val.value = input_dict[selected_key]
        else:
            for k, v in input_dict.items():
                if str(k) == selected_key:
                    self.O_val.value = v
                    break
