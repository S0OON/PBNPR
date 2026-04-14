from PySide6.QtWidgets import QVBoxLayout,QPushButton,QWidget,QCheckBox
from gl_studio.ui.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t

class NODE_PRINTER(BASE.NODE_INTERFACE):
    NODE_NAME = 'Printer'
    def __init__(self):
        super().__init__()
        self.I_input = self.add_input(type=t.ANY)
        self._Enabled = False
        self._force_crawl = False # Flag for the button click

    def build_ui(self):
        widget = QWidget()
        widget.setMinimumSize(100,100)
        Lay = QVBoxLayout()
        widget.setLayout(Lay)

        self.enabled = QCheckBox()
        self.enabled.clicked.connect(self.on_Enable)
        self.enabled.setText("Enable")
        Lay.addWidget(self.enabled)

        self.btn = QPushButton()
        self.btn.setText('Execute Connections.')
        self.btn.clicked.connect(self.on_btn_click)
        Lay.addWidget(self.btn)

        return widget

    def on_Enable(self): self._Enabled = self.enabled.isChecked()

    def on_btn_click(self): self._force_crawl = True
    
   
    def on_should_crawl(self):
        # Check if button was clicked OR if checkbox is on
        if self._force_crawl:
            self._force_crawl = False # Reset so it doesn't loop
            return True
        return self._Enabled
    
    def on_execute_crawler(self):
        print('Printer: ',self.I_input.value)
