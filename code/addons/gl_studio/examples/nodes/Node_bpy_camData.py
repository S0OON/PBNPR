import bpy
import numpy as np
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel


class NODE_CAMERA_EVAL(BASE.NODE_INTERFACE):
    NODE_NAME = "Camera Data"
    CATEGORY = "Blender"

    def __init__(self):
        super(NODE_CAMERA_EVAL, self).__init__()
        self.I_name = self.add_input("camera name", type=t.STR)
        self.I_w = self.add_input("Width", type=t.F)
        self.I_h = self.add_input("Height", type=t.F)

        self.O_camP = self.add_output("camera Pos", type=t.F2)
        self.O_view = self.add_output("view_matrix", type=t.F16)
        self.O_proj = self.add_output("proj_matrix", type=t.F16)

        self.O_pkg = self.add_output("Packed matricies", type=t.DICT)
        self.reset()

    def on_gui(self):
        self.status_label = QLabel()
        return self.status_label

    def reset(self):
        self.I_name.val = "active"
        self.I_w.val = t.RES_W
        self.I_h.val = t.RES_H
        self.O_view.val = None
        self.O_proj.val = None
        self.O_camP.val = None
        self.O_pkg.val = {}
        self.status_label.setText("No Camera linked")
        self.status_label.setStyleSheet(t.RED)

    def on_stream(self):
        self.on_sync_port_values()

        name_val = str(self.I_name.val)
        if not name_val or name_val.lower() == "active":
            cam = bpy.context.scene.camera # pyright: ignore
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
            x=int(self.I_w.val),
            y=int(self.I_h.val),
        )
        proj = np.array(proj_matrix.transposed(), dtype=np.float32).flatten()

        loc = cam.location

        self.O_view.val = view
        self.O_proj.val = proj
        self.O_camP.val = loc

        self.O_pkg.val = {"view_matrix": view, "proj_matrix": proj, "camera_pos":loc}

    def on_graph_load(self):
        self.reset()
