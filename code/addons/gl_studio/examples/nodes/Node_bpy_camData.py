# Node_camera_data.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import numpy as np
import bpy
from typing import cast
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE

def eval_camera_matrices(cam_obj, width, height):
    depsgraph = bpy.context.evaluated_depsgraph_get()
    m_view = np.array(cam_obj.matrix_world.inverted().transposed(), dtype=np.float32).flatten()
    m_proj = np.array(cam_obj.calc_matrix_camera(depsgraph, x=width, y=height).transposed(), dtype=np.float32).flatten()
    return [m_view, m_proj]

class NODE_INTERFACE(BASE_NODE):
    LABAL = "Camera Data"

    def __init__(self, parent):
        super().__init__(parent)

        self.EXECUTE = True
        self.ENABLE = True

        self.I_cam_name = t.NodeSocket(dpg.generate_uuid(), t.STR, 'Camera Name')
        self.I_Width    = t.NodeSocket(dpg.generate_uuid(), t.F,   'Width')
        self.I_Height   = t.NodeSocket(dpg.generate_uuid(), t.F,   'Height')
        
        self.O_view     = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Cam Matrix ->')
        self.O_proj     = t.NodeSocket(dpg.generate_uuid(), t.F16, 'Proj Matrix ->')
        
        # Fallback identity matrices
        self.I_cam_name.value = 'active'
        self.I_Width.value    = 64
        self.I_Height.value   = 64
        self.O_view.value     = np.eye(4, dtype=np.float32)
        self.O_proj.value     = np.eye(4, dtype=np.float32)
        #self.O_Width.value    = self.I_Width.value
        #self.O_Height.value   = self.O_Height.value
        self.ENABLE = True

        self._resgister_IO(
            input_sockets=[self.I_cam_name, self.I_Width, self.I_Height],
            output_sockets=[self.O_view, self.O_proj])
        
    def on_gui(self):
        super().on_gui()

        name = self._create_input_attr(self.I_cam_name)
        dpg.add_input_text(parent=name, default_value=self.I_cam_name.value, callback=lambda s,a,u: setattr(self.I_cam_name, 'value', a))
        w = self._create_input_attr(self.I_Width)
        dpg.add_input_float(parent=w, default_value=self.I_Width.value, callback=lambda s,a,u: setattr(self.I_Width, 'value', a))
        h = self._create_input_attr(self.I_Height)
        dpg.add_input_float(parent=h, default_value=self.I_Height.value, callback=lambda s,a,u: setattr(self.I_Height, 'value', a))

        mCam = self._create_output_attr(self.O_view)
        mProj = self._create_output_attr(self.O_proj)

    def on_execute(self):
        name = cast(str,self.I_cam_name.value)
        if not name: return None
        
        if not name or name.lower() == 'active':
            obj = bpy.context.scene.camera
        else:
            obj = bpy.data.objects.get(name)

        self.O_view.value = obj.matrix_world.inverted()

        self.O_proj.value = obj.calc_matrix_camera(
            bpy.context.evaluated_depsgraph_get(),
            x=self.I_Width.value,
            y=self.I_Height.value,
        )

    def on_execute_crawler(self, input_data=None):
        self.on_execute()
