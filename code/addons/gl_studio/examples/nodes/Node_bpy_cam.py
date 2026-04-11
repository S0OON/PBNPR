import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import bpy
import numpy as np

class NODE_INTERFACE(BASE_NODE):
    CATEGORY = 'Evaluate'
    LABEL = 'Camera data'

    def __init__(self, parent):
        super().__init__(parent)

        self.ENABLE = True

        self.I_name = t.NodeSocket(dpg.generate_uuid(), t.STR, '<- Camera Name', value='active')
        self.I_x = t.NodeSocket(dpg.generate_uuid(),    t.F,   '<- X',value=800)
        self.I_y = t.NodeSocket(dpg.generate_uuid(),    t.F,   '<- Y',value=600)
        self.O_mCam = t.NodeSocket(dpg.generate_uuid(), t.F16, 'view matrix ->')
        self.O_proj = t.NodeSocket(dpg.generate_uuid(), t.F16, 'projection matrix ->')

        self._resgister_IO(
            [self.I_name, self.I_x, self.I_y],
            [self.O_mCam, self.O_proj]
        )

    def on_gui(self):
        Id = super().on_gui()

        statics = self._create_static_attr()
        dpg.add_button(label="Execute",  callback=self.EXEC_CB, parent=statics)
        dpg.add_input_text(parent=statics, callback=self._on_name_change,width=100,label='Name', default_value=self.I_name.value)
        dpg.add_input_float(parent=statics, callback=self._on_change_x,default_value=self.I_x.value,width=100,label='x')
        dpg.add_input_float(parent=statics, callback=self._on_change_y,default_value=self.I_y.value,width=100,label='y')

        self._create_input_attr(self.I_name)
        self._create_input_attr(self.I_x)
        self._create_input_attr(self.I_y)
        self._create_output_attr(self.O_mCam)
        self._create_output_attr(self.O_proj)
    

    def _on_name_change(self, s,a,u):
        self.I_name.value = a

    def _on_change_x(self, s,a,u):
        self.I_x.value = a

    def _on_change_y(self, s,a,u):
        self.I_y.value = a

    def on_execute(self):
            if not self.I_name.value or self.I_name.value.lower() == 'active':
                cam = bpy.context.scene.camera
            else:
                cam = bpy.data.objects.get(self.I_name.value)

            if not cam: 
                print(f"Camera '{self.I_name.value}' not found!")
                return
             
            view = np.array(cam.matrix_world.inverted().transposed(), dtype=np.float32).flatten()
            self.O_mCam.value = view
             
            proj_matrix = cam.calc_matrix_camera(
                bpy.context.evaluated_depsgraph_get(), 
                x=int(self.I_x.value), 
                y=int(self.I_y.value)
            )
            self.O_proj.value = np.array(proj_matrix.transposed(), dtype=np.float32).flatten()

            print(f"Executed! : {self.I_name.value}, view matrix: {self.O_mCam.value}, proj matrix: {self.O_proj.value}") 

    def on_execute_crawler(self, input_data=None):
        if self.ENABLE:
            self.on_execute()