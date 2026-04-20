import bpy
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class NODE_CAMERA_EVAL(BASE.NODE_INTERFACE):
    NODE_NAME = "Camera Data"
    CATEGORY = "Blender"

    def __init__(self):
        super(NODE_CAMERA_EVAL, self).__init__()
        # Inputs
        self.I_name = self.add_input("cam_name", type=t.STR)
        self.I_width = self.add_input("Width", type=t.F)
        self.I_height = self.add_input("Height", type=t.F)

        # Manual Defaults
        self.I_name.value = "active"
        self.I_width.value = t.RES_W
        self.I_height.value = t.RES_H

        # Outputs
        self.O_view = self.add_output("view_matrix", type=t.F16)
        self.O_proj = self.add_output("proj_matrix", type=t.F16)

    def on_gui(self):
        self.status_label = QLabel("Camera: ---")
        self.status_label.setStyleSheet(t.RED)
        return self.status_label

    def reset(self):
        self.I_name.value = "active"
        self.O_view.value = None
        self.O_proj.value = None

    def on_stream(self):
        self.on_sync_port_values()

        name_val = str(self.I_name.value)
        if not name_val or name_val.lower() == "active":
            cam = bpy.context.scene.camera
        else:
            cam = bpy.data.objects.get(name_val)

        if not cam or cam.type != "CAMERA":
            self.status_label.setText("Status: NOT FOUND")
            self.status_label.setStyleSheet(t.RED)
            return

        self.status_label.setText(f"Status: {cam.name}")
        self.status_label.setStyleSheet(t.GREEN)
        # 2. View Matrix (Inverse of World)
        view = np.array(
            cam.matrix_world.inverted().transposed(), dtype=np.float32
        ).flatten()

        # 3. Projection Matrix
        # Using .data and correcting parameter names (width/height)
        depsgraph = bpy.context.evaluated_depsgraph_get()
        proj_matrix = cam.calc_matrix_camera(
            depsgraph,
            x=int(self.I_width.value),
            y=int(self.I_height.value),
        )
        proj = np.array(proj_matrix.transposed(), dtype=np.float32).flatten()

        self.O_view.value = view.tobytes()
        self.O_proj.value = proj.tobytes()

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        self.reset()
