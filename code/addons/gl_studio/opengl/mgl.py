import moderngl as gl
import moderngl as mgl
import numpy as np
from gl_studio.util import util_types as t

flag_context_enable = {
    "NOTHING": mgl.NOTHING,
    "BLEND": mgl.BLEND,
    "DEPTH_TEST": mgl.DEPTH_TEST,
    "CULL_FACE": mgl.CULL_FACE,
    "RASTERIZER_DISCARD": mgl.RASTERIZER_DISCARD,
    "PROGRAM_POINT_SIZE": mgl.PROGRAM_POINT_SIZE,
}

flag_primitive_modes = {
    "POINTS": mgl.POINTS,
    "LINES": mgl.LINES,
    "LINE_LOOP": mgl.LINE_LOOP,
    "LINE_STRIP": mgl.LINE_STRIP,
    "TRIANGLES": mgl.TRIANGLES,
    "TRIANGLE_STRIP": mgl.TRIANGLE_STRIP,
    "TRIANGLE_FAN": mgl.TRIANGLE_FAN,
    "LINES_ADJACENCY": mgl.LINES_ADJACENCY,
    "LINE_STRIP_ADJACENCY": mgl.LINE_STRIP_ADJACENCY,
    "TRIANGLES_ADJACENCY": mgl.TRIANGLES_ADJACENCY,
    "TRIANGLE_STRIP_ADJACENCY": mgl.TRIANGLE_STRIP_ADJACENCY,
    "PATCHES": mgl.PATCHES,
}

flag_texture_filters = {
    "NEAREST": mgl.NEAREST,
    "LINEAR": mgl.LINEAR,
    "NEAREST_MIPMAP_NEAREST": mgl.NEAREST_MIPMAP_NEAREST,
    "LINEAR_MIPMAP_NEAREST": mgl.LINEAR_MIPMAP_NEAREST,
    "NEAREST_MIPMAP_LINEAR": mgl.NEAREST_MIPMAP_LINEAR,
    "LINEAR_MIPMAP_LINEAR": mgl.LINEAR_MIPMAP_LINEAR,
}

flag_blend_functions_equations = {
    "ZERO": mgl.ZERO,
    "ONE": mgl.ONE,
    "SRC_COLOR": mgl.SRC_COLOR,
    "ONE_MINUS_SRC_COLOR": mgl.ONE_MINUS_SRC_COLOR,
    "SRC_ALPHA": mgl.SRC_ALPHA,
    "ONE_MINUS_SRC_ALPHA": mgl.ONE_MINUS_SRC_ALPHA,
    "DST_ALPHA": mgl.DST_ALPHA,
    "ONE_MINUS_DST_ALPHA": mgl.ONE_MINUS_DST_ALPHA,
    "DST_COLOR": mgl.DST_COLOR,
    "ONE_MINUS_DST_COLOR": mgl.ONE_MINUS_DST_COLOR,
    "FUNC_ADD": mgl.FUNC_ADD,
    "FUNC_SUBTRACT": mgl.FUNC_SUBTRACT,
    "FUNC_REVERSE_SUBTRACT": mgl.FUNC_REVERSE_SUBTRACT,
    "MIN": mgl.MIN,
    "MAX": mgl.MAX,
}

flag_vertex_conventions = {
    "FIRST_VERTEX_CONVENTION": mgl.FIRST_VERTEX_CONVENTION,
    "LAST_VERTEX_CONVENTION": mgl.LAST_VERTEX_CONVENTION,
}


class SHADER:
    """One-shor or temporary testing abtraction class"""

    def __init__(self, Standalone_context=True) -> None:
        self.ctx = gl.create_context(standalone=Standalone_context)
        # State trackers for safe cleanup
        self.prog = None
        self.fbo = None
        self.vao = None
        self.vbos = []  # Keep track of dynamic buffers
        self.texs = {}
        self.tex_list = []  # Keep track of textures for safe cleanup

        # Default shaders
        self.src_v = """
            #version 330
            in vec3 positions;
            void main() {
                gl_Position = vec4(positions, 1.0);
            }
        """
        self.src_f = """
            #version 330

            out vec4 fragColor;
            void main() {
                fragColor = vec4(1.0);
            }
        """
        self.w = int(t.RES_W)
        self.h = int(t.RES_H)
        self.screen = np.array(
            [
                -1.0,
                -1.0,  # Bottom Left
                1.0,
                -1.0,  # Bottom Right
                -1.0,
                1.0,  # Top Left
                1.0,
                1.0,  # Top Right
            ],
            dtype=np.float32,
        )

    def compile(self, w=None, h=None):
        if w is not None:
            self.w = int(w)
        if h is not None:
            self.h = int(h)

        self.prog = self.ctx.program(
            vertex_shader=self.src_v,
            fragment_shader=self.src_f,
        )
        self.fbo = self.ctx.simple_framebuffer((self.w, self.h))

    def uniforms(self, uniforms_dict):
        """Pushes global variables to the shader. (Uniformic data)"""
        if not self.prog:
            return
        uniforms = uniforms_dict if isinstance(uniforms_dict, dict) else {}

        if "resolution" not in uniforms.keys():
            uniforms["resolution"] = (self.w, self.h)

        for name, data in uniforms.items():
            if name in self.prog:
                if isinstance(data, (list, tuple)) and len(data) == 16:
                    self.prog[name].write(np.array(data, dtype="f4").tobytes())
                else:
                    # Handle normal values (floats, vectors)
                    self.prog[name].value = data

    def textures(self, textures_dict):
        """Creates textures, (Uniformic Data)"""
        if not self.prog:
            return

        textures = textures_dict if isinstance(textures_dict, dict) else {}

        # Keep track of the texture unit (slot) we are assigning
        # We start at slot 0 and count up for each texture
        texture_location = 0

        for name, tex_obj in textures.items():
            if name in self.prog:
                # 1. Extract metadata
                # Assuming fmt is a tuple like (width, height, components)
                # If it's literally a string like "1024,1024,3,4f":
                parts = tex_obj.fmt.split(",")
                w, h, components = map(int, parts[:3])
                dtype = parts[3]
                # 2. Create the texture in VRAM
                # ModernGL expects raw bytes, so we convert the numpy array
                pixel_bytes = tex_obj.data.tobytes()

                tex = self.ctx.texture(
                    (w, h), components, data=pixel_bytes, dtype=dtype
                )
                tex.filter = (gl.NEAREST, gl.NEAREST)

                # Store for safe cleanup later
                self.tex_list.append(tex)

                # 3. Bind it to a specific texture unit (slot)
                tex.use(location=texture_location)

                # 4. Tell the shader's sampler2D which slot to look at
                self.prog[name].value = texture_location

                # Increment slot for the next texture in the loop
                texture_location += 1

    def vertex_attributes(self, attributes_dict):
        """Generates VBOs and creates the VAO layout. Non-Uniformic data (Varying per Vertex)"""
        if not self.prog:
            return
        attrs = attributes_dict if isinstance(attributes_dict, dict) else {}

        if "positions" not in attrs.keys():
            attrs["positions"] = t.formated_data(self.screen, t.F2)

        vao_blueprint = []
        self.vbos = []  # Reset VBO tracker

        for name, obj in attrs.items():
            if name in self.prog:
                # Create buffer and track it
                vbo = self.ctx.buffer(obj.data)  # suggested to be np arrays
                self.vbos.append(vbo)
                # Add to blueprint
                vao_blueprint.append((vbo, obj.fmt, name))

        if not vao_blueprint:
            return

        # Build and store the VAO
        self.vao = self.ctx.vertex_array(self.prog, vao_blueprint)

    def render(self, render_flag):
        """Executes the draw call and returns RGB bytes."""
        if not self.vao or not self.fbo:
            return None

        # Lock onto the FBO right before rendering
        self.fbo.use()
        self.ctx.clear()

        self.vao.render(render_flag)

        return self.fbo.read(components=3)

    def clear(self):
        """Safely destroys all GPU objects to free VRAM."""
        # Add this inside clear(self)
        for tex in self.tex_list:
            tex.release()
        self.tex_list.clear()
        if self.vao:
            self.vao.release()
            self.vao = None

        for vbo in self.vbos:
            vbo.release()
        self.vbos.clear()

        if self.prog:
            self.prog.release()
            self.prog = None

        if self.fbo:
            self.fbo.release()
            self.fbo = None
