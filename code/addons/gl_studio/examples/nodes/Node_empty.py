# PART 1 -- MUST HAVE DEPENDCIES
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t

# PART 2 -- CUSOM PORT DRAWING
from PySide6.QtGui import QPainter

def paint( painter:QPainter, option,widget):
    painter.save()
    _rect = QRectF(0.0,0.0,15.0,15.0) # MUST BE FLOATS OTHERWISE A C++ CRASH (WONT BE TRACEBACKED)
    painter.drawRect( _rect)
    painter.restore()


# PART 3 --- CUSTOM OVERlAY ON NODE (Whole item)
# via Subclassing the custom QGraphicsItem abstrction class
from PySide6.QtWidgets import QGraphicsItem
from PySide6.QtGui import Qt
from PySide6.QtCore import QRectF

class ITEM(QGraphicsItem):
    _rect = QRectF(0.0,0.0,15.0,15.0) # MUST BE FLOATS OTHERWISE A C++ CRASH (WONT BE TRACEBACKED)
    def __init__(self, /, parent: QGraphicsItem) -> None:
        super().__init__(parent)

    def boundingRect(self):
        return self._rect

    def paint(self, painter:QPainter, option,widget):
        painter.save()
        painter.drawRect(self._rect)
        painter.restore()

# PART 1
class NODE_EMPTY(BASE.NODE_INTERFACE):
    NODE_NAME = "Empty"
    CATEGORY = "Misc"

    def __init__(self):
        super().__init__()
        self.I_a = self.add_input('in',type=t.NONE)
        # PART 2 -> overiding the ports default paint function (replacing behaviour)
        self.O_b = self.add_output('out',type=t.NONE )
        self.O_b.port_item.paint = paint
        # PART 3.1 naitive QGraphics object
        self.box = ITEM(parent=self.view)
