from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t

STATIC = "Value_Dict_Key"


class NODE_DICT_JOIN(BASE.NODE_INTERFACE):
    NODE_NAME = "Dict join"
    CATEGORY = "Containers"

    def __init__(self):
        super().__init__()
        self.I_dicts = self.add_input("Dicts", type=t.DICT, multi_input=True)
        self.O_dict = self.add_output("Dict", type=t.DICT)

    def on_stream(self):
        data = {}
        for sender in self.I_dicts.connected_ports():
            if isinstance(sender.val, dict):
                data.update(sender.val)
        self.O_dict.val = data
