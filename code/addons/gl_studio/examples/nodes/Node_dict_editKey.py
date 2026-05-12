from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLineEdit, QVBoxLayout, QWidget, QLabel

TARGET_KEY = "target_key"
NEW_KEY = "new_key"

class NODE_DICT_EDIT_KEY(BASE.NODE_INTERFACE):
    NODE_NAME = "Dict Edit Key"
    CATEGORY = "Containers"

    def __init__(self):
        super().__init__()
        self.I_dict = self.add_input("Dict", type=t.DICT)
        self.O_dict = self.add_output("Dict", type=t.DICT)
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.line_target = QLineEdit()
        self.line_target.setPlaceholderText("Target Key (to change)...")
        self.line_target.textChanged.connect(lambda v: self.set(TARGET_KEY, v))
        lay.addWidget(self.line_target)

        self.line_new = QLineEdit()
        self.line_new.setPlaceholderText("New Key Name...")
        self.line_new.textChanged.connect(lambda v: self.set(NEW_KEY, v))
        lay.addWidget(self.line_new)

        self.status = QLabel("Ready")
        lay.addWidget(self.status)

        return widget

    def reset(self):
        if self.has(TARGET_KEY):
            self.line_target.setText(self.get(TARGET_KEY))
        else:
            self.add(TARGET_KEY, "")

        if self.has(NEW_KEY):
            self.line_new.setText(self.get(NEW_KEY))
        else:
            self.add(NEW_KEY, "")

    def on_stream(self):
        self.on_sync_port_values()
        
        in_dict = self.I_dict.val
        if not isinstance(in_dict, dict):
            self.O_dict.val = {}
            self.status.setText("Input is not a Dict")
            return

        target = self.get(TARGET_KEY)
        new_name = self.get(NEW_KEY)

        if not new_name:
            self.O_dict.val = in_dict
            self.status.setText("New Key is empty")
            return

        # Create a new dict with the renamed key
        out_dict = {}
        found = False

        # Logic: 
        # 1. If 'target' is specified, only rename that one.
        # 2. If 'target' is empty AND dict has only 1 key, rename that 1 key.
        
        keys = list(in_dict.keys())
        
        if not target and len(keys) == 1:
            out_dict[new_name] = in_dict[keys[0]]
            found = True
        else:
            for k, v in in_dict.items():
                if k == target:
                    out_dict[new_name] = v
                    found = True
                else:
                    out_dict[k] = v

        self.O_dict.val = out_dict
        
        if found:
            self.status.setText(f"Renamed to '{new_name}'")
        else:
            self.status.setText(f"Key '{target}' not found")

    def on_graph_load(self):
        self.reset()
