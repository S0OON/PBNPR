from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QComboBox

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
        self.I_A = self.add_input("A", type=t.F)
        self.I_B = self.add_input("B", type=t.F)
        self.O_out = self.add_output("out_data", type=t.F)
        self.reset()

    def on_gui(self):
        self.Combo = QComboBox()
        self.Combo.addItems(ops.keys())
        self.Combo.currentTextChanged.connect(lambda v: self.set(STATIC, v))
        return self.Combo

    def reset(self):
        if self.has(STATIC):
            self.Combo.setCurrentText(self.get(STATIC))
        else:
            self.add(STATIC, self.Combo.currentText())

    def on_stream(self):
        self.on_sync_port_values()
        self.O_out.val = ops[self.get(STATIC)](self.I_A.val, self.I_B.val)
        self.reset()

    def on_graph_load(self):
        self.reset()
