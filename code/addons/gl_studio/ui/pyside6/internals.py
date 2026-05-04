import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QMenuBar, QMenu , QDockWidget
from PySide6.QtCore import Qt

class Window(QMainWindow):
    menu_bar : QMenuBar
    menu_docks : QMenu

    def __init__(self):
        super().__init__()
        self.setWindowTitle("GL Studio Editor")
        self.resize(1000, 800)

        self.menu_bar = self.menuBar()

        self.menu_docks = self.menu_bar.addMenu("&View")

        self.CentralW = QWidget()
        self.setCentralWidget(self.CentralW)

class INTERFACE:

    app: QApplication
    window: Window

    running = False

cfg = INTERFACE()

# ========= APPLICATION LAYER LEVEL


def _PreProcess():
    pass


def _Create_shortcuts():
    pass


def _Create_GUI():
    pass


def register():
    # init
    cfg.app = QApplication(sys.argv)

    if cfg.app is None:
        print("Failed to create QApplication")
        return

    # start
    cfg.running = True

    cfg.window = Window()
    cfg.window.show()


def unregister():
    cfg.running = False
    cfg.app.shutdown()


def check_state():
    return cfg.running


def process_frame():
    cfg.app.processEvents()
