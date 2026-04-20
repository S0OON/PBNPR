from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QPushButton


class NODE_PRINTER(BASE.NODE_INTERFACE):
    NODE_NAME = "Printer"
    CATEGORY = "Output"

    def on_gui(self):
        self.I_input = self.add_input(type=t.ANY)

        self.btn = QPushButton(text="Execute connections")
        self.btn.clicked.connect(self.on_click)

        return self.btn

    def on_click(self):
        if self not in t.GLOBAL_OUTPUT_NODES:
            t.GLOBAL_OUTPUT_NODES.append(self)

    def on_should_stream(self) -> bool:
        return True

    def on_stream(self):
        self.on_sync_port_values()
        print(f"Printer: {self.I_input.value}")
        self.on_delete()

    def on_sync_port_values(self) -> None:
        data = {}
        i = 0
        for O in self.I_input.connected_ports():
            data.update({f"{i}_{O.node()}": O.value})
            i += 1
        self.I_input.value = data

    def on_graph_save(self):
        self.I_input.value = None

    def on_delete(self):
        for i, j in enumerate(t.GLOBAL_OUTPUT_NODES):
            if j == self:
                t.GLOBAL_OUTPUT_NODES.pop(i)
