from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QLineEdit, QPlainTextEdit, QVBoxLayout, QWidget


class NODE_STRING_COMBINE(BASE.NODE_INTERFACE):
    NODE_NAME = "Combine Strings"
    CATEGORY = "String"

    def __init__(self):
        super().__init__()
        # Two string inputs
        self.I_A = self.add_input("A", type=t.STR)
        self.I_B = self.add_input("B", type=t.STR)

        # One string output
        self.O_out = self.add_output("Out", type=t.STR)

    def on_execute_crawler(self):
        # Grab values, defaulting to empty strings if nothing is connected
        val_a = str(self.I_A.value) if self.I_A.value else ""
        val_b = str(self.I_B.value) if self.I_B.value else ""

        # Combine A and B with a line break to keep the code clean
        self.O_out.value = f"{val_a}{val_b}"
