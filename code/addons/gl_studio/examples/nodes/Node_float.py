import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE


class NODE_INTERFACE(BASE_NODE):
    LABEL = 'Float'

    def __init__(self, parent):
        super().__init__(parent)

        self.EXECUTE = True # testing

        self.O_f = t.NodeSocket(dpg.generate_uuid(),t.F,'Float ->')

        self._resgister_IO(
            output_sockets=[
                self.O_f,
            ]
        )

    def on_gui(self):
        super().on_gui()
        
        Fl = self._create_output_attr(self.O_f)
        dpg.add_drag_float(default_value=self.O_f.value, callback=self._on_float_change, 
                           parent=Fl,width=50)


    def _on_float_change(self,sender,app_data):
        self.O_f.value = app_data

    def on_execute(self):
        print(f"Executed! : {self.O_f.value}")

    def on_execute_crawler(self, input_data=None):
        self.on_execute()