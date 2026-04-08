import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import time

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'Pulse'

    def __init__(self, parent):
        super().__init__(parent)

        self.ENABLE = False
        self.Pulse  = False # one time pulse

        self.O_output    = t.NodeSocket(dpg.generate_uuid(), t.NONE)
        self.I_intervals = t.NodeSocket(dpg.generate_uuid(), t.F,  '<- Intervals (seconds)', 5.0)
        self.I_stream    = t.NodeSocket(dpg.generate_uuid(), t.ANY,'<- Triggers Connections')

        self._last_pulse_time = time.time()

        self._resgister_IO(
            [self.I_stream, 
             self.I_intervals],
            [self.O_output]
        )

    def on_gui(self):
        Id = super().on_gui()

        statics = self._create_static_attr()
        dpg.add_button(label='execute connections', callback=self._on_change_pulse, parent=statics)
        dpg.add_checkbox(label='Enable',   callback=self._on_change_enable, parent=statics)
        dpg.add_drag_float(label='Seconds',parent=statics, callback=self._on_change_intervals, default_value=self.I_intervals.value, width=100)

        self._create_input_attr(self.I_intervals)
        self._create_input_attr(self.I_stream, dpg.mvNode_PinShape_TriangleFilled)

    def _on_change_enable(self, s, a, u):
        self.ENABLE = a
        if self.ENABLE:
            self._last_pulse_time = time.time() # Reset the timer when enabling so it doesn't instantly fire

    def _on_change_pulse(self, s, a, u):
        # Buttons don't pass a boolean state, so explicitly set True
        self.Pulse = True 

    def _on_change_intervals(self, s, a, u):
        self.I_intervals.value = a 

    def on_execute_crawler(self, input_data=None):
        print(f"Executed! : {self.LABEL}")
        self.Pulse = False

    def on_should_crawl(self):
        if self.Pulse:
            return True

        if self.ENABLE:
            current_time = time.time()
            if current_time - self._last_pulse_time >= self.I_intervals.value:
                self._last_pulse_time = current_time
                return True
            
        # Explicitly return False if no conditions are met
        return False