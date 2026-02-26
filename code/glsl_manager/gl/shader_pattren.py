
import moderngl
import numpy as np
from modrenGL_lib import GLContext

class ShaderBase:
    NAME = "BaseShader"
    VERT_SRC = """
        #version 330
        in vec3 in_pos;
        uniform mat4 mvp;
        void main() {
            gl_Position = mvp * vec4(in_pos, 1.0);
        }
    """
    
    FRAG_SRC = """
        #version 330
        out vec4 fragColor;
        uniform vec4 color;
        void main() {
            fragColor = color;
        }
    """
    
    def __init__(self):
        """
        Compile only (program creation), using the child's source code strings. #version 330
        
        Adds an additional FBO,VAO
        """
        self.ctx = GLContext.get()
        self.prog = self.ctx.program(vertex_shader=self.VERT_SRC,
                                    fragment_shader=self.FRAG_SRC)
        self.vao = None  # Created per-geometry
        self.fbo = None  # Created per-resolution
    
    def uniform(self, **kwargs):
        """Simple uniforms helper"""
        for name, value in kwargs.items():
            self.prog[name].value = value
    
    def exec(self, width, height, gl_flags, clear=True):
        """
        Render to an off-screen framebuffer, returning pixel data as a numpy array.
        
        Must provide VAO and program uniforms before calling.
        """
        if self.fbo is None or self.fbo.size != (width, height):
            self.fbo = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((width, height), 4)])
        
        self.fbo.use()
        self.ctx.enable(gl_flags)
    
        if clear:
            self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        if self.vao:
            self.vao.render(moderngl.TRIANGLES)
        
        # Read pixels (the bridge!)
        return np.frombuffer(
            self.fbo.read(components=4), 
            dtype=np.uint8)
    
    def render_object(self):
        """Override this method in child classes to set up VAO, uniforms, and call exec()"""
    
    def release(self):
        if self.vao:
            self.vao.release()
        if self.fbo:
            self.fbo.release()
        self.prog.release()