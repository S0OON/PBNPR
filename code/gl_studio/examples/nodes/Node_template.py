import dearpygui.dearpygui as dpg


class NODE_INTERFACE:
    LABEL = "Node"

    def __init__(self,parent):
        self.PARENT  = parent # as in node editor
        self.ID      = dpg.generate_uuid()

        self.EXEC_GUI_CB  = self.on_gui
        self.EXEC_CB      = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame

        self.SHOULD_EXEC_CB     =self.on_should_execute
        self.SHOULD_CRAWL_CB    =self.on_should_crawl
        self.SHOULD_BE_ACTIVE   =self.on_should_active

        self.ENABLE  = False
        self.ACTIVE  = False

        self.CRAWLER = None
        self.LINKS   = set()              # filled by plugin
        self.PINS    = {'CRAWLERS':set(), # filled by plugin
                        'INPUTS'  :set(), # self
                        'OUTPUTS' :set()} # self
        #custom
        self.floater  = 1.0
    
    def on_gui(self):
        """Node GUI"""
        with dpg.node(label=self.LABEL,parent=self.PARENT,tag=self.ID):
            #static 
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute",callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable",callback=self.on_enable_change)
                dpg.add_checkbox(label="Active",callback=self.on_active_change)
            
            #inputs
            floater_tag = dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Input)
            dpg.add_input_float(callback=self.on_float_change,parent=floater_tag)
            self.PINS['INPUTS'].add(floater_tag)

            #outputs
            output = dpg.add_node_attribute(attribute_type=dpg.mvNode_Attr_Output)
            dpg.add_text("Output ->",parent=output)
            self.PINS['OUTPUTS'].add(output)

            #Crawler
            self.CRAWLER = dpg.add_node_attribute(label="<- Crawling chain",shape=dpg.mvNode_PinShape_Quad,attribute_type=dpg.mvNode_Attr_Input)

    def on_enable_change(self,sender,app_data):
        """at Enable button click"""
        self.ENABLE = app_data

    def on_active_change(self,sender,app_data):
        """at Active button click"""
        self.ACTIVE = app_data

    def on_float_change(self,sender,app_data):
        """Custom"""
        self.float = app_data
    
    def on_should_execute(self):
        """Check if should execute"""
        return self.ENABLE
    
    def on_should_active(self):
        return (self.ACTIVE and self.ENABLE)

    def on_should_crawl(self):
        """check if should crawl"""
        return self.CRAWLER # None if shouldnt init a crawl.

    def on_execute(self):
        """Execution"""
        print(f"Im node example exec: {self.ID}")

    def on_execute_crawler(self):
        """on-Crawler-call Execution"""
        print(f"Im node example crawled exec: {self.ID}")

    def on_execute_after_frame(self):
        """On-Loop-call Execution"""
        print(f"Im node example loop exec: {self.ID}.")
