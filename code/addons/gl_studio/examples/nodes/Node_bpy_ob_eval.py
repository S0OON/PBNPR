import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import numpy as np

try:
    import bpy
except ImportError:
    bpy = None

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'Blender Object Data'

    def __init__(self, parent):
        super().__init__(parent)

        self.I_obj_name = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- object name','Cube')
        self.I_uv_name  = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- uv name','UVMap')

        self.O_pos     = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Position ->')
        self.O_normals = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Normals ->')
        self.O_matrix  = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Matrix ->')
        self.O_uv      = t.NodeSocket(dpg.generate_uuid(), t.F16, 'UV ->')

        self._resgister_IO(
            [self.I_obj_name,
             self.I_uv_name],
            [self.O_pos, 
             self.O_normals, 
             self.O_matrix, 
             self.O_uv]
        )

    def on_gui(self):
        Id = super().on_gui()

        statics = self._create_static_attr()
        dpg.add_input_text(label="Object Name", default_value=self.I_obj_name.value, callback=self._on_obj_change, parent=statics, width=150)
        dpg.add_input_text(label="UV Map Name", default_value=self.I_uv_name.value,  callback=self._on_uv_change, parent=statics, width=150)
        
        self._create_input_attr(self.I_obj_name)
        self._create_input_attr(self.I_uv_name)
        self._create_output_attr(self.O_pos)
        self._create_output_attr(self.O_normals)
        self._create_output_attr(self.O_matrix)
        self._create_output_attr(self.O_uv)

    def _on_obj_change(self, s, a, u): self.I_obj_name.value = a
    def _on_uv_change(self,  s, a, u): self.I_uv_name.value= a

    def on_execute(self):
        if not bpy: return
        obj_name = self.I_obj_name.value
        uv_name  = self.I_uv_name.value

        obj = bpy.data.objects.get(obj_name)
        if not obj or obj.type != 'MESH':
            print(f"[{self.LABEL}] Invalid Mesh: {obj_name}")
            return

        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        mesh.calc_loop_triangles()

        num_tris = len(mesh.loop_triangles)
        if num_tris == 0:
            eval_obj.to_mesh_clear()
            return

        vert_idx = np.zeros(num_tris * 3, dtype=np.int32)
        mesh.loop_triangles.foreach_get("vertices", vert_idx)
        
        loop_idx = np.zeros(num_tris * 3, dtype=np.int32)
        mesh.loop_triangles.foreach_get("loops", loop_idx)

        verts = np.zeros(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("co", verts)
        self.O_pos.value = verts.reshape(-1, 3)[vert_idx]

        norms = np.zeros(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("normal", norms)
        self.O_normals.value = norms.reshape(-1, 3)[vert_idx]

        if uv_name in mesh.uv_layers:
            uvs = np.zeros(len(mesh.loops) * 2, dtype=np.float32)
            mesh.uv_layers[uv_name].data.foreach_get("uv", uvs)
            self.O_uv.value = uvs.reshape(-1, 2)[loop_idx]
        else:
            self.O_uv.value = np.zeros((num_tris * 3, 2), dtype=np.float32)

        # Transpose applied instantly to fix Blender (Row) -> OpenGL (Col) mapping
        self.O_matrix.value = np.array(eval_obj.matrix_world, dtype=np.float32).T

        eval_obj.to_mesh_clear()

    def on_execute_crawler(self, input_data=None):
        self.on_execute()