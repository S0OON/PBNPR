from PySide6.QtWidgets import QWidget, QDockWidget
from PySide6.QtCore import Qt
# ========== SELF LEVEL
from gl_studio.ui.pyside6.internals import cfg as CFG

class INTERFACE:
    label = "Runtime Info"

    dock:  QDockWidget
    widget:QWidget

    def toggle_docker(self):
        self.dock.toggleViewAction()

    def setup_layout(self):
        self.dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.dock.setFeatures(
            QDockWidget.DockWidgetFeature.DockWidgetMovable |
            QDockWidget.DockWidgetFeature.DockWidgetFloatable |
            QDockWidget.DockWidgetFeature.DockWidgetClosable
        )
        self.dock.setWidget(self.widget)
        CFG.window.menu_docks.addAction(self.dock.toggleViewAction())
        CFG.window.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.dock)

cfg = INTERFACE()
# ========== APPLICATION LAYER LEVEL

def _PreProcess():
    pass


def _Create_shortcuts():
    pass


def _Create_GUI():
    cfg.dock = QDockWidget(cfg.label,CFG.window)

    cfg.widget = QWidget()

    cfg.setup_layout()

def register():
    _PreProcess()
    _Create_GUI()
    _Create_shortcuts()


def unregister():
    pass


def check_state():
    return True


def process_frame():
    pass
