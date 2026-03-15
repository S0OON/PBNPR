# DONT CHANGE CAPITLIZED NAMES! (called from the plugin)
from PySide6 import QtWidgets
import moderngl, bpy
from PIL import Image
import numpy as np
from gl_studio.gl.modrenGL_lib import GLContext as GL
from gl_studio.util import util_types as t
from gl_studio.ui.util.HotCombo import HotCombo # Kept your import just in case

class ShaderBase:
    
    vertex_shader=f"""
#version 330
    uniform mat4 uOBJ;
    uniform mat4 uCAM;
    uniform mat4 uPROJ;

    in vec3 inPOS;
    in vec2 inUV;

    out vec2 vUV;

        void main() {{
            gl_Position = uPROJ * uCAM * uOBJ * vec4(inPOS, 1.0);
            vUV = inUV;
        }}
"""
    fragment_shader=f"""
#version 330
    uniform sampler2D uTEX;
    in vec2 vUV;

    out vec4 fragCol;

        void main() {{
            fragCol = texture(uTEX, vUV);
        }}
"""
    __slots__ = ['ctx', 'prog', 'vao', 'fbo']
    def __init__(self): 
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

    def _uniforms(self, **kwargs): 
        for name, value in kwargs.items():
            self.prog[name].value = value

    def Execute(self, width, height, gl_flags=None, clear=True):
        W, H = int(width),int(height)
        if self.fbo is None or self.fbo.size != (W, H):
            if self.fbo:
                self.fbo.release()
            
            depth_buffer = self.ctx.depth_renderbuffer((W, H))
            Color_buffer = self.ctx.texture((W, H), 4)
            
            self.fbo = self.ctx.framebuffer( 
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

        # WARNING, WILL BREAK BLENDER UI IF THIS SNIPPET IS DELETED
        # Fallback dictionary gets () in case t.GL_FLAGS is missing keys
        self.ctx.disable(t.GL_FLAGS.get('DEPTH_TEST', moderngl.DEPTH_TEST) |
                         t.GL_FLAGS.get('CULL_FACE', moderngl.CULL_FACE) |        
                         t.GL_FLAGS.get('BLEND', moderngl.BLEND) |        
                         t.GL_FLAGS.get('PROGRAM_POINT_SIZE', moderngl.PROGRAM_POINT_SIZE) |        
                         t.GL_FLAGS.get('RASTERIZER_DISCARD', moderngl.RASTERIZER_DISCARD) )
        return pixels 

class MAIN:
    __slots__ = ['data', '__weakref__', 
                 'shader', 
                 'targetOBJ','targetUV','targetIMG','targetOUT',
                 'use_depth', 'use_cull', 'use_blend'] # <-- Added flag slots
    
    def __init__(self):
        self.shader = ShaderBase()
        self.targetIMG = ''
        self.targetOUT = ''
        self.targetOBJ = ''
        self.targetUV  = ''
        
        # Default states for ModernGL flags
        self.use_depth = True
        self.use_cull = True
        self.use_blend = False

    def BUILD_UI(self, target_layout:QtWidgets.QVBoxLayout):
        # --- Output Image Name ---
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Output (bpy.data.images):"))
        field = QtWidgets.QLineEdit()
        field.setText(self.targetOUT)
        field.textChanged.connect(self.on_targetOUT_change)
        row.addWidget(field)
        target_layout.addLayout(row)

        # --- Object Name ---
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Target Object:"))
        field = QtWidgets.QLineEdit()
        field.setText(self.targetOBJ) 
        field.textChanged.connect(self.on_targetOBJ_change)
        row.addWidget(field)
        target_layout.addLayout(row)

        # --- UV Map Name ---
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("UV Map Name:"))
        field = QtWidgets.QLineEdit()
        field.setText(self.targetUV)
        field.textChanged.connect(self.on_targetUV_change)
        row.addWidget(field)
        target_layout.addLayout(row)
        
        # --- Input Image ---
        row = QtWidgets.QHBoxLayout()
        row.addWidget(QtWidgets.QLabel("Input Texture:"))
        field = QtWidgets.QLineEdit()
        field.setText(self.targetIMG)
        field.textChanged.connect(self.on_targetIMG_change)
        row.addWidget(field)
        target_layout.addLayout(row)

        # --- ModernGL Flags ---
        row_flags = QtWidgets.QHBoxLayout()
        row_flags.addWidget(QtWidgets.QLabel("GL Flags:"))

        cb_depth = QtWidgets.QComboBox()
        cb_depth.addItems(["Depth: ON", "Depth: OFF"])
        cb_depth.setCurrentIndex(0 if self.use_depth else 1)
        cb_depth.activated.connect(self.on_depth_change)
        row_flags.addWidget(cb_depth)

        cb_cull = QtWidgets.QComboBox()
        cb_cull.addItems(["Cull: ON", "Cull: OFF"])
        cb_cull.setCurrentIndex(0 if self.use_cull else 1)
        cb_cull.activated.connect(self.on_cull_change)
        row_flags.addWidget(cb_cull)

        cb_blend = QtWidgets.QComboBox()
        cb_blend.addItems(["Blend: OFF", "Blend: ON"])
        cb_blend.setCurrentIndex(1 if self.use_blend else 0)
        cb_blend.activated.connect(self.on_blend_change)
        row_flags.addWidget(cb_blend)

        target_layout.addLayout(row_flags)

    def EXECUTE(self):
        pixels = self._Render()
        if pixels is None: 
            return
            
        out_image = bpy.data.images.get(self.targetOUT)
        if out_image:
            # ModernGL returns uint8 (0-255). Blender wants floats (0.0 - 1.0)
            blender_pixels = (pixels.astype(np.float32) / 255.0).flatten()
            out_image.pixels = blender_pixels
            out_image.update()
            print(f"SUCCESS: Rendered to '{self.targetOUT}'")
        else:
            # Fallback if Blender image doesn't exist
            print(f"Warning: Output image '{self.targetOUT}' not found. Opening PIL preview.")
            W = bpy.context.scene.render.resolution_x
            H = bpy.context.scene.render.resolution_y
            img = Image.frombytes('RGBA', (W, H), pixels).transpose(Image.FLIP_TOP_BOTTOM)
            img.show()

    # --- Callbacks ---
    def on_targetOUT_change(self, text): self.targetOUT = text
    def on_targetOBJ_change(self, text): self.targetOBJ = text      
    def on_targetUV_change(self, text):  self.targetUV = text
    def on_targetIMG_change(self, text): self.targetIMG = text
    def on_depth_change(self, index):    self.use_depth = (index == 0)
    def on_cull_change(self, index):     self.use_cull = (index == 0)
    def on_blend_change(self, index):    self.use_blend = (index == 1)

    def _get_obj_data(self, name: str):
        obj = bpy.data.objects.get(name)
        if not obj: return None, None, None, None
        
        depsgraph = bpy.context.evaluated_depsgraph_get()
        eval_obj = obj.evaluated_get(depsgraph)
        mesh = eval_obj.to_mesh()
        mesh.calc_loop_triangles()

        # Unroll Positions
        all_pos = np.empty(len(mesh.vertices) * 3, dtype=np.float32)
        mesh.vertices.foreach_get("co", all_pos)
        all_pos = all_pos.reshape(-1, 3)

        # Unroll UVs
        all_uvs = np.zeros((len(mesh.loops), 2), dtype=np.float32)
        if mesh.uv_layers.get(self.targetUV):
            mesh.uv_layers[self.targetUV].data.foreach_get("uv", all_uvs.reshape(-1))
        else: 
            print(f"Error: UV Map '{self.targetUV}' not found!")
            return None, None, None, None

        loop_vert_indices = np.empty(len(mesh.loops), dtype=np.int32)
        mesh.loops.foreach_get("vertex_index", loop_vert_indices)
        
        # Map vertices to loops (removes the need for an index buffer!)
        final_pos = all_pos[loop_vert_indices]
        final_uvs = all_uvs

        eval_obj.to_mesh_clear()
        
        # Returning exactly 4 variables so your unpack (i, p, n, uv) doesn't crash
        return None, final_pos, None, final_uvs

    def _Render(self):
        Shader = self.shader
 
        obj  = bpy.data.objects.get(self.targetOBJ)
        cam  = bpy.context.scene.camera
        if not obj or not cam: return None
        
        deps = bpy.context.evaluated_depsgraph_get()
        w,h  = [bpy.context.scene.render.resolution_x, bpy.context.scene.render.resolution_y]

        m_world = np.array(obj.matrix_world.transposed(), dtype=np.float32).flatten()
        m_view  = np.array(cam.matrix_world.inverted().transposed(), dtype=np.float32).flatten()
        m_proj  = np.array(cam.calc_matrix_camera(deps, x=w, y=h).transposed(), dtype=np.float32).flatten()
        
        i, p, n, uv = self._get_obj_data(self.targetOBJ)
        if p is None: return None 

        # 1. Update Uniforms
        Shader.prog['uOBJ'].value = tuple(m_world)
        Shader.prog['uCAM'].value = tuple(m_view)
        Shader.prog['uPROJ'].value = tuple(m_proj)

        # 2. Bind the Texture
        input_image = bpy.data.images.get(self.targetIMG)
        tex = None
        if input_image:
            tex_pixels = np.array(input_image.pixels, dtype=np.float32)
            tex = Shader.ctx.texture((input_image.size[0], input_image.size[1]), 4, tex_pixels.tobytes(), dtype='f4')
            tex.use(location=0)
            Shader.prog['uTEX'].value = 0 
        else:
            print(f"Warning: Input image '{self.targetIMG}' not found!")

        # 3. Create Buffers and VAO
        vbo_pos = Shader.ctx.buffer(p.tobytes())
        vbo_uv = Shader.ctx.buffer(uv.tobytes())

        if Shader.vao:
            Shader.vao.release()

        # No index_buffer needed because arrays are perfectly unrolled!
        Shader.vao = Shader.ctx.vertex_array(
            Shader.prog,
            [
                (vbo_pos, '3f', 'inPOS'),
                (vbo_uv, '2f', 'inUV') 
            ]
        )

        # 4. Construct GL Flags
        gl_flags = 0
        if self.use_depth: gl_flags |= moderngl.DEPTH_TEST
        if self.use_cull:  gl_flags |= moderngl.CULL_FACE
        if self.use_blend: gl_flags |= moderngl.BLEND

        # 5. Execute and cleanup
        result_pixels = Shader.Execute(w, h, gl_flags=gl_flags, clear=True)
        
        vbo_pos.release()
        vbo_uv.release()
        if tex: tex.release()

        return result_pixels