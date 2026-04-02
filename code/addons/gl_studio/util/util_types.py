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
