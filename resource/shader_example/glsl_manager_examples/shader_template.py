import moderngl

from glsl_manager.gl.shader_pattren import ShaderBase
from PIL import Image
import numpy as np
# this is a simple tringle implementation.

coords = np.array([(-0.5, -0.5), (0.5, -0.5), (0.0, 0.5)], dtype=np.float32)

class Shader(ShaderBase):
    NAME = "TriangleShader"
    VERT_SRC='''
    #version 330\n
    in vec2 in_pos;
void main() {
    gl_Position = vec4(in_pos,1.0, 1.0);
}
'''
    FRAG_SRC='''
    #version 330\n
    uniform vec4 color;
    out vec4 fragColor;
void main() {
    fragColor = color;
}
'''
    def __init__(self):
        super().__init__()

    def render_object(self):
        # In components
        vao = self.ctx.buffer(coords.tobytes())
        self.vao = self.ctx.vertex_array(
            self.prog,
            [(vao, '2f', 'in_pos')])
        # uniforms
        self.prog['color'].value = (0.5, 0.0, 0.5, 1.0)  # Red
        # out 
        self.fbo = self.ctx.framebuffer(
            color_attachments=self.ctx.texture((800, 600), 4))
        self.fbo.use()
        self.vao.render(moderngl.TRIANGLES)
        # Read pixels (the bridge!)
        return np.frombuffer(
            self.fbo.read(components=4), dtype=np.uint8)

#def exec():
#    """run the example, resault to an image"""
#    s = Shader()
#    res = s.render_object()
#    width, height = 800, 600  # match render_object dimensions
#    img = Image.fromarray(res.reshape((height, width, 4)), 'RGBA')
#    img.show()
#
#
#if __name__ == "__main__":
#    exec()