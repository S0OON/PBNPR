import dearpygui.dearpygui as dpg
import time

def attch():
    print("SUUUUUUUPPPPPPPPPPPPPP")

def timer(DeadLine:float):
    time = dpg.get_total_time() - dpg.get_delta_time()
    if DeadLine <= time:
        attch()

class NODE_INTERFACE:
    main_node_editor = "node_editor_main"
    label = "Timer node"
    ID = None

    IN_t   = None
    IN_bol = ''

    def BUILD(self, sender, app_data):
        self.ID     = dpg.generate_uuid()
        self.T      = f"NODE_IN_TIMER_{self.ID}"
        self.IN_bol = f"NODE_IN_BOl_{self.ID}"

        with dpg.node(label=self.label, parent=self.main_node_editor):

            with dpg.node_attribute(label="Float",
                                    attribute_type=dpg.mvNode_Attr_Static):
                self.IN_t = dpg.add_input_float(label="Seconds", default_value=1.0, width=100)
                dpg.add_checkbox(label="Activate",tag=self.IN_bol)

            with dpg.node_attribute(label="Execute", 
                                    attribute_type=dpg.mvNode_Attr_Input,
                                    shape=dpg.mvNode_PinShape_Triangle):
                dpg.add_text("-> Execute Branch")

    def AFTER_DRAW_CALL(self):
        if dpg.get_value(self.IN_bol):
            print(dpg.get_value(self.IN_t))
        #    timer(dpg.get_value(self.IN_t))

cfg = NODE_INTERFACE()