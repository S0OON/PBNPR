import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
from gl_studio.examples.nodes.Node_zPattren import NODE_BASE_INTERFACE as BASE_NODE
import moderngl
import numpy as np

def check_matrix(obj: t.NodeSocket):
    val = obj.value
    if isinstance(val, np.ndarray) and val.dtype == np.float16:
        return True
    
    name = getattr(obj, 'label', getattr(obj, 'name', 'Unknown Socket'))
    print(f"Error: {name} is not an f16 matrix (got {type(val)})")
    return False

def render_simple(pos, normals, matrix, view, proj, width=1920, height=1080):
    """
    Standalone one-shot renderer. Takes raw geometry/matrix arrays and returns an RGBA numpy array.
    """
    # Quick sanity check
    if pos is None or len(pos) == 0:
        return np.zeros((height, width, 4), dtype=np.uint8)

    ctx = None
    fbo = None
    prog = None
    vbo_pos = None
    vbo_norm = None
    vao = None
    
    try:
        ctx = moderngl.create_context(standalone=True)
        
        fbo = ctx.simple_framebuffer((width, height))
        fbo.use()

        ctx.enable(moderngl.DEPTH_TEST | moderngl.CULL_FACE)

        prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec3 in_position;
                in vec3 in_normal;
                
                uniform mat4 M;
                uniform mat4 V;
                uniform mat4 P;
                
                out vec3 v_normal;
                
                void main() {
                    gl_Position = P * V * M * vec4(in_position, 1.0);
                    // Transform normals to world space (assuming uniform scaling)
                    v_normal = mat3(M) * in_normal; 
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_normal;
                out vec4 f_color;
                
                void main() {
                    vec3 n = normalize(v_normal);
                    // Map normal range [-1, 1] to color range [0, 1]
                    f_color = vec4(n * 0.5 + 0.5, 1.0);
                }
            '''
        )

        prog['M'].write(matrix.astype('f4').tobytes())
        prog['V'].write(view.astype('f4').tobytes())
        prog['P'].write(proj.astype('f4').tobytes())

        vbo_pos = ctx.buffer(pos.astype('f4').tobytes())
        vbo_norm = ctx.buffer(normals.astype('f4').tobytes())
        
        vao = ctx.vertex_array(prog, [
            (vbo_pos, '3f', 'in_position'),
            (vbo_norm, '3f', 'in_normal')
        ])

        ctx.clear(0.05, 0.05, 0.05, 1.0) # Dark grey background
        vao.render(moderngl.TRIANGLES)

        raw_data = fbo.read(components=4)
        image_array = np.frombuffer(raw_data, dtype=np.uint8).reshape((height, width, 4))
        
        return np.flipud(image_array)

    except Exception as e:
        print(f"[render_simple] Engine Fault: {e}")
        return np.zeros((height, width, 4), dtype=np.uint8)

    finally:
        # ==========================================
        # 9. THE NUCLEAR CLEANUP (Guaranteed to run)
        # ==========================================
        if ctx:
            # A. Reset all intrusive state flags
            try:
                ctx.screen.use()
                ctx.disable(moderngl.DEPTH_TEST)
                ctx.disable(moderngl.CULL_FACE)
                ctx.disable(moderngl.BLEND)
                ctx.blend_func = moderngl.DEFAULT_BLENDING
                ctx.depth_func = '<'
                _ = ctx.error # Clear error buffer
            except:
                pass
            
            # B. Nuke VRAM objects
            if vao: vao.release()
            if vbo_pos: vbo_pos.release()
            if vbo_norm: vbo_norm.release()
            if prog: prog.release()
            if fbo: fbo.release()
            
            # C. Kill Context
            ctx.release()

class NODE_INTERFACE(BASE_NODE):
    LABEL = 'Shader - colored obj simple'

    def __init__(self, parent):
        super().__init__(parent)

        # --- Sockets Setup ---
        self.I_w = t.NodeSocket(dpg.generate_uuid(),t.F, '<- W',value=128)
        self.I_h = t.NodeSocket(dpg.generate_uuid(),t.F, '<- H',value=128)
        self.I_matrix  = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Model Matrix',np.identity(4,np.float32))
        self.I_normals = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Normals'     ,np.identity(4,np.float32))
        self.I_pos     = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Position'    ,np.identity(4,np.float32))
        self.I_view    = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- View Matrix' ,np.identity(4,np.float32))
        self.I_proj    = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Proj Matrix' ,np.identity(4,np.float32))
        
        self.O_pixels  = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Pixels ->')

        # Register routing
        self._resgister_IO(
            [self.I_w,
             self.I_h,
             self.I_matrix, 
             self.I_normals, 
             self.I_pos, 
             self.I_view, 
             self.I_proj],
            [self.O_pixels]
        )

    def on_gui(self):
        Id = super().on_gui()

        # Static Controls
        statics = self._create_static_attr()
        dpg.add_button(label="Execute Render", callback=self.EXEC_CB, parent=statics)
        dpg.add_input_int(label="Width",  default_value=self.I_w.value,  callback=self._on_width_change,  parent=statics, width=100)
        dpg.add_input_int(label="Height", default_value=self.I_h.value, callback=self._on_height_change, parent=statics, width=100)

        # Inputs
        self._create_input_attr(self.I_w      )
        self._create_input_attr(self.I_h      )
        self._create_input_attr(self.I_matrix )
        self._create_input_attr(self.I_normals )
        self._create_input_attr(self.I_pos    )
        self._create_input_attr(self.I_view)
        self._create_input_attr(self.I_proj)

        # Outputs
        self._create_output_attr(self.O_pixels)

    def _on_width_change(self, s, a, u):  self.I_w.value = max(1, a)
    def _on_height_change(self, s, a, u): self.I_h.value = max(1, a)

    def _create_input_attr(self, socket, pin_shape=dpg.mvNode_PinShape_CircleFilled,name=True):
        Id = super()._create_input_attr(socket, pin_shape)
        if name:
            dpg.add_text(socket.name,parent=Id)
        return Id

    def on_execute(self):
        Pos = self.I_pos.value
        N = self.I_normals.value
        M = self.I_matrix.value
        V = self.I_view.value
        P = self.I_proj.value


        print(f"[{self.LABEL}] Executing custom MGL node...")

        self.O_pixels.value = render_simple(Pos,N,M,V,P,int(self.I_w.value),int(self.I_h.value))


    def on_execute_crawler(self, input_data=None):
        matrix_sockets = [
            self.I_pos, 
            self.I_normals, 
            self.I_matrix, 
            self.I_view, 
            self.I_proj
        ]
        self.on_execute()