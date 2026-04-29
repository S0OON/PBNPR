from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.opengl import mgl
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QComboBox
import numpy as np
STATICc = 'Combo_vertex_array_primitive'

class NODE_MGL_BASIC(BASE.NODE_INTERFACE):
    NODE_NAME = "mgl mesh"
    CATEGORY = "OpenGL"

    def __init__(self):
        super().__init__()
        # --- Shader & Settings ---
        self.I_w = self.add_input("width", type=t.F)
        self.I_h = self.add_input("Height", type=t.F)

        self.I_vert = self.add_input("Vert_str", type=t.STR)
        self.I_frag = self.add_input("Frag_str", type=t.STR)

        self.I_uniforms = self.add_input("Uniforms", type=t.DICT)
        self.I_attrs = self.add_input("Attributes", type=t.DICT)

        self.I_textures = self.add_input("Textures", type=t.DICT)

        # --- Outputs ---
        self.O_pixels = self.add_output("Pixels_RGBA", type=t.RGBA)
        self.O_depth = self.add_output("Depth",type=t.RGBA)
        self.reset()

    def on_gui(self):
        self.combo = QComboBox()
        self.combo.addItems(mgl.flag_primitive_modes.keys())
        self.combo.currentTextChanged.connect(
            lambda x: self.set(STATICc,self.combo.currentText()))

        return self.combo

    def reset(self):
        self.I_w.val = t.RES_W
        self.I_h.val = t.RES_H
        self.I_vert.val = t.SRC_SCREEN_VERT
        self.I_frag.val = t.SRC_SCREEN_FRAG
        self.I_uniforms.val = None
        self.I_attrs.val = None
        self.O_pixels.val = None

        if self.has(STATICc):
            self.combo.setCurrentText(self.get(STATICc))
        else:
            self.add(STATICc,self.combo.currentText())

    def on_stream(self):
        self.on_sync_port_values()

        shader = mgl.SHADER()

        shader.w = self.I_w.val
        shader.h = self.I_h.val
        if isinstance(self.I_vert.val, str):
            shader.src_v = self.I_vert.val
        if isinstance(self.I_frag.val, str):
            shader.src_f = self.I_frag.val

        shader.compile()

        shader.uniforms(self.I_uniforms.val)
        shader.uniforms_textures(self.I_textures.val)
        shader.vertex_attributes(self.I_attrs.val)

        shader.ctx.enable(mgl.Flags.context.depth_test)

        a,d = shader.render(mgl.flag_primitive_modes[self.get(STATICc)])

        A = np.frombuffer(a,dtype=np.float32)
        A = A.reshape((shader.h,shader.w,4))

        B = np.frombuffer(d,dtype=np.float32)
        B = B.reshape((shader.h,shader.w))

        self.O_pixels.val = A
        self.O_depth.val = B
        shader.clear()

    def on_graph_load(self):
        self.reset()
