# Node_object_evaluation.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import bpy
import numpy as np


class NODE_INTERFACE:
    LABEL = "Object Evaluation"
    
    def __init__(self, parent):
        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
# 1. Define Sockets (Using t.STR for input, t.ANY for Numpy arrays)
        self.I_obj_name = t.NodeSocket(dpg.generate_uuid(), t.STR,'obj name')
        self.O_verts    = t.NodeSocket(dpg.generate_uuid(), t.F16,'obj vertices')
        self.O_normals  = t.NodeSocket(dpg.generate_uuid(), t.F16,'obj normals')
        self.O_uvs      = t.NodeSocket(dpg.generate_uuid(), t.F16,'obj uvs')
        self.O_mat      = t.NodeSocket(dpg.generate_uuid(), t.F16,'obj matrix')
        
# Default value so it doesn't crash on empty execution
        self.I_obj_name.value = "" 

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
        
# 2. Register Sockets 
        self.inputs = {
            self.I_obj_name.ID : self.I_obj_name
        } 
        
        self.outputs = {
            self.O_verts.ID   : self.O_verts,
            self.O_normals.ID : self.O_normals,
            self.O_uvs.ID     : self.O_uvs,
            self.O_mat.ID     : self.O_mat
        }

    def on_gui(self):
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            # Static Controls
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute",  callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable", callback=self.on_enable_change, default_value=self.ENABLE)
                dpg.add_checkbox(label="Active", callback=self.on_active_change, default_value=self.ACTIVE)
                dpg.add_checkbox(label="Crawl",  callback=self.on_crawl_change, default_value=self.CRAWL)
                
            # String Input
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_obj_name.ID):
                dpg.add_input_text(label="Obj Name", callback=self.on_string_change, width=100)
            
            # Outputs
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_verts.ID):
                dpg.add_text("Vertices (np) ->")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_normals.ID):
                dpg.add_text("Normals (np) ->")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_uvs.ID):
                dpg.add_text("UV Map (np) ->")
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_mat.ID):
                dpg.add_text("Matrix (np) ->")


    # --- UI Callbacks ---
    def on_enable_change(self, sender, app_data):
        self.ENABLE = app_data
    
    def on_active_change(self, sender, app_data):
        self.ACTIVE = app_data
        
    def on_crawl_change(self, sender, app_data):
        self.CRAWL = app_data

    def on_string_change(self, sender, app_data):
        self.I_obj_name.value = app_data

    # --- Execution Logic ---
    def on_should_execute(self):
        return self.ENABLE
    
    def on_should_crawl(self):
        return self.CRAWL
    
    def on_should_active(self):
        return self.ACTIVE and self.ENABLE
    
    def on_execute(self):
        obj_name = self.I_obj_name.value
        
        # 1. Safety Checks
        if not obj_name or obj_name not in bpy.data.objects:
            print(f"[{self.LABEL}] Error: Object '{obj_name}' not found.")
            return
            
        obj = bpy.data.objects[obj_name]
        if obj.type != 'MESH':
            print(f"[{self.LABEL}] Error: Object '{obj_name}' is not a MESH.")
            return
            
        mesh = obj.data
        
        # 2. Ultra-fast Numpy Extraction
        # Extract Vertices
        verts = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("co", verts)
        self.O_verts.value = verts.reshape(-1, 3) # Reshape to (N, 3)
        
        # Extract Normals (Vertex normals)
        normals = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("normal", normals)
        self.O_normals.value = normals.reshape(-1, 3)
        
        # Extract UVs (UVs are per-loop, not per-vertex!)
        if mesh.uv_layers.active:
            uvs = np.empty(len(mesh.loops) * 2, dtype=np.float32)
            mesh.uv_layers.active.data.foreach_get("uv", uvs)
            self.O_uvs.value = uvs.reshape(-1, 2)
        else:
            self.O_uvs.value = np.array([]) # No UV map fallback

        # Extract Object Matrix
        self.O_mat.value = np.array(obj.matrix_world, dtype=np.float32)
            
        print(f"[{self.LABEL}] Success! Extracted {len(self.O_verts.value)} vertices from {obj_name}.")
    
    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB():
            self.on_execute()
    
    def on_execute_after_frame(self):
        pass