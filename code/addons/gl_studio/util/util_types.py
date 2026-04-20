from dataclasses import dataclass


@dataclass
class formated_data:
    data: bytes  # The raw .tobytes() data
    fmt: str  # The layout format (e.g., '3f', '2f', '4f')


# Ouput nodes list,
# itterated by PAG to evaluate the branches's nodes.
# lifetime is managed by node itself
GLOBAL_OUTPUT_NODES = []
# --- util Types
NONE = "NONE"  # flags
ANY = "ANY"
STR = "string"  # basic
INT = "int"
F = "f"
F2 = "2f"
F3 = "3f"
F4 = "4f"
F16 = "F16"
DICT = "Dict"  # containers
DICTS = "Dicts"
RGBA = "rgba"
# --- util constants
RES_W = 1024
RES_H = 1024
LNKED = "Linked."
LNKED_FAIL = "Not Linked."
# --- HEX (pyside6)
RED = "color: #ff0000;"
GREEN = "color: #00ff00;"
# --- mgl specific
