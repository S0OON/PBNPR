import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import bpy
import numpy as np

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'Object Eval'

    def __init__(self, parent):
        super().__init__(parent)

        self.ENABLE = True

        # --- Sockets Setup ---
        self.I_name    = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- Obj Name', value="Cube")
        
        self.O_verts   = t.NodeSocket(dpg.generate_uuid(), t.F16, 'pos ->')
        self.O_normals = t.NodeSocket(dpg.generate_uuid(), t.F16, 'normals ->')
        self.O_mat     = t.NodeSocket(dpg.generate_uuid(), t.F16, 'matrix ->')
        self.O_uvs     = t.NodeSocket(dpg.generate_uuid(), t.F16, 'active uv ->')

        # Register to the BASE_NODE router
        self._resgister_IO(
            [self.I_name],
            [self.O_verts, self.O_normals, self.O_mat, self.O_uvs]
        )

    def on_gui(self):
        # Draw the main node window
        Id = super().on_gui()

        # Add the Execute Button to the static header
        statics = self._create_static_attr()
        dpg.add_button(  label="Execute", callback=self.EXEC_CB,           parent=statics)
        dpg.add_checkbox(label="Enable",  callback=self._on_change_enable, parent=statics, default_value=self.ENABLE)

        # Draw Inputs
        name = self._create_input_attr(self.I_name)
        dpg.add_input_text(parent=name, callback=self._on_name_change, default_value=self.I_name.value, width=120)

        # Draw Outputs
        pos = self._create_output_attr(self.O_verts)
        dpg.add_text(self.O_verts.name, parent=pos)

        n = self._create_output_attr(self.O_normals)
        dpg.add_text(self.O_normals.name, parent=n)

        m = self._create_output_attr(self.O_mat)
        dpg.add_text(self.O_mat.name, parent=m)

        u = self._create_output_attr(self.O_uvs)
        dpg.add_text(self.O_uvs.name, parent=u)


    def _on_change_enable(self, sender, app_data, user_data):
        self.ENABLE = app_data

    def _on_name_change(self, sender, app_data, user_data):
        self.I_name.value = app_data

    def on_execute(self):
        obj_name = self.I_name.value
        
        if not obj_name or obj_name not in bpy.data.objects:
            print(f"[{self.LABEL}] Error: Object '{obj_name}' not found.")
            return
            
        obj = bpy.data.objects[obj_name]
        if obj.type != 'MESH':
            print(f"[{self.LABEL}] Error: Object '{obj_name}' is not a MESH.")
            return
        
        # --- The NumPy Blender Extraction Engine ---
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj  = obj.evaluated_get(depsgraph)
        mesh      = eval_obj.to_mesh()
        mesh.calc_loop_triangles()
        
        tris_count = len(mesh.loop_triangles)
        
        # 1. Triangulation Indices (Corners of every triangle)
        loops_indices = np.empty((tris_count * 3), dtype=np.int32)
        mesh.loop_triangles.foreach_get("loops", loops_indices)

        vertex_indices = np.empty((tris_count * 3), dtype=np.int32)
        mesh.loop_triangles.foreach_get("vertices", vertex_indices)

        # 2. Positions (Unrolled to triangles)
        all_pos = np.empty((len(mesh.vertices), 3), dtype=np.float32)
        mesh.vertices.foreach_get("co", all_pos.reshape(-1))
        final_pos = all_pos[vertex_indices]

        # 3. Normals (From loops to preserve sharp/custom edges)
        all_normals = np.empty((len(mesh.loops), 3), dtype=np.float32)
        mesh.loops.foreach_get("normal", all_normals.reshape(-1))
        final_normals = all_normals[loops_indices]

        # 4. UV Map (Active layer)
        if mesh.uv_layers.active:
            all_uvs = np.empty((len(mesh.loops), 2), dtype=np.float32)
            mesh.uv_layers.active.data.foreach_get("uv", all_uvs.reshape(-1))
            final_uvs = all_uvs[loops_indices]
        else:
            final_uvs = np.array([], dtype=np.float32)

        eval_obj.to_mesh_clear()

        # --- 5. Push data to the Output Sockets ---
        self.O_verts.value   = final_pos
        self.O_normals.value = final_normals
        self.O_uvs.value     = final_uvs
        self.O_mat.value     = np.array(obj.matrix_world.transposed(), dtype=np.float32).flatten()

        print(f"[{self.LABEL}] Extracted {len(final_pos)} vertices from '{obj_name}'")

    def on_execute_crawler(self, input_data=None):
        if self.ENABLE:
            self.on_execute()