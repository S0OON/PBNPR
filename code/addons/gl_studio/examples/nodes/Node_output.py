import time
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QCheckBox, QSlider, QLabel
from PySide6.QtCore import Qt

class NODE_PULSE(BASE.NODE_INTERFACE):
    NODE_NAME = "Pulse"
    CATEGORY = "Output"

    is_active = False
    should_print = True
    interval_seconds = 1.0
    last_exec_time = 0.0

    def __init__(self):
        super().__init__()
        self.I_input = self.add_input(type=t.ANY)


    def on_gui(self):
        # Create a layout container
        self.widget = QWidget()
        self.widget.setStyleSheet("color: white;")
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget.setLayout(layout)

        # 1. Checkbox for 'Print Output'
        self.cb_print = QCheckBox("Print Output")
        self.cb_print.setChecked(self.should_print)
        self.cb_print.toggled.connect(self.on_print_toggled)
        layout.addWidget(self.cb_print)

        # 1. Button for Manual Print
        self.btn_manual = QPushButton("Manual Print")
        self.btn_manual.setStyleSheet("color: black;")
        self.btn_manual.clicked.connect(self.on_manual_click)
        layout.addWidget(self.btn_manual)

        # 2. Checkbox for 'Active' (keeps it in GLOBAL_OUTPUT_NODES)
        self.cb_active = QCheckBox("Active")
        self.cb_active.setChecked(self.is_active)
        self.cb_active.toggled.connect(self.on_active_toggled)
        layout.addWidget(self.cb_active)

        # 3. Intervals Slider
        self.lbl_slider = QLabel(f"Interval: {self.interval_seconds:.1f}s")
        layout.addWidget(self.lbl_slider)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setMinimum(1)   # 0.1s minimum
        self.slider.setMaximum(100) # 10.0s maximum
        self.slider.setValue(int(self.interval_seconds * 10))
        self.slider.valueChanged.connect(self.on_slider_changed)
        layout.addWidget(self.slider)

        return self.widget

    # --- UI Callbacks ---
    def on_print_toggled(self, checked):
        self.should_print = checked

    def on_active_toggled(self, checked):
        self.is_active = checked
        if self.is_active:
            # Register to the execution engine loop
            if self not in t.GLOBAL_OUTPUT_NODES:
                t.GLOBAL_OUTPUT_NODES.append(self)
        else:
            # Remove from loop
            self.reset()

    def on_slider_changed(self, value):
        self.interval_seconds = value / 10.0
        self.lbl_slider.setText(f"Interval: {self.interval_seconds:.1f}s")

    def on_manual_click(self):
        # Force one-time execution by adding it to globals temporarily
        if self not in t.GLOBAL_OUTPUT_NODES:
            t.GLOBAL_OUTPUT_NODES.append(self)

    # --- Node Logic ---
    def reset(self):
        # Important: only pop from GLOBAL_OUTPUT_NODES if the node is NOT active.
        if not self.is_active:
            for i, j in enumerate(t.GLOBAL_OUTPUT_NODES):
                if j == self:
                    t.GLOBAL_OUTPUT_NODES.pop(i)
                    break

    def on_should_stream(self) -> bool:
        # Manual trigger
        if not self.is_active:
            return True

        # Interval check for active streaming
        current_time = time.time()
        if current_time - self.last_exec_time >= self.interval_seconds:
            self.last_exec_time = current_time
            return True

        return False

    def on_stream(self):
        self.on_sync_port_values()

        # Only print if the checkbox is checked
        if self.should_print:
            print(f"Pulse: {self.I_input.val}")

        # Cleanup routine (Will keep it in t.GLOBAL_OUTPUT_NODES if active, pop if manual trigger)
        self.reset()

    def on_sync_port_values(self) -> None:
        data = []
        for sender in self.I_input.connected_ports():
            data.append(sender.val)

        self.I_input.val = data
