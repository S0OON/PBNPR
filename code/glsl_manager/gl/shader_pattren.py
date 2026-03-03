import moderngl,bpy
import numpy as np
from glsl_manager.gl.modrenGL_lib import GLContext
from glsl_manager.gl.util import util_types as t


class ShaderBase:
    """
    Base class for the ui to understand (Base unit).

    a child class MUST override: NAME, VERT_SRC and FRAG_SRC and render_object().

    helper functions start with '_'
    """
    __slots__ = ['ctx', 'prog', 'vao', 'fbo']  # Optimize memory usage by defining fixed attributes
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
    
    def _exec(self, width, height, gl_flags=None, clear=True):
        """
        Execute render with specified GPU state flags.
        
        Args:
            width, height: Render target size
            gl_flags: ModernGL flags from ctx.enable() (DEPTH_TEST, BLEND, etc.)
            clear: Whether to clear framebuffer before render
        """
        # Setup framebuffer
        if self.fbo is None or self.fbo.size != (width, height):
            if self.fbo:
                self.fbo.release() 
            depth_buffer = self.ctx.depth_renderbuffer((width, height))
            
            self.fbo = self.ctx.framebuffer(
                color_attachments=[self.ctx.texture((width, height), 4)],
                depth_attachment=depth_buffer
            )

        self.fbo.use()
        # Apply render state flags
        if gl_flags:
            self.ctx.enable(gl_flags)
        
        if clear:
            self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        
        if self.vao:
            self.vao.render(moderngl.TRIANGLES)
        
        pixels = np.frombuffer(
            self.fbo.read(components=4),
            dtype=np.uint8)

        self.ctx.disable(t.GL_FLAGS['DEPTH_TEST'] |        
                         t.GL_FLAGS['CULL_FACE'] |        
                         t.GL_FLAGS['BLEND'] |        
                         t.GL_FLAGS['PROGRAM_POINT_SIZE'] |        
                         t.GL_FLAGS['RASTERIZER_DISCARD'] )
        # Read pixels
        return pixels 
    
class ui_base(bpy.types.PropertyGroup):
    """
    Base class to define custom UI as the shader demnads.
    
    must override draw_self_to_panel_canvas to draw the UI in the panel.
    must override unregister to clean up locale data.
    """ 
        
    def draw_self_to_panel_canvas(self,canvas:bpy.types.UILayout):
        """
        Canvas is a box() passed boy the addon internal machine.

        Just like a canvas.
        """
        return
    
    def unregister(self):
        pass