from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.opengl import mgl_class
from gl_studio.util import util_types as t
from gl_studio.util import export_cloud as c
from PySide6.QtWidgets import QComboBox, QCheckBox, QWidget, QVBoxLayout
import numpy as np

STATICc = 'Combo_vertex_array_primitive'

class NODE_MGL_BASIC(BASE.NODE_INTERFACE):
    NODE_NAME = "mgl mesh"
    CATEGORY = "OpenGL"

    def __init__(self):
        super().__init__()
        # --- Shader & Settings ---
        self.shader = mgl_class.MGL(c.CTX)
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
        w = QWidget()
        l = QVBoxLayout()
        w.setLayout(l)

        self.chBox = QCheckBox()
        self.chBox.setStyleSheet("color: white;")
        self.chBox.setText("Standalone Context (Headless only!)")
        l.addWidget(self.chBox)

        self.combo = QComboBox()
        self.combo.addItems(t.flag_primitive_modes.keys())
        self.combo.currentTextChanged.connect(
            lambda x: self.set(STATICc,self.combo.currentText()))
        l.addWidget(self.combo)

        return w

    def reset(self):
        if self.has(STATICc):
            self.combo.setCurrentText(self.get(STATICc))
        else:
            self.add(STATICc,self.combo.currentText())

        # Reset port values to defaults
        self.I_w.val = int(t.RES_W)
        self.I_h.val = int(t.RES_H)
        self.I_vert.val = t.SRC_SCREEN_VERT
        self.I_frag.val = t.SRC_SCREEN_FRAG
        self.I_uniforms.val = None
        self.I_attrs.val = None
        self.O_pixels.val = None


    def on_stream(self):
        self.on_sync_port_values()

        if c.CTX is None:
            # Check if standalone is requested (default to False if GUI not initialized)
            standalone = self.chBox.isChecked() if self.chBox else False
            c.CTX = mgl_class.gl.create_context(standalone=standalone)
            c.CTX.gc_mode = 'context_gc'

        shader = self.shader
        shader.ctx = c.CTX

        shader.w = int(self.I_w.val)
        shader.h = int(self.I_h.val)
        if isinstance(self.I_vert.val, str):
            shader.src_v = self.I_vert.val
        if isinstance(self.I_frag.val, str):
            shader.src_f = self.I_frag.val

        rebuild = shader.compile()

        shader.uniforms(self.I_uniforms.val)
        shader.uniforms_textures(self.I_textures.val)
        shader.vertex_attributes(self.I_attrs.val,force_rebuild=rebuild)

        shader.ctx.enable(t.Flags.context.depth_test)

        a,d = shader.render(t.flag_primitive_modes[self.get(STATICc)])

        A = np.frombuffer(a,dtype=np.float32)
        A = A.reshape((shader.h,shader.w,4))

        B = np.frombuffer(d,dtype=np.float32)
        B = B.reshape((shader.h,shader.w))

        self.O_pixels.val = A
        self.O_depth.val = B


    def on_graph_load(self):
        self.reset()

    def on_delete(self):
        self.shader.clear()
