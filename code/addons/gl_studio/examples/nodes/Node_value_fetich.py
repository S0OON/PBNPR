
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from gl_studio.util import export_cloud as c
from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget

PRESISTANT = "value_name"


class NODE_CLOUD_FETCH(BASE.NODE_INTERFACE):
    NODE_NAME = "Value Exported"
    CATEGORY = "Global"

    def __init__(self):
        super().__init__()
        self.O_ = self.add_output(type=t.ANY)
        self.reset()

    def on_gui(self):
        widget = QWidget()

        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.line = QLineEdit()
        self.line.textChanged.connect(lambda v: self.set(PRESISTANT, v))
        lay.addWidget(self.line)

        self.status_label = QLabel()
        lay.addWidget(self.status_label)

        return widget

    def reset(self, v=None):
        if self.has(PRESISTANT):
            self.line.setText(self.get(PRESISTANT))
        else:
            self.add(PRESISTANT, self.line.text())

        self.status_label.setText("No Export value")
        self.status_label.setStyleSheet(t.RED)

    def on_stream(self):
        name = self.get(PRESISTANT)
        v = c.EXPORT.get(name,None)
        if v is None:
            self.reset()
        else:
            self.status_label.setText("Recieved")
            self.status_label.setStyleSheet(t.GREEN)
            self.O_.val = v

    def on_graph_load(self):
        self.reset()
