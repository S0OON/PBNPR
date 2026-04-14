from PySide6 import QtWidgets
from gl_studio.ui.pyside6.internals import cfg as CFG

def register():
    placeholder = QtWidgets.QWidget()
    CFG.tabs.addTab(placeholder, "Settings")

def unregister(): pass

def check_state():
    return True

def process_frame():pass