from dataclasses import dataclass
from typing import Any

@dataclass(slots=True)
class NodeSocket:
    ID: int | str
    data_type: str
    name: str = None
    value: Any = None
    connected_to: int | str | None = None

F = 'float'
F2= '2float'
F4= '4float'
F16= '16float'
RGBA = 'rgba'
STR = 'string'
ANY = 'any'
NONE = 'none'
# --- blender specific ---
bl_verts = 'vertices'
bl_Co = 'co'
bl_normal = 'normal'
bl_loop_triangles = 'loop_triangles'