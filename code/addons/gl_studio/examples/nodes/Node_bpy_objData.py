import bpy
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel


class NODE_OBJECT_EVAL(BASE.NODE_INTERFACE):
    NODE_NAME = "Object Data"
    CATEGORY = "Blender"

    def __init__(self):
        super().__init__()
        self.I_name = self.add_input("obj_name", type=t.STR)

        self.O_pos = self.add_output("pos", type=t.ANY)
        self.O_normals = self.add_output("normals", type=t.ANY)
        self.O_uvs = self.add_output("uvs", type=t.DICT)  # Dict of Numpy Arrays
        self.O_matrix = self.add_output("world_matrix", type=t.F16)
        self.reset()

    def on_gui(self):
        self.status_label = QLabel()
        return self.status_label

    def reset(self):
        self.I_name.val = "Cube"
        self.O_pos.val = None
        self.O_normals.val = None
        self.O_uvs.val = None
        self.O_matrix.val = None
        self.status_label.setText("No object linked")
        self.status_label.setStyleSheet(t.RED)

    def on_stream(self):
        self.on_sync_port_values()
        obj_name = self.I_name.val
        obj = bpy.data.objects.get(obj_name)
        if obj is None:
            self.status_label.setText(f"Missing: {obj_name}")
            self.status_label.setStyleSheet(t.RED)  # Red text
            return

        self.status_label.setText(f"Connected: {obj.name}")
        self.status_label.setStyleSheet(t.GREEN)  # Green text

        # 2. Extract World Matrix (Transposed and Flattened for ModernGL)
        # ModernGL/OpenGL expects column-major order, so we transpose before flattening
        world_matrix = np.array(
            obj.matrix_world.transposed(), dtype=np.float32
        ).flatten()
        self.O_matrix.val = world_matrix

        # 3. Extract Mesh Data using Fast Numpy foreach_get()
        # 3. Extract Mesh Data using Fast Numpy
        if obj.type == "MESH":
            mesh = obj.data

            # 1. Force Blender to generate triangulation data
            mesh.calc_loop_triangles()

            num_tris = len(mesh.loop_triangles)
            num_tri_verts = num_tris * 3  # e.g. 36 for a cube

            # Get the Vertex Indices and Loop Indices for every triangle corner
            tri_vert_indices = np.empty(num_tri_verts, dtype=np.int32)
            mesh.loop_triangles.foreach_get("vertices", tri_vert_indices)

            tri_loop_indices = np.empty(num_tri_verts, dtype=np.int32)
            mesh.loop_triangles.foreach_get("loops", tri_loop_indices)

            # --- Positions ---
            raw_pos = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
            mesh.vertices.foreach_get("co", raw_pos)
            raw_pos = raw_pos.reshape(-1, 3)
            # Map raw vertices to unrolled triangle vertices
            self.O_pos.val = raw_pos[tri_vert_indices].flatten()

            # --- Normals ---
            # (Note: For flat shading, you might want split normals (mesh.loops.normal),
            # but here is the mapping for smooth vertex normals)
            raw_norms = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
            mesh.vertices.foreach_get("normal", raw_norms)
            raw_norms = raw_norms.reshape(-1, 3)
            self.O_normals.val = raw_norms[tri_vert_indices].flatten()

            # --- UVs ---
            uv_dict = {}
            if mesh.uv_layers:
                for layer in mesh.uv_layers:
                    raw_uvs = np.empty(len(mesh.loops) * 2, dtype=np.float32)
                    layer.data.foreach_get("uv", raw_uvs)
                    raw_uvs = raw_uvs.reshape(-1, 2)
                    # UVs are mapped by loop indices, not vertex indices!
                    uv_dict[layer.name] = raw_uvs[tri_loop_indices].flatten()

            self.O_uvs.val = uv_dict

        else:
            self.reset()

    def on_graph_load(self):
        self.reset()
