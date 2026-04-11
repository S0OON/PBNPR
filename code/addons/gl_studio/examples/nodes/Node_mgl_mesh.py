# Node_mgl_layered_renderer.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
from gl_studio.gl.ModernOpenGL import GLctx as GL
import moderngl
import numpy as np

class NODE_INTERFACE(BASE_NODE):
    CATEGORY = 'MGL'
    LABEL = 'Layered Mesh Renderer'
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Resolution
        self.I_width  = t.NodeSocket(dpg.generate_uuid(), t.F, '<- Width', 1024)
        self.I_height = t.NodeSocket(dpg.generate_uuid(), t.F, '<- Height', 1024)
        
        # Geometry inputs (from BPY nodes)
        self.I_vertices = t.NodeSocket(dpg.generate_uuid(), t.OB, '<- Vertices (flat)')
        self.I_uvs      = t.NodeSocket(dpg.generate_uuid(), t.OB, '<- UVs (flat)')
        self.I_normals  = t.NodeSocket(dpg.generate_uuid(), t.OB, '<- Normals (flat)')
        
        # Transform inputs
        self.I_view = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- View Matrix')
        self.I_proj = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Proj Matrix')
        
        # Material
        self.I_texture_data = t.NodeSocket(dpg.generate_uuid(), t.OB, '<- Texture Data')
        
        # Outputs - Layer textures as numpy arrays
        self.O_color    = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Color (RGBA) ->')
        self.O_normal   = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Normal Map ->')
        self.O_depth    = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Depth Map ->')
        self.O_position = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Position Map ->')
        
        self._resgister_IO(
            [self.I_vertices, self.I_uvs, self.I_normals, 
             self.I_view, self.I_proj, self.I_texture_data,
             self.I_width, self.I_height],
            [self.O_color, self.O_normal, self.O_depth, self.O_position]
        )
        
        # MGL resources (lazy init)
        self._ctx = None
        self._vbo_pos = None
        self._vbo_uv = None
        self._vbo_normal = None
        self._texture = None
        self._programs = {}
        self._fbos = {}
        
    def on_gui(self):
        Id = super().on_gui()
        statics = self._create_static_attr()
        dpg.add_button(label="Execute", callback=self.EXEC_CB, parent=statics)
        
        # Resolution controls
        dpg.add_drag_float(label="Width", default_value=self.I_width.value,
                          callback=lambda s,a,u: setattr(self.I_width, 'value', a),
                          parent=statics, width=100)
        dpg.add_drag_float(label="Height", default_value=self.I_height.value,
                          callback=lambda s,a,u: setattr(self.I_height, 'value', a),
                          parent=statics, width=100)
        
        # Sockets
        for sock in [self.I_vertices, self.I_uvs, self.I_normals, 
                     self.I_view, self.I_proj, self.I_texture_data,
                     self.I_width, self.I_height]:
            self._create_input_attr(sock)
            
        for sock in [self.O_color, self.O_normal, self.O_depth, self.O_position]:
            self._create_output_attr(sock)

    def on_execute(self):
        ctx = GL.get()
        self._ctx = ctx
        
        # Validate inputs
        verts    = self.I_vertices.value
        uvs      = self.I_uvs.value
        normals  = self.I_normals.value
        view     = self.I_view.value
        proj     = self.I_proj.value
        tex_data = self.I_texture_data.value
        
        if any(v is None for v in [verts, uvs, normals, view, proj]):
            print(f"[{self.LABEL}] Missing required inputs")
            return
        
        w, h = int(self.I_width.value), int(self.I_height.value)
        
        # Build/update geometry buffers
        self._update_geometry(verts, uvs, normals)
        
        # Build/update texture
        self._update_texture(tex_data)
        
        # Build/update FBOs
        self._update_fbos(w, h)
        
        # Build shaders if needed
        if not self._programs:
            self._build_shaders()
        
        # Render all layers
        self._render_layers(view, proj, w, h)
        
        print(f"[{self.LABEL}] Rendered {w}x{h} layers")

    def _update_geometry(self, verts, uvs, normals):
        """Create VBOs from numpy arrays"""
        ctx = self._ctx
        
        # Release old
        for vbo in [self._vbo_pos, self._vbo_uv, self._vbo_normal]:
            if vbo: vbo.release()
        
        # Create new (ensure float32)
        self._vbo_pos = ctx.buffer(np.array(verts, dtype='f4').tobytes())
        self._vbo_uv = ctx.buffer(np.array(uvs, dtype='f4').tobytes())
        self._vbo_normal = ctx.buffer(np.array(normals, dtype='f4').tobytes())

    def _update_texture(self, tex_data):
        """Create texture from BPY texture data dict"""
        ctx = self._ctx
        
        if self._texture:
            self._texture.release()
        
        if tex_data and 'size' in tex_data:
            self._texture = ctx.texture(
                tex_data['size'],
                tex_data['channels'],
                tex_data['data'],
                dtype=tex_data.get('dtype', 'f4')
            )
        else:
            # White fallback
            white = np.array([1.0, 1.0, 1.0, 1.0], dtype='f4').tobytes()
            self._texture = ctx.texture((1, 1), 4, white, dtype='f4')

    def _update_fbos(self, w, h):
        """Create/resize FBOs for all layers"""
        ctx = self._ctx
        
        # Release old
        for fbo in self._fbos.values():
            if fbo: fbo.release()
        
        self._fbos = {}
        
        # Color: uint8 RGBA
        tex_color = ctx.texture((w, h), 4, dtype='f1')
        self._fbos['color'] = ctx.framebuffer(color_attachments=[tex_color])
        
        # Normal: float32 RGBA (for precision)
        tex_normal = ctx.texture((w, h), 4, dtype='f4')
        self._fbos['normal'] = ctx.framebuffer(color_attachments=[tex_normal])
        
        # Depth: float32 R (or packed)
        tex_depth = ctx.texture((w, h), 4, dtype='f4')
        self._fbos['depth'] = ctx.framebuffer(color_attachments=[tex_depth])
        
        # Position: float32 RGBA (world position)
        tex_pos = ctx.texture((w, h), 4, dtype='f4')
        self._fbos['position'] = ctx.framebuffer(color_attachments=[tex_pos])

    def _build_shaders(self):
        """Compile shader programs for each layer"""
        ctx = self._ctx
        
        vertex_src = '''
            #version 330
            uniform mat4 M, V, P;
            in vec3 in_position;
            in vec3 in_normal;
            in vec2 in_uv;
            out vec3 v_world_pos;
            out vec3 v_normal;
            out vec2 v_uv;
            out float v_depth;
            
            void main() {
                vec4 world_pos = M * vec4(in_position, 1.0);
                vec4 view_pos = V * world_pos;
                vec4 clip_pos = P * view_pos;
                
                gl_Position = clip_pos;
                v_world_pos = world_pos.xyz;
                v_normal = mat3(transpose(inverse(M))) * in_normal;
                v_uv = in_uv;
                v_depth = -view_pos.z;
            }
        '''
        
        # Color pass (with texture)
        frag_color = '''
            #version 330
            uniform sampler2D u_texture;
            uniform vec3 u_light_dir;
            in vec3 v_world_pos;
            in vec3 v_normal;
            in vec2 v_uv;
            in float v_depth;
            out vec4 f_color;
            
            void main() {
                vec4 tex = texture(u_texture, v_uv);
                vec3 n = normalize(v_normal);
                float diff = max(dot(n, normalize(u_light_dir)), 0.0);
                vec3 ambient = tex.rgb * 0.2;
                vec3 lit = tex.rgb * diff * 0.8;
                f_color = vec4(ambient + lit, tex.a);
            }
        '''
        
        # Normal pass
        frag_normal = '''
            #version 330
            in vec3 v_world_pos;
            in vec3 v_normal;
            in vec2 v_uv;
            in float v_depth;
            out vec4 f_color;
            
            void main() {
                vec3 n = normalize(v_normal);
                f_color = vec4(n * 0.5 + 0.5, 1.0);
            }
        '''
        
        # Depth pass
        frag_depth = '''
            #version 330
            uniform float u_far;
            in vec3 v_world_pos;
            in vec3 v_normal;
            in vec2 v_uv;
            in float v_depth;
            out vec4 f_color;
            
            void main() {
                float d = clamp(v_depth / u_far, 0.0, 1.0);
                f_color = vec4(d, d, d, 1.0);
            }
        '''
        
        # Position pass
        frag_position = '''
            #version 330
            in vec3 v_world_pos;
            in vec3 v_normal;
            in vec2 v_uv;
            in float v_depth;
            out vec4 f_color;
            
            void main() {
                f_color = vec4(v_world_pos, 1.0);
            }
        '''
        
        self._programs['color'] = ctx.program(vertex_shader=vertex_src, fragment_shader=frag_color)
        self._programs['normal'] = ctx.program(vertex_shader=vertex_src, fragment_shader=frag_normal)
        self._programs['depth'] = ctx.program(vertex_shader=vertex_src, fragment_shader=frag_depth)
        self._programs['position'] = ctx.program(vertex_shader=vertex_src, fragment_shader=frag_position)

    def _render_layers(self, view_mat, proj_mat, w, h):
        """Render to all FBO layers"""
        ctx = self._ctx
        
        # Prepare matrices (column-major for OpenGL)
        V = np.array(view_mat, dtype='f4').reshape(4, 4)
        P = np.array(proj_mat, dtype='f4').reshape(4, 4)
        # Identity model (or could be input)
        M = np.eye(4, dtype='f4')
        
        # Common VAO setup
        def make_vao(prog):
            return ctx.vertex_array(
                prog,
                [
                    (self._vbo_pos, '3f', 'in_position'),
                    (self._vbo_normal, '3f', 'in_normal'),
                    (self._vbo_uv, '2f', 'in_uv')
                ]
            )
        
        # Render each layer
        layers = ['color', 'normal', 'depth', 'position']
        outputs = [self.O_color, self.O_normal, self.O_depth, self.O_position]
        
        for layer, output_sock in zip(layers, outputs):
            prog = self._programs[layer]
            fbo = self._fbos[layer]
            
            fbo.use()
            ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)
            ctx.clear(0.0, 0.0, 0.0, 0.0)
            
            vao = make_vao(prog)
            
            # Set uniforms
            prog['M'].write(M.tobytes())
            prog['V'].write(V.tobytes())
            prog['P'].write(P.tobytes())
            
            if 'u_texture' in prog:
                self._texture.use(0)
                prog['u_texture'].value = 0
            
            if 'u_light_dir' in prog:
                prog['u_light_dir'].value = (1.0, 1.0, 1.0)
            
            if 'u_far' in prog:
                prog['u_far'].value = 100.0
            
            vao.render(moderngl.TRIANGLES)
            vao.release()
            
            # Readback (flip Y for image coordinates)
            raw = fbo.read(components=4)
            dtype = np.uint8 if layer == 'color' else np.float32
            img = np.frombuffer(raw, dtype=dtype).reshape((h, w, 4))
            output_sock.value = np.flipud(img)

    def on_execute_crawler(self, input_data=None):
        self.on_execute()