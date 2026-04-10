import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import moderngl
import numpy as np

class NODE_INTERFACE(BASE_NODE):
    CATEGORY = 'MGL'
    LABEL = 'MGL Mesh'
    
    def __init__(self, parent):
        super().__init__(parent)
        # Geometry
        self.I_pos_buf = t.NodeSocket(dpg.generate_uuid(), t.OB, '<- Position Buffer')
        self.I_uv_buf = t.NodeSocket(dpg.generate_uuid(), t.OB, '<- UV Buffer')
        # Transform
        self.I_m = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Model Matrix')
        self.I_v = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- View Matrix')
        self.I_p = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Proj Matrix')
        # Material
        self.I_tex = t.NodeSocket(dpg.generate_uuid(), t.OB, '<- Texture')
        # Output
        self.I_w = t.NodeSocket(dpg.generate_uuid(), t.F, '<- Width', 1024)
        self.I_h = t.NodeSocket(dpg.generate_uuid(), t.F, '<- Height', 1024)
        self.O_pixels = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Pixels ->')
        
        self._fbo = None
        self._vao = None
        self._prog = None
        
    def on_execute(self):
        # Lazy init shader (once)
        if self._prog is None:
            self._init_shader()
            
        ctx = GLctx.get()
        w, h = int(self.I_w.value), int(self.I_h.value)
        
        # Lazy init FBO (on size change)
        if self._fbo is None or self._fbo.size != (w, h):
            if self._fbo: self._fbo.release()
            self._fbo = ctx.simple_framebuffer((w, h))
            
        # Get resources
        pos_buf = self.I_pos_buf.value  # MGL Buffer object
        uv_buf = self.I_uv_buf.value
        tex = self.I_tex.value
        
        if None in (pos_buf, uv_buf, tex):
            print("Missing inputs")
            return
            
        # Build VAO (can cache if buffer IDs don't change)
        if self._vao: self._vao.release()
        self._vao = ctx.vertex_array(
            self._prog,
            [(pos_buf, '3f', 'in_position'),
             (uv_buf, '2f', 'in_uv')]
        )
        
        # Render
        self._fbo.use()
        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
        
        # Upload uniforms
        self._prog['M'].write(self.I_m.value.astype('f4').tobytes())
        self._prog['V'].write(self.I_v.value.astype('f4').tobytes())
        self._prog['P'].write(self.I_p.value.astype('f4').tobytes())
        
        tex.use(0)
        self._prog['tex'].value = 0
        
        ctx.clear(0.05, 0.05, 0.05, 1.0)
        self._vao.render(moderngl.TRIANGLES)
        
        # Readback
        raw = self._fbo.read(components=4)
        img = np.frombuffer(raw, dtype=np.uint8).reshape((h, w, 4))
        self.O_pixels.value = np.flipud(img)
        
    def _init_shader(self):
        ctx = GLctx.get()
        self._prog = ctx.program(
            vertex_shader='''#version 330
                uniform mat4 M, V, P;
                in vec3 in_position;
                in vec2 in_uv;
                out vec2 v_uv;
                void main() {
                    gl_Position = P * V * M * vec4(in_position, 1.0);
                    v_uv = in_uv;
                }''',
            fragment_shader='''#version 330
                uniform sampler2D tex;
                in vec2 v_uv;
                out vec4 f_color;
                void main() {
                    f_color = texture(tex, v_uv);
                }'''
        )