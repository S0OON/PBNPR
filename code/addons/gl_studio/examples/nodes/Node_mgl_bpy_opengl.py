# Node_opengl.py
import dearpygui.dearpygui as dpg
from gl_studio.util import util_types as t
import numpy as np
import moderngl
from gl_studio.gl.ModernOpenGL import GLctx as GL

class NODE_INTERFACE:
    LABEL = "ModernGL Render"
    
    def __init__(self, parent):
        self.PARENT = parent
        self.ID = dpg.generate_uuid()
        
        # --- 1. Sockets Setup (Using new name idiom) ---
        # Geometry Inputs
        self.I_verts   = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Vertices (Numpy)')
        self.I_normals = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Normals (Numpy)')
        
        # Matrix Inputs
        self.I_model = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Model Matrix')
        self.I_view  = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- View Matrix')
        self.I_proj  = t.NodeSocket(dpg.generate_uuid(), t.F16, '<- Proj Matrix')
        
        self.I_model.value = np.eye(4, dtype=np.float32)
        self.I_view.value  = np.eye(4, dtype=np.float32)
        self.I_proj.value  = np.eye(4, dtype=np.float32)
        
        # Output
        self.O_pixels = t.NodeSocket(dpg.generate_uuid(), t.RGBA, 'Image Pixels (RGBA) ->')
        
        # --- 2. ModernGL Setup ---
        self.ctx = GL.get()
        self.ctx.enable(moderngl.DEPTH_TEST | moderngl.PROGRAM_POINT_SIZE)
        
        self.width, self.height = 512, 512
        self.fbo = self.ctx.simple_framebuffer((self.width, self.height))
        
        self.prog = self.ctx.program(
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
                    gl_PointSize = 4.0; 
                    v_normal = in_normal;
                }
            ''',
            fragment_shader='''
                #version 330
                in vec3 v_normal;
                out vec4 fragColor;
                
                void main() {
                    vec3 light = normalize(vec3(1.0, 1.0, 1.0));
                    float diff = max(dot(v_normal, light), 0.2);
                    vec3 color = vec3(0.2, 0.6, 1.0) * diff; 
                    fragColor = vec4(color, 1.0);
                }
            '''
        )
        
        # --- Standard Callbacks ---
        self.EXEC_GUI_CB        = self.on_gui
        self.EXEC_CB            = self.on_execute
        self.EXEC_ON_CRAWLER_CB = self.on_execute_crawler
        self.EXEC_ON_LOOP_CB    = self.on_execute_after_frame
        
        self.SHOULD_EXEC_CB     = self.on_should_execute
        self.SHOULD_CRAWL_CB    = self.on_should_crawl
        self.SHOULD_BE_ACTIVE   = self.on_should_active
        
        self.ENABLE = True
        self.ACTIVE = False
        self.CRAWL  = False
        
        self.inputs = {
            self.I_verts.ID   : self.I_verts,
            self.I_normals.ID : self.I_normals,
            self.I_model.ID   : self.I_model,
            self.I_view.ID    : self.I_view,
            self.I_proj.ID    : self.I_proj
        } 
        
        self.outputs = {
            self.O_pixels.ID : self.O_pixels
        }

    def on_gui(self):
        with dpg.node(label=self.LABEL, parent=self.PARENT, tag=self.ID):
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                dpg.add_button(label="Execute Render", callback=self.EXEC_CB)
                dpg.add_checkbox(label="Enable", callback=self.on_enable_change, default_value=self.ENABLE)
                dpg.add_text(f"All sockets uses NumPy data")

            # Inputs (Using the new idiom!)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_verts.ID):
                dpg.add_text(self.I_verts.name)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_normals.ID):
                dpg.add_text(self.I_normals.name)
                
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_model.ID):
                dpg.add_text(self.I_model.name)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_view.ID):
                dpg.add_text(self.I_view.name)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input, tag=self.I_proj.ID):
                dpg.add_text(self.I_proj.name)
            
            # Outputs (Using the new idiom!)
            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output, tag=self.O_pixels.ID):
                dpg.add_text(self.O_pixels.name)

    # --- Callbacks ---
    def on_enable_change(self, sender, app_data):
        self.ENABLE = app_data
        
    def on_should_execute(self): return self.ENABLE
    def on_should_crawl(self): return self.CRAWL
    def on_should_active(self): return self.ACTIVE and self.ENABLE

    def on_execute(self):
        verts = self.I_verts.value
        normals = self.I_normals.value
        
        if verts is None or not isinstance(verts, np.ndarray) or len(verts) == 0:
            print(f"[{self.LABEL}] Error: Missing or invalid vertex data.")
            return

        if normals is None or len(normals) != len(verts):
            normals = np.ones_like(verts, dtype=np.float32)

        self.prog['M'].write(self.I_model.value.astype('f4').tobytes(order='F'))
        self.prog['V'].write(self.I_view.value.astype('f4').tobytes(order='F'))
        self.prog['P'].write(self.I_proj.value.astype('f4').tobytes(order='F'))

        vbo_pos = self.ctx.buffer(verts.astype('f4').tobytes())
        vbo_norm = self.ctx.buffer(normals.astype('f4').tobytes())
        
        vao = self.ctx.vertex_array(self.prog, [
            (vbo_pos, '3f', 'in_position'),
            (vbo_norm, '3f', 'in_normal')
        ])

        self.fbo.use()
        self.ctx.clear(0.1, 0.1, 0.1, 1.0)
        
        vao.render(moderngl.POINTS) 

        raw_bytes = self.fbo.read(components=4) 
        
        pixels = np.frombuffer(raw_bytes, dtype=np.uint8).reshape((self.height, self.width, 4))
        
        self.O_pixels.value = pixels
        
        vao.release()
        vbo_pos.release()
        vbo_norm.release()
        
        print(f"[{self.LABEL}] Rendered {len(verts)} vertices to {self.width}x{self.height} image.")

    def on_execute_crawler(self, input_data=None):
        if self.SHOULD_EXEC_CB():
            self.on_execute()
        
    def on_execute_after_frame(self): pass