# Node_object_evaluation.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import bpy
import numpy as np

def _get_mesh_data_for_gpu(obj:bpy.types.Object):
    """Returns [ i, pos[], n[], mat4, UV(active) ]"""
    depsgraph = bpy.context.evaluated_depsgraph_get()
    eval_obj  = obj.evaluated_get(depsgraph)
    mesh      = eval_obj.to_mesh()
    mesh.calc_loop_triangles()
    
    tris_count = len(mesh.loop_triangles)
    
    loops_indices  = np.empty((tris_count * 3), dtype=np.int32)
    mesh.loop_triangles.foreach_get("loops", loops_indices)

    vertex_indices = np.empty((tris_count * 3), dtype=np.int32)
    mesh.loop_triangles.foreach_get(t.bl_verts, vertex_indices)

    all_pos   = np.empty((len(mesh.vertices), 3), dtype=np.float32)
    mesh.vertices.foreach_get(t.bl_Co, all_pos.reshape(-1))
    final_pos = all_pos[vertex_indices]

    all_normals   = np.empty((len(mesh.loops), 3), dtype=np.float32)
    mesh.loops.foreach_get(t.bl_normal, all_normals.reshape(-1))
    final_normals = all_normals[loops_indices]
    
    mesh = obj.data
    
    if mesh.uv_layers.active:
        uvs = np.empty(len(mesh.loops) * 2, dtype=np.float32)
        mesh.uv_layers.active.data.foreach_get("uv", uvs)
        final_UV = uvs.reshape(-1, 2)
    else:
        final_UV = np.array([]) 
    
    final_mat = np.array(obj.matrix_world, dtype=np.float32)

    eval_obj.to_mesh_clear() 
    return loops_indices, final_pos, final_normals, final_mat, final_UV


class X:
    LABEL = "Object Evaluation"
    
    def __init__(self, parent):
        self.PARENT = parent
        self.ID     = dpg.generate_uuid()
        
# --- 1. Sockets Setup ---
        self.I_obj_name = t.NodeSocket(dpg.generate_uuid(), t.STR, 'obj name')
        self.O_verts    = t.NodeSocket(dpg.generate_uuid(), t.F16, 'obj vertices')
        self.O_normals  = t.NodeSocket(dpg.generate_uuid(), t.F16, 'obj normals')
        self.O_mat      = t.NodeSocket(dpg.generate_uuid(), t.F16, 'obj matrix')
        self.O_uvs      = t.NodeSocket(dpg.generate_uuid(), t.F16, 'obj uvs')
# Defaults
        self.I_obj_name.value = "" 
# std calls
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
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute",  callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable", callback=self.on_enable_change, default_value=self.ENABLE)
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_obj_name.ID):
                dpg.add_input_text(label="Obj Name", callback=self.on_string_change, width=100)
            
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_verts.ID):
                dpg.add_text("Vertices (np) ->")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_normals.ID):
                dpg.add_text("Normals (np) ->")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_mat.ID):
                dpg.add_text("Matrix (np) ->")
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_uvs.ID):
                dpg.add_text("UV Map (np) ->")


    def on_enable_change(self, sender, app_data): self.ENABLE = app_data
    def on_string_change(self, sender, app_data): self.I_obj_name.value = app_data

    def on_should_execute(self): return self.ENABLE
    def on_should_crawl(self):   return None
    def on_should_active(self):  return None
    
    
    def on_execute(self):
        obj_name = self.I_obj_name.value
        
        if not obj_name or obj_name not in bpy.data.objects:
            print(f"[{self.LABEL}] Error: Object '{obj_name}' not found.")
            return
            
        obj  = bpy.data.objects[obj_name]
        if obj.type != 'MESH':
            print(f"[{self.LABEL}] Error: Object '{obj_name}' is not a MESH.")
            return
        
        i, V, N, M, UV = _get_mesh_data_for_gpu(obj)

        self.O_verts.value   = V
        self.O_normals.value = N
        self.O_mat.value     = M
        self.O_uvs.value     = UV

        print(f"[{self.LABEL}] Success! Extracted {len(self.O_verts.value)} vertices from {obj_name}.")
    
    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB(): self.on_execute()
    
    def on_execute_after_frame(self): pass