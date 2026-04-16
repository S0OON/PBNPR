import os

from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

STATIC = "ui_file_path"


class NODE_TEXT_BLOCK(BASE.NODE_INTERFACE):
    NODE_NAME = "Text Block"
    CATEGORY = "String"

    def __init__(self):
        super().__init__()
        self.O_text = self.add_output("Text", type=t.STR)
        self.text_field_pacing = 0
        self.reset()

    def build_ui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        lay.addWidget(QLabel("File Path (Optional):"))
        self.ui_filepath = QLineEdit()
        lay.addWidget(self.ui_filepath)

        lay.addWidget(QLabel("Direct Text / File Content:"))

        layH = QHBoxLayout()
        lay.addLayout(layH)

        btn_size = QPushButton(text="+")
        btn_size.clicked.connect(self.on_size)
        layH.addWidget(btn_size)

        btn_desize = QPushButton(text="-")
        btn_desize.clicked.connect(self.on_desize)
        layH.addWidget(btn_desize)

        self.spinbox_pacing = QSpinBox()
        self.spinbox_pacing.valueChanged.connect(self.on_change_spin)
        layH.addWidget(self.spinbox_pacing)

        self.ui_text = QPlainTextEdit()
        lay.addWidget(self.ui_text)

        # This tells the text box to take up as much space as possible
        self.ui_text.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )

        return widget

    def on_change_spin(self, data):
        self.text_field_pacing = data

    def on_size(self):
        spacing = self.text_field_pacing
        size = self.ui_text.size()
        self.ui_text.resize(size.width() + spacing, size.height() + spacing)

    def on_desize(self):
        size = self.ui_text.size()
        spacing = self.text_field_pacing
        self.ui_text.resize(size.width() - spacing, size.height() - spacing)

    def on_execute_crawler(self):
        filepath = self.ui_filepath.text().strip()

        # 1. Logic: Try to read from file
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()

                # 2. Sync UI: Only update if the content is different
                # (Prevents focus loss and cursor jumping)
                if self.ui_text.toPlainText() != file_content:
                    self.ui_text.setPlainText(file_content)

                self.O_text.value = file_content

            except Exception as e:
                self.O_text.value = f"// Error: {e}"
        else:
            # Fallback: Just use what is manually typed in the box
            self.O_text.value = self.ui_text.toPlainText()

    def reset(self):
        if not self.has_property(STATIC):
            self.create_property(STATIC, self.ui_filepath.text())
        else:
            self.ui_filepath.setText(self.get_property(STATIC))

    def on_graph_load(self):
        self.reset()
