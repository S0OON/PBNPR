# Node_camera_data.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import numpy as np
import bpy

class NODE_INTERFACE:
    LABEL = "Camera Data"
    
    def __init__(self, parent):
        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
        # --- 1. Sockets Setup ---
        # Input (String for camera name)
        self.I_cam_name = t.NodeSocket(dpg.generate_uuid(), t.STR, 'Camera Name')
        self.I_cam_name.value = 'active' # Default value
        
        # Outputs (Matrices)
        self.O_view = t.NodeSocket(dpg.generate_uuid(), t.F16, 'View Matrix ->')
        self.O_proj = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Proj Matrix ->')
        
        # Fallback identity matrices so it doesn't crash on start
        self.O_view.value = np.eye(4, dtype=np.float32)
        self.O_proj.value = np.eye(4, dtype=np.float32)
        
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
            self.I_cam_name.ID : self.I_cam_name
        } 
        
        self.outputs = {
            self.O_view.ID : self.O_view,
            self.O_proj.ID : self.O_proj
        }

    def on_gui(self):
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute", callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable", callback=self.on_enable_change, default_value=self.ENABLE)

            # String Input
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_cam_name.ID):
                # Using add_input_text instead of add_text so you can actually type the name!
                dpg.add_input_text(label=self.I_cam_name.name, default_value=self.I_cam_name.value, 
                                   callback=self.on_string_change, width=100)
            
            # Outputs
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_view.ID):
                dpg.add_text(self.O_view.name)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_proj.ID):
                dpg.add_text(self.O_proj.name)

    # --- Callbacks ---
    def on_enable_change(self, sender, app_data):
        self.ENABLE = app_data
        
    def on_string_change(self, sender, app_data):
        self.I_cam_name.value = app_data

    def on_should_execute(self): return self.ENABLE
    def on_should_crawl(self): return self.CRAWL
    def on_should_active(self): return self.ACTIVE and self.ENABLE

    def on_execute(self):
        cam_name = self.I_cam_name.value.strip()
        
        # 1. Resolve which camera to use
        if cam_name.lower() == 'active':
            cam_obj = bpy.context.scene.camera
        else:
            cam_obj = bpy.data.objects.get(cam_name)
            
        if not cam_obj or cam_obj.type != 'CAMERA':
            print(f"[{self.LABEL}] Error: Could not find valid camera '{cam_name}'.")
            return

        # 2. View Matrix (Inverse of the Camera's World Matrix)
        # We wrap it directly in np.array() to turn Blender's mathutils matrix into Numpy
        view_mat = np.array(cam_obj.matrix_world.inverted(), dtype=np.float32)
        self.O_view.value = view_mat

        # 3. Projection Matrix
        # Blender calculates this for us using the current scene's render resolution
        depsgraph = bpy.context.evaluated_depsgraph_get()
        render = bpy.context.scene.render
        
        proj_mat = cam_obj.calc_matrix_camera(
            depsgraph,
            x=render.resolution_x,
            y=render.resolution_y,
            scale_x=render.pixel_aspect_x,
            scale_y=render.pixel_aspect_y
        )
        
        self.O_proj.value = np.array(proj_mat, dtype=np.float32)
        
        print(f"[{self.LABEL}] Extracted matrices from '{cam_obj.name}'.")

    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB(): self.on_execute()
        
    def on_execute_after_frame(self): pass