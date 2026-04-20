from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QCheckBox, QComboBox, QPushButton, QVBoxLayout, QWidget

STATIC = "Math type"


def add(a, b):
    return a + b


def subtract(a, b):
    return a - b


def multiply(a, b):
    return a * b


def divide(a, b):
    if b == 0:
        return "Error: Division by zero"
    return a / b


ops = {"Add": add, "Subtract": subtract, "Multiply": multiply, "Divide": divide}


class NODE_FLOAT_MATH(BASE.NODE_INTERFACE):
    NODE_NAME = "Math Float"
    CATEGORY = "Float"

    def __init__(self):
        super(NODE_FLOAT_MATH, self).__init__()
        self.I_A = self.add_input("A", type=t.F, default_value=0.0)
        self.I_B = self.add_input("B", type=t.F, default_value=0.0)
        self.O_out = self.add_output("out_data", type=t.F)
        self.reset()

    def on_gui(self):
        self.Combo = QComboBox()
        self.Combo.addItems(ops.keys())
        self.Combo.currentTextChanged.connect(self.reset)
        return self.Combo

    def reset(self):
        self.I_A.value = 0.0
        self.I_B.value = 0.0
        self.O_out.value = 0.0
        if not self.has_property(STATIC):
            self.create_property(STATIC, self.Combo.currentText())

    def on_stream(self):
        self.on_sync_port_values()
        self.O_out.value = ops[self.Combo.currentText()](self.I_A.value, self.I_B.value)
        self.reset()

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        if self.has_property(STATIC):
            if self.get_property(STATIC) is not None:
                self.Combo.setCurrentText(self.get_property(STATIC))
