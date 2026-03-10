
from PySide6.QtWidgets import QCheckBox


class HotCheckBox(QCheckBox):
    Pre_SuperClick = None
    def nextCheckState(self):
        if self.Pre_SuperClick:
            self.Pre_SuperClick()
        return super().nextCheckState()