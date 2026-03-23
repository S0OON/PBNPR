import dearpygui.dearpygui as dpg
from collections import defaultdict



class NODE_INTERFACE:
    LABEL = "Node"

    def __init__(self,parent):
        self.PARENT = parent # as in node editor
        self.ID     = dpg.generate_uuid()
        self.GUI_CB = self.on_gui
        self.EXEC_CB= self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.LOOP_CB= self.on_execute_after_frame
        self.SHOULD_EXEC_CB=self.on_should_execute
        self.ENABLE = False
        self.ACTIVE = False
        self.IS_ROOT= False
        self.CRAWLER= None
        self.LINKS  = set()             # filled by plugin
        self.PINS   = {'CRAWLERS':set(), # filled by plugin
                       'INPUTS' :set(), # self
                       'OUTPUTS':set()} # self
        #custom
        self.floater  = 1.0
        
    def on_gui(self):
        with dpg.node(label=self.LABEL,parent=self.PARENT,tag=self.ID):
            #static 
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute",callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable",callback=self.on_enable)
                dpg.add_checkbox(label="Active",callback=self.on_active)
            
            #inputs
            floater_tag = dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            self.PINS['INPUTS'].add(floater_tag)
            dpg.add_input_float(callback=self.on_float_change,parent=floater_tag)

            #outs
            out_tag = dpg.add_node_attribute(label="Out ->",attribute_type=dpg.mvNode_Attr_Output)
            self.PINS['OUTPUTS'].add(out_tag)
            #Crawler
            self.CRAWLER = dpg.add_node_attribute(label="<- Crawling chain",shape=dpg.mvNode_PinShape_Quad,attribute_type=dpg.mvNode_Attr_Input)

    def on_enable(self,sender,app_data):
        self.ENABLE = app_data

    def on_active(self,sender,app_data):
        self.ACTIVE = app_data

    def on_float_change(self,sender,app_data):
        self.floater = app_data
        print(self.float)

    def on_should_execute(self):
        return True

    def on_execute(self):
        if not self.ENABLE: return
        print(f"Im example: {self.ID}.")

    def on_execute_crawler(self):
        self.on_execute()

    def on_execute_after_frame(self):
        if not self.ACTIVE: return
        print(f"Im example's loop: {self.ID}.")



