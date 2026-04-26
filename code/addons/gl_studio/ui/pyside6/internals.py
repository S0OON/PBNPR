import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget


class INTERFACE:
    def __init__(self):
        self.running = False

        self.app: QApplication = None

        self.window: QMainWindow = None
        self.tabs: QTabWidget = None


class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GL Studio Editor")
        self.resize(1000, 800)
        self.Tabs = QTabWidget()
        self.setCentralWidget(self.Tabs)


cfg = INTERFACE()


def _PreProcess():
    pass


def _Create_shortcuts():
    pass


def _Create_GUI():
    pass


def register():
    # init
    cfg.app = QApplication(sys.argv)

    if cfg.app == None:
        print("Failed to create QApplication")
        return

    # start
    cfg.running = True

    cfg.window = Window()

    cfg.tabs = cfg.window.Tabs

    cfg.window.show()


def unregister():
    cfg.running = False


def check_state():
    return cfg.running


def process_frame():
    cfg.app.processEvents()
