from dataclasses import dataclass
from functools import lru_cache
from typing import Any
from PySide6.QtWidgets import QWidget
import numpy as np

@dataclass(slots=True)
class formated_data:
    data: Any
    fmt: str

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

# Ouput nodes list,
# itterated by PAG to evaluate the branches's nodes.
# lifetime is managed by node itself
GLOBAL_OUTPUT_NODES = []
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
def get_socket_color(data_type):
    """
    Returns an RGB tuple (0-255)
    """
    # BLENDER REFERENCE MAPPING
    colors = {
        # Grey: Simple numerical or undefined values
        NONE: (150, 150, 150),
        ANY: (200, 200, 200),
        # Lime Green: Booleans
        BOOL: (163, 201, 126),
        # Darker Green: Integers
        INT: (28, 138, 70),
        # Grey/Light Blue: Floats
        F: (161, 161, 161),
        F2: (119, 143, 168),  # Light Blue-ish
        F3: (63, 126, 252),  # Blue (Vectors)
        F4: (44, 88, 176),  # Deep Blue
        F16: (30, 60, 120),
        # Blue: Strings
        STR: (111, 190, 240),
        # Yellow: RGBA / Colors
        RGBA: (199, 199, 41),
        # Green: Shaders / Materials
        SHADER: (78, 209, 115),
        # Turquoise/Cyan: Geometry
        GEO: (0, 214, 163),
        # White: Execution Flow
        EXEC: (255, 255, 255),
        # Orange/Gold: Dictionaries and Complex Containers
        DICT: (255, 155, 0),
        DICTS: (200, 120, 0),
        ARRAY: (255, 180, 50),
    }

    # Return the color or a default pink if type is unknown (so you notice the error!)
    return colors.get(data_type, (255, 0, 255))

    #
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
GLOBAL_DEFAULT_SCREEN_V = np.array([
     1.0,  1.0,  # Top-Right
     1.0, -1.0,  # Bottom-Right
    -1.0,  1.0,  # Top-Left
    -1.0, -1.0,  # Bottom-Left
], dtype=np.float32).reshape(4, 2)

GLOBAL_DEFAULT_SCREEN_UV = np.array([
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
GLOB_INSPECTOR_WIDGET : QWidget = None
