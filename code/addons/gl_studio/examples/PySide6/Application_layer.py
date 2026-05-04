from PySide6.QtWidgets import QWidget

# ========== SELF LEVEL
from gl_studio.ui.pyside6.internals import cfg as CFG

class INTERFACE:
    Tab:QWidget = None

cfg = INTERFACE()
# ========== APPLICATION LAYER LEVEL

def _PreProcess():
    pass


def _Create_shortcuts():
    pass


def _Create_GUI():
    cfg.Tab = QWidget()


def register():
    _PreProcess()
    _Create_GUI()
    _Create_shortcuts()
    # crete own tab
    CFG.tabs.addTab(cfg.Tab, "Template")


def unregister():
    pass


def check_state():
    return True


def process_frame():
    pass
