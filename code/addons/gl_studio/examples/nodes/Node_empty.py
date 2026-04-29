from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t


class NODE_EMPTY(BASE.NODE_INTERFACE):
    NODE_NAME = "Empty"

    def __init__(self):
        super().__init__()
        self.I_a = self.add_input('in',type=t.NONE)
        self.O_b = self.add_output('out',type=t.NONE)
