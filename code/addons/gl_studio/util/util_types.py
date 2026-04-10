# all mallocs are on heap so who cares for infinite classes >:]
class SocketDataType:
    """A unified class to hold a socket's type ID and its visual color."""
    def __init__(self, id_string: str, color: tuple):
        self.id = id_string
        self.color = color

    def __str__(self): return self.id
    def __repr__(self): return self.id
    def __eq__(self, other):
        if isinstance(other, str): return self.id == other
        if isinstance(other, SocketDataType): return self.id == other.id
        return False
    def __hash__(self): return hash(self.id)

# =====================================================================
# SOCKET CLASS
# =====================================================================
class NodeSocket:
    def __init__(self, id_tag, data_type, name, value=None):
        self.ID = id_tag
        self.name = name
        self.value = value
        # If passed a SocketDatatype object, extract its string ID automatically
        self.data_type = data_type.id if isinstance(data_type, SocketDataType) else data_type

# =====================================================================
# DATA TYPES 
# Colors mapped to Blender's node editor standards (RGB format)
# =====================================================================

# Primitives
F       = SocketDataType("FLOAT",   (160, 160, 160)) # Grey
INT     = SocketDataType("INT",     ( 44, 176, 115)) # Green
BOOL    = SocketDataType("BOOL",    (204, 166, 217)) # Soft Pink
STR     = SocketDataType("STR",     (230, 150,  50)) # Soft Orange

# Math & Data
VEC     = SocketDataType("VECTOR",  ( 99,  99, 200)) # Deep Blue/Purple
F16     = SocketDataType("MATRIX",  (200,  80,  80)) # Red
RGBA    = SocketDataType("COLOR",   (204, 204,  51)) # Yellow

# Objects & Geometry
OB      = SocketDataType("OBJECT",  (230, 150, 100)) # Object Orange
GEO     = SocketDataType("GEOMETRY",(  0, 210, 160)) # Geometry Cyan/Teal

# System / Logic
ANY     = SocketDataType("ANY",     (220, 220, 220)) # White (Accepts anything)
NONE    = SocketDataType("NONE",    ( 80,  80,  80)) # Dark Grey (Execution/Pulse)

# =====================================================================
# AUTOMATIC DICTIONARY 
# =====================================================================

_all_types = [F, INT, BOOL, STR, VEC, F16, RGBA, OB, GEO, ANY, NONE]
SOCKET_COLORS = {t.id: t.color for t in _all_types}
