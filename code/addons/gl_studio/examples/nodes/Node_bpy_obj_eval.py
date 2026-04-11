# Node_bpy_ob_eval.py - Enhanced version
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import numpy as np

try:
    import bpy
except ImportError:
    bpy = None

class NODE_INTERFACE(BASE_NODE):
    CATEGORY = 'Evaluate'
    LABEL = 'Blender Object Data'

    def __init__(self, parent):
        super().__init__(parent)

        self.I_obj_name = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- object name', 'Cube')
        self.I_uv_name  = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- uv name', 'UVMap')

        # Outputs as MGL-ready numpy arrays
        self.O_vertices = t.NodeSocket(dpg.generate_uuid(), t.OB, 'Vertices (flat) ->')  # For VBO
        self.O_indices  = t.NodeSocket(dpg.generate_uuid(), t.OB, 'Triangle Indices ->')  # For indexed drawing
        self.O_uvs      = t.NodeSocket(dpg.generate_uuid(), t.OB, 'UVs (flat) ->')
        self.O_normals  = t.NodeSocket(dpg.generate_uuid(), t.OB, 'Normals (flat) ->')
        self.O_matrix   = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Matrix ->')

        self._resgister_IO(
            [self.I_obj_name, self.I_uv_name],
            [self.O_vertices, self.O_indices, self.O_uvs, self.O_normals, self.O_matrix]
        )

    def on_gui(self):
        Id = super().on_gui()
        
        statics = self._create_static_attr()
        dpg.add_input_text(label="Object", default_value=self.I_obj_name.value, 
                          callback=self._on_obj_change, parent=statics, width=150)
        dpg.add_input_text(label="UV Map", default_value=self.I_uv_name.value,
                          callback=self._on_uv_change, parent=statics, width=150)
        

        self._create_input_attr(self.I_obj_name)

        self._create_input_attr(self.I_uv_name)
        self._create_output_attr(self.O_vertices)
        self._create_output_attr(self.O_indices)
        self._create_output_attr(self.O_uvs)
        self._create_output_attr(self.O_normals)
        self._create_output_attr(self.O_matrix)


    def _on_obj_change(self, s, a, u): self.I_obj_name.value = a
    def _on_uv_change(self, s, a, u): self.I_uv_name.value = a


    def on_execute(self):
        if not bpy: return
        
        obj = bpy.data.objects.get(self.I_obj_name.value)
        if not obj or obj.type != 'MESH':
            print(f"[{self.LABEL}] Invalid Mesh: {self.I_obj_name.value}")
            return

        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        mesh.calc_loop_triangles()

        if len(mesh.loop_triangles) == 0:
            eval_obj.to_mesh_clear()
            return

        # Get triangle indices (for indexed drawing)
        num_tris = len(mesh.loop_triangles)
        vert_idx = np.zeros(num_tris * 3, dtype=np.int32)
        mesh.loop_triangles.foreach_get("vertices", vert_idx)
        self.O_indices.value = vert_idx

        # Get loop indices for UVs/normals
        loop_idx = np.zeros(num_tris * 3, dtype=np.int32)
        mesh.loop_triangles.foreach_get("loops", loop_idx)

        # Vertices (flat array for VBO)
        verts = np.zeros(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("co", verts)
        # Flatten by index for non-indexed VAO (simpler for MGL)
        self.O_vertices.value = verts.reshape(-1, 3)[vert_idx].flatten()

        # Normals (per-vertex, flattened)
        norms = np.zeros(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("normal", norms)
        self.O_normals.value = norms.reshape(-1, 3)[vert_idx].flatten()

        # UVs
        uv_name = self.I_uv_name.value
        if uv_name in mesh.uv_layers:
            uvs = np.zeros(len(mesh.loops) * 2, dtype=np.float32)
            mesh.uv_layers[uv_name].data.foreach_get("uv", uvs)
            self.O_uvs.value = uvs.reshape(-1, 2)[loop_idx].flatten()
        else:
            self.O_uvs.value = np.zeros(num_tris * 3 * 2, dtype=np.float32)

        # Matrix (row-major for OpenGL)
        self.O_matrix.value = np.array(eval_obj.matrix_world, dtype=np.float32).T

        eval_obj.to_mesh_clear()
        print(f"[{self.LABEL}] Extracted {num_tris} triangles from {self.I_obj_name.value}")

    def on_execute_crawler(self, input_data=None):
        self.on_execute()