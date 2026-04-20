from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)


class NODE_IO_DYNAMIC(BASE.NODE_INTERFACE):
    NODE_NAME = "Dynamic IO"
    CATEGORY = "Containers"

    def __init__(self):
        super().__init__()
        self.O_dict = self.add_output("output_dir", type=t.DICT)
        # Dictionary to keep track of {port_object: QLineEdit_widget}
        self.port_name_map = {}
        self.set_port_deletion_allowed(True)

    def build_ui(self):
        self.main_widget = QWidget()
        self.main_lay = QVBoxLayout()
        self.main_widget.setLayout(self.main_lay)

        # --- Control Layout (+ / - / Index) ---
        ctrl_lay = QHBoxLayout()

        self.btn_add = QPushButton("+")
        self.btn_add.setFixedSize(30, 30)
        self.btn_add.setStyleSheet("background-color: #2e7d32; font-weight: bold;")
        self.btn_add.clicked.connect(self.on_add_port)

        self.btn_rem = QPushButton("-")
        self.btn_rem.setFixedSize(30, 30)
        self.btn_rem.setStyleSheet("background-color: #c62828; font-weight: bold;")
        self.btn_rem.clicked.connect(self.on_remove_port)

        self.index_spin = QSpinBox()
        self.index_spin.setMinimum(0)
        self.index_spin.setToolTip("Index to remove")
        self.index_spin.setStyleSheet("background: #222; color: #FFF;")

        ctrl_lay.addWidget(self.btn_add)
        ctrl_lay.addWidget(self.index_spin)
        ctrl_lay.addWidget(self.btn_rem)
        self.main_lay.addLayout(ctrl_lay)

        # --- Container for Name Fields ---
        self.names_container = QVBoxLayout()
        self.main_lay.addLayout(self.names_container)

        return self.main_widget

    def on_add_port(self):
        # 1. Create unique internal ID for the port
        idx = len(self.inputs())
        port_id = f"in_{idx}"

        # 2. Add the physical port
        new_port = self.add_input(port_id, type=t.ANY, display_name=False)

        # 3. Add the corresponding Text Field to UI
        name_edit = QLineEdit()
        name_edit.setPlaceholderText(f"Key Name {idx}")
        name_edit.setStyleSheet(
            "background: #1a1a1a; color: #00ff00; border-bottom: 1px solid #444;"
        )

        self.names_container.addWidget(name_edit)
        self.port_name_map[new_port] = name_edit

        # Update spinbox range
        self.index_spin.setMaximum(len(self.inputs()) - 1)
        self.update()

    def on_remove_port(self):
        idx = self.index_spin.value()
        input_ports = list(self.inputs().values())

        if 0 <= idx < len(input_ports):
            target_port = input_ports[idx]

            # Remove UI Widget
            widget_to_delete = self.port_name_map[target_port]
            self.names_container.removeWidget(widget_to_delete)
            widget_to_delete.deleteLater()

            # Cleanup mappings and delete actual port
            del self.port_name_map[target_port]
            self.delete_input(target_port)

            # Update spinbox range
            new_max = max(0, len(self.inputs()) - 1)
            self.index_spin.setMaximum(new_max)
            self.update()

    def on_execute_crawler(self):
        """Builds dictionary using the text fields as Keys and port values as Values."""
        result = {}
        for port, line_edit in self.port_name_map.items():
            key_name = line_edit.text().strip()

            # Fallback to port name if user left the text field empty
            if not key_name:
                key_name = port.name()

            result[key_name] = port.value

        self.O_dict.value = result
