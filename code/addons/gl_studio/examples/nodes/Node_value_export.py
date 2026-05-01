from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import export_cloud as c
from gl_studio.util import util_types as t

class NODE_CLOUD(BASE.NODE_INTERFACE):
    NODE_NAME = "Cloud (Export value)"
    CATEGORY = "Global"

    def __init__(self):
        super().__init__()
        self.I_ = self.add_input(type=t.DICT)
        c.CLOUD_NODES[self]=True

    def on_should_stream(self):
        return True

    def on_stream(self):
        self.on_sync_port_values()

        if isinstance(self.I_.val,dict):
            c.EXPORT.update(self.I_.val)

    def on_delete(self):
        c.CLOUD_NODES.pop(self)
