from PySide6 import QtWidgets
import sys

class INTERFACE:
    def __init__(self):
        self.running = False
        self.app : QtWidgets.QApplication = None
        self.window : QtWidgets.QMainWindow = None
        self.tabs : QtWidgets.QTabWidget = None
        #self.check_state = None
        #self.render_a_frame = None
        #self.register = None
        #self.unregister = None

cfg = INTERFACE()


def register():
    cfg.app = QtWidgets.QApplication(sys.argv)
    if cfg.app:

        cfg.running = True

        cfg.window = QtWidgets.QMainWindow()
        cfg.window.setWindowTitle("GL Studio Editor")
        cfg.window.resize(800, 600)

        cfg.tabs = QtWidgets.QTabWidget()
        cfg.window.setCentralWidget(cfg.tabs)
        
        cfg.window.show()
        return
    print("Failed to create QApplication")
    return
    
def unregister(): pass

def check_state():
    return cfg.running

def process_frame():
    cfg.app.processEvents()