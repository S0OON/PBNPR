from gl_studio.ui.pyside6.internals import cfg as CFG
from PySide6 import QtWidgets


def _PreProcess():
    pass


def _Create_shortcuts():
    pass


def _Create_GUI():
    pass


def register():
    Tab = QtWidgets.QWidget()
    CFG.tabs.addTab(Tab, "Template")


def unregister():
    pass


def check_state():
    return True


def process_frame():
    pass
