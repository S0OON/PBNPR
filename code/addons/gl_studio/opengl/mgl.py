import moderngl as gl
import moderngl as mgl
import numpy as np
from gl_studio.util import util_types as t

#---- Defaulted Constants

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


class ContextFlags:
    nothing = mgl.NOTHING
    blend = mgl.BLEND
    depth_test = mgl.DEPTH_TEST
    cull_face = mgl.CULL_FACE
    rasterizer_discard = mgl.RASTERIZER_DISCARD
    program_point_size = mgl.PROGRAM_POINT_SIZE

class PrimitiveFlags:
    points = mgl.POINTS
    lines = mgl.LINES
    line_loop = mgl.LINE_LOOP
    line_strip = mgl.LINE_STRIP
    triangles = mgl.TRIANGLES
    triangle_strip = mgl.TRIANGLE_STRIP
    triangle_fan = mgl.TRIANGLE_FAN
    lines_adjacency = mgl.LINES_ADJACENCY
    line_strip_adjacency = mgl.LINE_STRIP_ADJACENCY
    triangles_adjacency = mgl.TRIANGLES_ADJACENCY
    triangle_strip_adjacency = mgl.TRIANGLE_STRIP_ADJACENCY
    patches = mgl.PATCHES

class TextureFlags:
    nearest = mgl.NEAREST
    linear = mgl.LINEAR
    nearest_mipmap_nearest = mgl.NEAREST_MIPMAP_NEAREST
    linear_mipmap_nearest = mgl.LINEAR_MIPMAP_NEAREST
    nearest_mipmap_linear = mgl.NEAREST_MIPMAP_LINEAR
    linear_mipmap_linear = mgl.LINEAR_MIPMAP_LINEAR

class BlendFlags:
    zero = mgl.ZERO
    one = mgl.ONE
    src_color = mgl.SRC_COLOR
    one_minus_src_color = mgl.ONE_MINUS_SRC_COLOR
    src_alpha = mgl.SRC_ALPHA
    one_minus_src_alpha = mgl.ONE_MINUS_SRC_ALPHA
    dst_alpha = mgl.DST_ALPHA
    one_minus_dst_alpha = mgl.ONE_MINUS_DST_ALPHA
    dst_color = mgl.DST_COLOR
    one_minus_dst_color = mgl.ONE_MINUS_DST_COLOR
    func_add = mgl.FUNC_ADD
    func_subtract = mgl.FUNC_SUBTRACT
    func_reverse_subtract = mgl.FUNC_REVERSE_SUBTRACT
    min = mgl.MIN
    max = mgl.MAX

class ConventionFlags:
    first_vertex = mgl.FIRST_VERTEX_CONVENTION
    last_vertex = mgl.LAST_VERTEX_CONVENTION

# The Composite Class
class Flags:
    context = ContextFlags
    primitive = PrimitiveFlags
    texture = TextureFlags
    blend = BlendFlags
    convention = ConventionFlags


class SHADER:
    """One-shot or temporary testing abtraction class"""

    def __init__(self, Standalone_context=True) -> None:
        self.ctx = gl.create_context(standalone=Standalone_context)
        self.ctx.gc_mode = 'context_gc'
        # State trackers for safe cleanup
        self.prog = None
        self.fbo = None
        self.depth=None
        self.vao = None
        self.vbos = []  # Keep track of dynamic buffers
        self.texs = {}
        self.tex_list = []  # Keep track of textures for safe cleanup

        self.src_v = t.SRC_SCREEN_VERT
        self.src_f = t.SRC_SCREEN_FRAG
        self.w = int(t.RES_W)
        self.h = int(t.RES_H)
        self.def_screen_pos = t.GLOBAL_DEFAULT_SCREEN_V
        self.def_screen_uv = t.GLOBAL_DEFAULT_SCREEN_UV

    def compile(self):
        self.prog = self.ctx.program(
            vertex_shader=self.src_v,
            fragment_shader=self.src_f,
        )

        self.col = self.ctx.renderbuffer((self.w, self.h),dtype='f4')
        self.depth = self.ctx.depth_renderbuffer((self.w,self.h))

        self.fbo = self.ctx.framebuffer(color_attachments=self.col,depth_attachment=self.depth)

    def uniforms(self, uniforms_dict):
        """Pushes global variables to the shader. (Uniformic data)"""
        if not self.prog:
            return
        uniforms = uniforms_dict if isinstance(uniforms_dict, dict) else {}

        if t.RES not in uniforms.keys():
            uniforms[t.RES] = (self.w, self.h)

        for name, data in uniforms.items():
            if name in self.prog:
                if isinstance(data, (list, tuple)) and len(data) == 16:
                    self.prog[name].write(np.array(data, dtype="f4").tobytes())
                else:
                    # Handle normal values (floats, vectors)
                    self.prog[name].value = data

    def uniforms_textures(self, textures_dict):
        if not self.prog:
            return

        textures = textures_dict if isinstance(textures_dict, dict) else {}
        texture_location = 0

        for name, tex_obj in textures.items():
            if name in self.prog:
                if isinstance(tex_obj, np.ndarray):
                    # Valid way to get dimensions from a (H, W, C) array
                    h, w, c = tex_obj.shape
                    pixels = tex_obj.tobytes()
                    dtype = 'f4' # Defaulting to float32 as used in your nodes [cite: 108, 112]
                else:
                    print(f"[MGL CLASS] invalid texture object type: {type(tex_obj)}")
                    return

                tex = self.ctx.texture((w, h), c, data=pixels, dtype=dtype)
                tex.filter = (gl.NEAREST, gl.NEAREST)
                self.tex_list.append(tex)
                tex.use(location=texture_location)
                self.prog[name].value = texture_location
                texture_location += 1

    def vertex_attributes(self, attributes_dict):
        """Generates VBOs and creates the VAO layout. Non-Uniformic data (Varying per Vertex)"""
        if not self.prog:
            return

        attrs = attributes_dict if isinstance(attributes_dict, dict) else {}
        keys = attrs.keys()

        if t.POS not in keys:
            attrs[t.POS] = self.def_screen_pos
        if t.UV not in keys:
            attrs[t.UV] = self.def_screen_uv

        vao_blueprint = []
        self.vbos = []  # Reset VBO tracker

        for name, obj in attrs.items():
            if name in self.prog:
                if isinstance(obj,np.ndarray):
                    vbo = self.ctx.buffer(obj)
                    fmt = t.get_mgl_format(obj)
                    vao_blueprint.append((vbo, fmt, name))
                else:
                    print(f"[MGL CLASS] invalid: {type(obj)}")
                    return

        if not vao_blueprint:
            return

        # Build and store the VAO
        self.vao = self.ctx.vertex_array(self.prog, vao_blueprint)

    def render(self, render_flag):
        """Executes the draw call and returns bytes."""
        if not self.vao or not self.fbo:
            return None

        self.fbo.use()
        self.ctx.clear()
        self.vao.render(render_flag)

        # 1. Add dtype to frombuffer (defaults to float64, which is wrong for 1-byte color)
        raw = self.fbo.read(components=4, dtype='f4')
        rawD = self.fbo.read(attachment=-1,components=1, dtype='f4')

        return raw, rawD


    def clear(self):
        """Safely destroys all GPU objects to free VRAM."""
        # Add this inside clear(self)
        self.ctx.gc()
        return
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
