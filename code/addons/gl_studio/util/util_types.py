import numpy as np
import moderngl as mgl
# --- util Types
NONE = "NONE"  # flags
ANY = "ANY"
BOOL = "bool"  # basic
STR = "string"
INT = "int"
F = "f"
F2 = "2f"
F3 = "3f"
F4 = "4f"
F16 = "F16"
DICT = "Dict"   # containers
DICTS = "Dicts"
RGBA = "rgba"
GEO = "geometry"
ARRAY = "array"
EXEC = "exec"
SHADER = "shader"

# --- util constants
RES_W = 1024
RES_H = 1024
LNKED = "Linked."
LNKED_FAIL = "Not Linked."

# --- PySide6
WHITE = "color: #ffffff;"
RED = "color: #ff0000;"
GREEN = "color: #00ff00;"
BLUE = "color: #0000ff;"


# --- ModernGl
POS = 'positions'
UV = 'UVMap'
RES = 'resolution'

SCREEN_VERTS = np.array([
     1.0,  1.0,  # Top-Right
     1.0, -1.0,  # Bottom-Right
    -1.0,  1.0,  # Top-Left
    -1.0, -1.0,  # Bottom-Left
], dtype=np.float32).reshape(4, 2)

SCREEN_UV = np.array([
    1.0, 1.0,  # Top-Right
    1.0, 0.0,  # Bottom-Right
    0.0, 1.0,  # Top-Left
    0.0, 0.0,  # Bottom-Left
], dtype=np.float32).reshape(4, 2)

SRC_SCREEN_VERT = f"""
    #version 330
    in vec2 {POS};

    void main() {{
        gl_Position = vec4(vec3({POS},0.0), 1.0);
    }}
"""

SRC_SCREEN_FRAG = """
    #version 330

    out vec4 fragColor;

    void main() {
        fragColor = vec4(1.0);
    }
"""
# --- Global nukes, fast and unsafe access.

MGL_TYPES = {
    np.float32: 'f',
    np.float64: 'd',
    np.int32:   'i',
    np.uint8:   'u1'
}

#@lru_cache(maxsize=128)
def get_mgl_format(array: np.ndarray) -> str:
    """Dynamically generates a ModernGL format string from an N-Dimensional Numpy Array."""

    mgl_char = MGL_TYPES.get(array.dtype.type, 'f')

    # If the array is 2D (e.g. Nx3), components = 3.
    # If the array is 1D (e.g. N), components = 1.
    components = array.shape[1] if len(array.shape) > 1 else 1

    return f"{components}{mgl_char}"

 #+=====================

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
