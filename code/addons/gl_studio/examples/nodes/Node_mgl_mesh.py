from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.opengl import mgl
from gl_studio.util import util_types as t
from PIL import Image


class NODE_MGL_BASIC(BASE.NODE_INTERFACE):
    NODE_NAME = "mgl mesh"
    CATEGORY = "OpenGL"

    def __init__(self):
        super().__init__()
        # --- Shader & Settings ---
        self.I_w = self.add_input("width", type=t.F, default_value=t.RES_W)
        self.I_h = self.add_input("Height", type=t.F, default_value=t.RES_H)

        self.I_vert = self.add_input("Vert_str", type=t.STR)
        self.I_frag = self.add_input("Frag_str", type=t.STR)

        self.I_uniforms = self.add_input("Uniforms", type=t.DICT)
        self.I_attrs = self.add_input("Attributes", type=t.DICT)

        # --- Outputs ---
        self.O_pixels = self.add_output("Pixels_RGBA", type=t.ANY)

    def on_stream(self):
        self.on_sync_port_values()
        shader = mgl.SHADER()
        if isinstance(self.I_vert.value, str):
            shader.src_v = self.I_vert.value
        if isinstance(self.I_frag.value, str):
            shader.src_f = self.I_frag.value

        shader.compile(self.I_w.value, self.I_h.value)

        shader.uniforms(self.I_uniforms.value)
        shader.vertex_attributes(self.I_attrs.value)
        self.O_pixels.value = shader.render()

    def reset(self):
        self.I_vert.value = None
        self.I_frag.value = None
        self.I_uniforms.value = None
        self.I_attrs.value = None
        self.O_pixels.value = None

    def on_graph_save(self):
        self.reset()

    def on_graph_load(self):
        self.reset()
