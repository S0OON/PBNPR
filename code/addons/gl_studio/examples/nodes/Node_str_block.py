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

STATIC = "file_path_str"
STATIC_BLK = "block_str"


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

        label = QLabel("File Path (Optional):")
        label.setStyleSheet("color: white;")
        lay.addWidget(label)

        lay_H = QHBoxLayout()
        lay.addLayout(lay_H)

        self.ui_filepath = QLineEdit()
        self.ui_filepath.textChanged.connect(
            lambda v: self.set(STATIC, self.ui_filepath.text())
        )
        lay_H.addWidget(self.ui_filepath)

        button = QPushButton(text="...")
        button.clicked.connect(lambda: self.ui_filepath.setText(show_dialog()))
        lay_H.addWidget(button)

        label = QLabel("Direct Text / File Content:")
        label.setStyleSheet("color: white;")
        lay.addWidget(label)

        self.text_block = QPlainTextEdit()
        self.text_block.textChanged.connect(
            lambda: self.set(STATIC_BLK, self.text_block.toPlainText())
        )
        lay.addWidget(self.text_block)

        return widget

    def reset(self):
        if not self.has(STATIC):
            self.add(STATIC, self.ui_filepath.text())
        else:
            self.ui_filepath.setText(self.get(STATIC))

        if not self.has(STATIC_BLK):
            self.add(STATIC_BLK, self.text_block.toPlainText())
        else:
            self.text_block.setPlainText(self.get(STATIC_BLK))

    def on_stream(self):
        filepath = self.ui_filepath.text().strip()

        # 1. Logic: Try to read from file
        if filepath and os.path.exists(filepath):
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()

                # 2. Sync UI: Only update if the content is different
                # (Prevents focus loss and cursor jumping)
                if self.text_block.toPlainText() != file_content:
                    self.text_block.setPlainText(file_content)

                self.O_text.val = file_content

            except Exception as e:
                self.O_text.val = f"// Error reading path file: {e}"
        else:
            # Fallback: Just use what is manually typed in the box
            self.O_text.val = self.text_block.toPlainText()

    def on_graph_load(self):
        self.reset()
