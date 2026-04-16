import bpy
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class NODE_OBJECT_EVAL(BASE.NODE_INTERFACE):
    NODE_NAME = "Object Eval"
    CATEGORY = "Blender"

    def __init__(self):
        super(NODE_OBJECT_EVAL, self).__init__()

        # Inputs
        self.I_name = self.add_input("obj_name", type=t.STR)

        # Outputs
        self.O_pos = self.add_output("world_pos", type=t.F3)
        self.O_normals = self.add_output("normals", type=t.F3)  # List of Vec3 (F3)
        self.O_matrix = self.add_output("world_matrix", type=t.F16)  # 4x4 Matrix
        self.O_uvs = self.add_output("uv_maps", type=t.DICT)  # Dict of UV layers

    def build_ui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.status_label = QLabel("No Object Linked")
        self.status_label.setStyleSheet("color: #888;")
        lay.addWidget(self.status_label)

        return widget

    def on_execute_crawler(self):
        obj_name = self.I_name.value

        # 1. Check if object exists in Blender
        if not obj_name or obj_name not in bpy.data.objects:
            self.status_label.setText(f"Missing: {obj_name}")
            self.status_label.setStyleSheet("color: #ff5555;")  # Red text
            return

        obj = bpy.data.objects[obj_name]
        self.status_label.setText(f"Connected: {obj.name}")
        self.status_label.setStyleSheet("color: #55ff55;")  # Green text

        # 2. Extract World Data
        # World Position (Translation component of the matrix)
        self.O_pos.value = [obj.location.x, obj.location.y, obj.location.z]

        # World Matrix (Flattened list for easier passing)
        self.O_matrix.value = [list(row) for row in obj.matrix_world]

        # 3. Extract Mesh Data (Requires Mesh type)
        if obj.type == "MESH":
            mesh = obj.data

            # Extract Normals (World Space)
            # Note: For efficiency, we just grab vertex normals
            self.O_normals.value = [
                [v.normal.x, v.normal.y, v.normal.z] for v in mesh.vertices
            ]

            # Extract UVs as a Dictionary
            uv_dict = {}
            if mesh.uv_layers:
                for layer in mesh.uv_layers:
                    # Collect UV coordinates for each loop
                    uv_dict[layer.name] = [
                        [data.uv.x, data.uv.y] for data in layer.data
                    ]

            self.O_uvs.value = uv_dict
        else:
            self.O_normals.value = []
            self.O_uvs.value = {}
