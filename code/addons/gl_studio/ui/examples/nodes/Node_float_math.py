from gl_studio.ui.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QCheckBox, QComboBox, QPushButton, QVBoxLayout, QWidget


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
    NODE_NAME = "Float Math"

    def __init__(self):
        super(NODE_FLOAT_MATH, self).__init__()
        self.I_A = self.add_input("A", type=t.F)
        self.I_B = self.add_input("B", type=t.F)
        self.O_out = self.add_output("out_data", type=t.F)

    def build_ui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.combo_types = QComboBox()
        self.combo_types.addItems(ops.keys())
        lay.addWidget(self.combo_types)

        return widget

    def on_execute_crawler(self):
        self.O_out.value = ops[self.combo_types.currentText()](
            self.I_A.value, self.I_B.value
        )
