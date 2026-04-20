from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QPushButton


class NODE_PRINTER(BASE.NODE_INTERFACE):
    NODE_NAME = "Printer"
    CATEGORY = "Output"

    def __init__(self):
        super().__init__()
        self.I_input = self.add_input(type=t.ANY)

    def on_gui(self):
        self.btn = QPushButton(text="Evaluate Node Tree")
        self.btn.clicked.connect(self.on_click)
        return self.btn

    def on_click(self):
        if self not in t.GLOBAL_OUTPUT_NODES:
            t.GLOBAL_OUTPUT_NODES.append(self)

    def reset(self):
        for i, j in enumerate(t.GLOBAL_OUTPUT_NODES):
            if j == self:
                t.GLOBAL_OUTPUT_NODES.pop(i)

    def on_should_stream(self) -> bool:
        return True

    def on_stream(self):
        self.on_sync_port_values()
        print(f"Printer: {self.I_input.val}")
        self.reset()

    def on_sync_port_values(self) -> None:
        data = []
        for sender in self.I_input.connected_ports():
            data.append(sender.val)

        self.I_input.val = data
