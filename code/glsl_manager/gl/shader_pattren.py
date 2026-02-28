import moderngl,bpy
import numpy as np
from glsl_manager.gl.modrenGL_lib import GLContext


class ShaderBase:
    """
    Base class for the ui to understand (Base unit).

    a child class MUST override: NAME, VERT_SRC and FRAG_SRC and render_object().

    helper functions start with '_'
    """
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
        
        Adds an additional ctx,prog,FBO,VAO
        """
        self.ctx = GLContext.get()
        self.prog = self.ctx.program(vertex_shader=self.VERT_SRC,
                                    fragment_shader=self.FRAG_SRC)
        self.vao = None
        self.fbo = None

    def render_object(self):
        """
        Must overide, will be called in addon's internals.
        """
    
    def _release(self):
        if self.vao:
            self.vao.release()
        if self.fbo:
            self.fbo.release()
        self.prog.release()
    
    def _uniform(self, **kwargs): 
        for name, value in kwargs.items():
            self.prog[name].value = value
    
    def _exec(self, width, height, gl_flags:list =None, clear=True):
        """Return the Rendered Pixel data (demands VAO)"""
        if self.fbo is None or self.fbo.size != (width, height):
            self.fbo = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((width, height), 4)])
            
        self.fbo.use()
        if gl_flags:
            for f in gl_flags:
                self.ctx.enable(f)
    
        if clear:
            self.ctx.clear(0.0, 0.0, 0.0, 0.0)

        if self.vao:
            self.vao.render(moderngl.TRIANGLES)
        
        # Read pixels (the bridge!)
        return np.frombuffer(
            self.fbo.read(components=4), 
            dtype=np.uint8)
    
class ui_base(bpy.types.PropertyGroup):
    """
    Base class to define custom UI as the shader demnads.
    
    must override draw_self_to_panel_canvas to draw the UI in the panel.
    """ 
        
    def draw_self_to_panel_canvas(self,canvas:bpy.types.UILayout):
        """
        Canvas is a box() passed boy the addon internal machine.

        Just like a canvas.
        """
        return