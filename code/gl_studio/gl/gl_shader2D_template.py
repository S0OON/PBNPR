# DONT CHANGE CAPITLIZED NAMES! (called from the plugin)
from PySide6 import QtWidgets
import moderngl,bpy
from PIL import Image
import numpy as np
from gl_studio.gl.modrenGL_lib import GLContext as GL
from gl_studio.util import util_types as t
from gl_studio.ui.util.HotCombo import HotCombo

class ShaderBase:
    vertex_shader=f"""#version 330

    in vec2 in_vert;
                    
        void main() {{
            gl_Position = vec4(in_vert, 0.0, 1.0);
        }}
"""
    fragment_shader=f"""#version 330

    out vec4 f_color;

        void main() {{
            // Normalize coordinates to create a gradient
            f_color = vec4(gl_FragCoord.x / 800.0, 0.5, gl_FragCoord.y / 600.0, 1.0);
        }}
"""
    __slots__ = ['ctx', 'prog', 'vao', 'fbo']
    def __init__(self): # __family__ lol
        """
        Compile only. (program creation), using the child's source code strings. #version 330
        
        Adds an additional ctx,prog,FBO,VAO
        """
        self.ctx = GL.get()
        self.prog = self.ctx.program(vertex_shader=self.vertex_shader,
                                    fragment_shader=self.fragment_shader)
        self.vao = None
        self.fbo = None
    
    def Release(self):
        if self.vao:
            self.vao.release()
        if self.fbo:
            self.fbo.release()
        self.prog.release()

    def Execute(self, width, height, gl_flags=None, clear=True):
        W, H = int(width),int(height)
        if self.fbo is None or self.fbo.size != (width, height):
            if self.fbo:
                self.fbo.release()
            
            depth_buffer = self.ctx.depth_renderbuffer((width, height))
            Color_buffer = self.ctx.texture((width, height), 4)
            
            self.fbo = self.ctx.framebuffer( # Set Actives
                color_attachments=Color_buffer,
                depth_attachment=depth_buffer)

        self.fbo.use()
        
        if gl_flags:
            self.ctx.enable(gl_flags)
        
        if clear:
            self.ctx.clear(0.0, 0.0, 0.0, 0.0)
        
        if self.vao:
            self.vao.render(moderngl.TRIANGLES)
        
        pixels = np.frombuffer(
            self.fbo.read(components=4),
            dtype=np.uint8)

        # WARNING, WILL BREAK BLENDER UI IF THIS IS SNIPPET DELETED
        self.ctx.disable(t.GL_FLAGS['DEPTH_TEST'        ] |
                         t.GL_FLAGS['CULL_FACE'         ] |        
                         t.GL_FLAGS['BLEND'             ] |        
                         t.GL_FLAGS['PROGRAM_POINT_SIZE'] |        
                         t.GL_FLAGS['RASTERIZER_DISCARD'] )
        return pixels 

class MAIN:
    __slots__ = ['data', '__weakref__', #<- DONT CHANGE, remove  __slots__ if further errors occure amigo.
                 'shader', # main
                 'width','height','targetOBJ','sliderUV'] # peripheral
    def __init__(self):
        self.shader = ShaderBase()
        self.width = 512.0
        self.height = 512.0
        self.targetOBJ = ''
        self.sliderUV = None

    def BUILD_UI(self, target_layout:QtWidgets.QVBoxLayout):
        # --- object name ---
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Object name"))
        field = QtWidgets.QLineEdit()
        field.setText(self.targetOBJ)
        field.textChanged.connect(self.on_targetOBJ_change)
        row.addWidget(field)

        target_layout.addLayout(row) 
        # --- uv map  ---
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("UV map:"))
        combo = HotCombo()
        combo.PreSuper_Popup = self.on_UV_activated_reload
        combo.activated.connect(self.on_UV_activated)
        self.sliderUV = combo
        row.addWidget(combo)
        
        target_layout.addLayout(row) 

    def EXECUTE(self):
        return
        pixels = self.shader.Execute(self.width,self.height,
                                     gl_flags=None,clear=None)
        
        img = Image.frombytes('RGB', pixels.size, pixels).transpose(Image.FLIP_TOP_BOTTOM)
        img.show()

    def on_targetOBJ_change(self,text):
        self.targetOBJ = text

    def on_UV_activated_reload(self):
        obj = bpy.data.objects.get(self.targetOBJ)
        if obj:
            uv_slider = self.sliderUV
            uv_slider.clear()
            for i,j in obj.data.uv_layers.items():
                uv_slider.addItem(i,j)

    def on_UV_activated(self, index):
        pass


    def on_width_changed(self, value):
        self.width = value

    def on_height_changed(self, value):
        self.height = value