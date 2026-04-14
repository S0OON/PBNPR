import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget


class INTERFACE:
    def __init__(self):
        self.running = False
        self.app: QApplication = None
        self.window: QMainWindow = None
        self.tabs: QTabWidget = None
        # self.check_state = None
        # self.render_a_frame = None
        # self.register = None
        # self.unregister = None


cfg = INTERFACE()


def register():
    cfg.app = QApplication(sys.argv)
    if cfg.app:
        cfg.running = True

        cfg.window = QMainWindow()
        cfg.window.setWindowTitle("GL Studio Editor")
        cfg.window.resize(800, 600)

        cfg.tabs = QTabWidget()
        cfg.window.setCentralWidget(cfg.tabs)

        cfg.window.show()
        return
    else:
        print("Failed to create QApplication")
        return


def unregister():
    cfg.running = False


def check_state():
    return cfg.running


def process_frame():
    cfg.app.processEvents()
