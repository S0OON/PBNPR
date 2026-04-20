import os

from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPlainTextEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

STATIC = "ui_file_path"


def show_dialog():
    a, b = QFileDialog.getOpenFileName(
        None, "Open File", "", "All Files (*);;Text Files (*.txt)"
    )
    return a


class NODE_TEXT_BLOCK(BASE.NODE_INTERFACE):
    NODE_NAME = "Text Block"
    CATEGORY = "String"

    def __init__(self):
        super().__init__()
        self.O_text = self.add_output("Text", type=t.STR)
        self.reset()

    def on_gui(self):
        widget = QWidget()

        lay = QVBoxLayout()
        widget.setLayout(lay)

        lay.addWidget(QLabel("File Path (Optional):"))

        lay_H = QHBoxLayout()
        lay.addLayout(lay_H)

        self.ui_filepath = QLineEdit()
        self.ui_filepath.textChanged.connect(self.on_line_change)
        lay_H.addWidget(self.ui_filepath)

        button = QPushButton(text="...")
        button.clicked.connect(self.on_click)
        lay_H.addWidget(button)

        lay.addWidget(QLabel("Direct Text / File Content:"))

        self.ui_text = QPlainTextEdit()
        lay.addWidget(self.ui_text)

        return widget

    def on_click(self):
        self.ui_filepath.setText(show_dialog())

    def on_line_change(self, text):
        if not self.has_property(STATIC):
            self.create_property(STATIC, text)
        else:
            self.set_property(STATIC, text)

    def reset(self):
        if not self.has_property(STATIC):
            self.create_property(STATIC, self.ui_filepath.text())
        else:
            self.ui_filepath.setText(self.get_property(STATIC))

    def on_stream(self):
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
                self.O_text.value = f"// Error reading path file: {e}"
        else:
            # Fallback: Just use what is manually typed in the box
            self.O_text.value = self.ui_text.toPlainText()

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        self.reset()
