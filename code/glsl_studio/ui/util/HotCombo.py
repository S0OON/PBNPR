
from PySide6.QtWidgets import QComboBox

class HotCombo(QComboBox):
    label = ''
    PreSuper_Popup = None
    def showPopup(self):
        if self.PreSuper_Popup:
            self.PreSuper_Popup()
        return super().showPopup()