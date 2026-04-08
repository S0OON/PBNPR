import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE


class NODE_INTERFACE(BASE_NODE):
    LABEL = 'Float'

    def __init__(self, parent):
        super().__init__(parent)

        self.O_float = t.NodeSocket(dpg.generate_uuid(),t.F,'Float ->',value=0.0)

        self._resgister_IO(
            [],
            [self.O_float]
        )

    def on_gui(self):
        Id = super().on_gui()

        statics = self._create_static_attr()
        dpg.add_button(label="Execute",  callback=self.EXEC_CB, parent=statics)
        dpg.add_input_float(parent=statics, callback=self._on_change_float, default_value=self.O_float.value,width=100)

        self._create_output_attr(self.O_float)

    def _on_change_float(self, s,a,u):
        self.O_float.value = a

    def on_execute(self):
        print(f"Executed! : {self.O_float.value}")

    def on_execute_crawler(self, input_data=None):
        self.on_execute()