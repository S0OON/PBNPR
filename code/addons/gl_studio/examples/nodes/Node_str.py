import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE


class NODE_INTERFACE(BASE_NODE):
    LABEL = 'String'

    def __init__(self, parent):
        super().__init__(parent)

        self.EXECUTE = True # testing

        self.O_str = t.NodeSocket(dpg.generate_uuid(),t.STR,'String ->',value="Hello World")

        self._resgister_IO(
            output_sockets=[
                self.O_str,
            ]
        )

    def on_gui(self):
        super().on_gui()
        
        Str = self._create_output_attr(self.O_str)
        dpg.add_input_text(default_value=self.O_str.value, callback=self._on_str_change, 
                           parent=Str,width=60)


    def _on_str_change(self,sender,app_data):
        self.O_str.value = app_data

    def on_execute(self):
        print(f"Executed! : {self.O_str.value}")

    def on_execute_crawler(self, input_data=None):
        self.on_execute()