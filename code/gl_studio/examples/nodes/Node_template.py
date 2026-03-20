import dearpygui.dearpygui as dpg

def attch():
    print("YYYYYYOOOOOOOOOOOOOOOOOOOOOO")

class NODE_INTERFACE:
    main_node_editor = "node_editor_main"
    label = "node"
    ID = None

    def BUILD(self, sender, app_data):
        self.ID = dpg.generate_uuid()
        
        with dpg.node(label=self.label, parent=self.main_node_editor):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute",callback=attch)

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output):
                dpg.add_text(label="Output ->")

    def AFTER_DRAW_CALL(self):
        pass
cfg = NODE_INTERFACE()