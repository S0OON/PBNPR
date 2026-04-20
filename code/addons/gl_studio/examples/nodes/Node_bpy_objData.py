import bpy
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class NODE_OBJECT_EVAL(BASE.NODE_INTERFACE):
    NODE_NAME = "Object Data"
    CATEGORY = "Blender"

    def __init__(self):
        super().__init__()

        # Inputs
        self.I_name = self.add_input("obj_name", type=t.STR, default_value="Cube")

        # Outputs
        self.O_pos = self.add_output("pos", type=t.ANY)
        self.O_normals = self.add_output("normals", type=t.ANY)
        self.O_uvs = self.add_output("uvs", type=t.DICT)  # Dict of Numpy Arrays
        self.O_matrix = self.add_output("world_matrix", type=t.F16)
        self.reset()

    def on_gui(self):
        self.status_label = QLabel("No object linked")
        self.status_label.setStyleSheet(t.RED)
        return self.status_label

    def reset(self):
        self.I_name.value = "Cube"
        self.O_pos.value = None
        self.O_normals.value = None
        self.O_uvs.value = None
        self.O_matrix.value = None
        self.status_label.setText("No object linked")
        self.status_label.setStyleSheet(t.RED)

    def on_stream(self):
        self.on_sync_port_values()
        obj_name = self.I_name.value

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
        self.O_matrix.value = world_matrix.tobytes()

        # 3. Extract Mesh Data using Fast Numpy foreach_get()
        if obj.type == "MESH":
            mesh = obj.data

            # Note: We enforce a depsgraph evaluation if there are modifiers,
            # but using raw data as a baseline matching the old node logic.

            num_verts = len(mesh.vertices)

            # Positions (Vertex Coordinates)
            pos_data = np.empty(num_verts * 3, dtype=np.float32)
            mesh.vertices.foreach_get("co", pos_data)
            self.O_pos.value = pos_data.tobytes()

            # Normals (Vertex Normals)
            normals_data = np.empty(num_verts * 3, dtype=np.float32)
            mesh.vertices.foreach_get("normal", normals_data)
            self.O_normals.value = normals_data.tobytes()

            # UVs (Loop UVs extracted into a dictionary)
            uv_dict = {}
            if mesh.uv_layers:
                num_loops = len(mesh.loops)
                for layer in mesh.uv_layers:
                    uv_data = np.empty(num_loops * 2, dtype=np.float32)
                    layer.data.foreach_get("uv", uv_data)

                    # Convert to bytes here so the dictionary is safe to compare!
                    uv_dict[layer.name] = uv_data.tolist()

            self.O_uvs.value = uv_dict

        else:
            self.reset()

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        self.reset()
