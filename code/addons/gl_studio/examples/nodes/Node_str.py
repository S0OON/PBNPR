import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE


class NODE_INTERFACE(BASE_NODE):
    LABEL = 'String'

    def __init__(self, parent):
        super().__init__(parent)

        self.O_str = t.NodeSocket(dpg.generate_uuid(),t.STR,'String ->',value="Hello World")

        self._resgister_IO(
            [],
            [self.O_str]
        )

    def on_gui(self):
        Id = super().on_gui()

        statics = self._create_static_attr()
        dpg.add_button(label="Execute",  callback=self.EXEC_CB, parent=statics)

        Str = self._create_output_attr(self.O_str)
        dpg.add_input_text(parent=Str, callback=self._on_change_str, default_value=self.O_str.value,width=100,label=self.O_str.name)

    def _on_change_str(self, s,a,u):
        self.O_str.value = a

    def on_execute(self):
        print(f"Executed! : {self.O_str.value}")

    def on_execute_crawler(self, input_data=None):
        self.on_execute()