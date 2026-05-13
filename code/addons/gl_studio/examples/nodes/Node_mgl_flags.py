from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QCheckBox, QVBoxLayout, QWidget

class NODE_MGL_FLAGS(BASE.NODE_INTERFACE):
    NODE_NAME = "mgl Flags"
    CATEGORY = "OpenGL"

    def __init__(self):
        super().__init__()
        self.ports = {}
        self.checks = {}



        self.O_flags = self.add_output("Flags", type=t.DICT)
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        # We skip NOTHING as it's a null flag/placeholder
        self.FLAGS_TO_MANAGE = [k for k in t.flag_context_enable.keys() if k != "NOTHING"]

        for flag in self.FLAGS_TO_MANAGE:
            # Add input port for each flag
            self.ports[flag] = self.add_input(flag, type=t.BOOL)

        for flag in self.FLAGS_TO_MANAGE:
            cb = QCheckBox(flag)
            cb.setStyleSheet("color: white;")
            # Map checkbox change to property
            cb.stateChanged.connect(lambda v, f=flag: self.set(f, v > 0))
            lay.addWidget(cb)
            self.checks[flag] = cb

        return widget

    def reset(self, v=None):
        for flag in self.FLAGS_TO_MANAGE:
            val = self.get(flag) if self.has(flag) else False
            if not self.has(flag):
                self.add(flag, False)

            # Sync GUI
            if flag in self.checks:
                self.checks[flag].blockSignals(True)
                self.checks[flag].setChecked(val)
                self.checks[flag].blockSignals(False)

    def on_stream(self):
        self.on_sync_port_values()

        results = {}
        for flag in self.FLAGS_TO_MANAGE:
            # Priority: Port Value (if connected) > GUI Property
            port_val = self.ports[flag].val

            # port_val is None if the port has no connection (and no default was pushed)
            val = port_val if port_val is not None else self.get(flag)
            results[flag] = bool(val)

        self.O_flags.val = results

    def on_graph_load(self):
        self.reset()
