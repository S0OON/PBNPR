# Node_camera_data.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import numpy as np
import bpy

def eval_camera_matrices(cam_obj, width, height):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    m_view = np.array(cam_obj.matrix_world.inverted().transposed(), dtype=np.float32).flatten()
    m_proj = np.array(cam_obj.calc_matrix_camera(depsgraph, x=width, y=height).transposed(), dtype=np.float32).flatten()
    return [m_view, m_proj]

class X:
    LABEL = "Camera Data"
    
    def __init__(self, parent):
        self.PARENT = parent
        self.ID     = dpg.generate_uuid()
        
# --- 1. Sockets Setup ---
        self.I_cam_name = t.NodeSocket(dpg.generate_uuid(), t.STR, 'Camera Name')
        self.I_Width    = t.NodeSocket(dpg.generate_uuid(), t.F,   'Width')
        self.I_Height   = t.NodeSocket(dpg.generate_uuid(), t.F,   'Height')
        
        self.O_view     = t.NodeSocket(dpg.generate_uuid(), t.F16, 'View Matrix ->')
        self.O_proj     = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Proj Matrix ->')
        
        # Fallback identity matrices
        self.I_cam_name.value = 'active'
        self.I_Width.value    = 64
        self.I_Height.value   = 64
        self.O_view.value     = np.eye(4, dtype=np.float32)
        self.O_proj.value     = np.eye(4, dtype=np.float32)
        #self.O_Width.value    = self.I_Width.value
        #self.O_Height.value   = self.O_Height.value
        
# --- Standard Callbacks ---
        self.EXEC_GUI_CB        = self.on_gui
        self.EXEC_CB            = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        
        self.SHOULD_EXEC_CB     = self.on_should_execute
        self.SHOULD_CRAWL_CB    = self.on_should_crawl
        self.SHOULD_BE_ACTIVE   = self.on_should_active
        
        self.ENABLE = True
        self.ACTIVE = False
        self.CRAWL  = False
        
        self.inputs = {
            self.I_cam_name.ID : self.I_cam_name,
            self.I_Width.ID    : self.I_Width,
            self.I_Height.ID   : self.I_Height
        } 
        
        self.outputs = {
            self.O_view.ID   : self.O_view,
            self.O_proj.ID   : self.O_proj,
            #self.O_Width.ID  : self.O_Width,
            #self.O_Height.ID : self.O_Height
        }

    def on_gui(self):
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute", callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable", callback=self.on_enable_change, default_value=self.ENABLE)
# INputs
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_cam_name.ID):
                dpg.add_input_text(label=self.I_cam_name.name, default_value=self.I_cam_name.value, callback=self.on_string_change, width=100)
            
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_Width.ID):
                dpg.add_text(self.I_Width.name)
                dpg.add_input_float(callback=self.on_W_change,width=80)

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_Height.ID):
                dpg.add_text(self.I_Height.name)
                dpg.add_input_float(callback=self.on_H_change,width=80)
# outputs
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_view.ID):
                dpg.add_text(self.O_view.name)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_proj.ID):
                dpg.add_text(self.O_proj.name)

    def on_enable_change(self, sender, app_data): self.ENABLE = app_data
    def on_string_change(self, sender, app_data): self.I_cam_name.value = app_data
    def on_should_execute(self):  return self.ENABLE
    def on_should_crawl(self):    return self.CRAWL
    def on_should_active(self):   return self.ACTIVE and self.ENABLE
    
    def on_W_change(self, sender, app_data):
        self.I_Width.value = app_data

    def on_H_change(self, sender, app_data):
        self.I_Height.value = app_data

    def on_execute(self):
        cam_name = self.I_cam_name.value.strip()
        
        if cam_name.lower() == 'active':
            cam_obj = bpy.context.scene.camera
        else:
            cam_obj = bpy.data.objects.get(cam_name)
            
        if not cam_obj or cam_obj.type != 'CAMERA':
            print(f"[{self.LABEL}] Error: Could not find valid camera '{cam_name}'.")
            return

        self.O_view.value , self.O_proj.value = eval_camera_matrices(cam_obj, int(self.I_Width.value), int(self.I_Height.value))
    
        print(f"[{self.LABEL}] Extracted matrices from '{cam_obj.name}'.")

    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB(): self.on_execute()
        
    def on_execute_after_frame(self): pass