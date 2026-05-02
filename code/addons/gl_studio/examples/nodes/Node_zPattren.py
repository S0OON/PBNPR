from typing import Any

from gl_studio.util import util_types as t
from OdenGraphQt import BaseNode, NodeBaseWidget, Port
from PySide6.QtWidgets import QWidget


class PortType(Port):
    val = Any
    Fmt = ""
    Type = ""


class NODE_WIDGET(NodeBaseWidget):
    def __init__(self, qt_widget, label="Control", parent=None):
        super(NODE_WIDGET, self).__init__(parent)

        self.set_name(label)

        self.set_custom_widget(qt_widget)

    def get_value(self):
        return ""  # Satisfies the library requirements

    def set_value(self, text):
        pass  # Satisfies the library requirements



class NODE_INTERFACE(BaseNode):
    NODE_NAME = "Node"
    CATEGORY = "Misc"

    # INTERNALS
    def __init__(self):
        super().__init__()
        self.create_property(
            name="null", value=""
        )  # Satisfies the library requirements

        self.CB_IS_STREAM = self.on_should_stream
        self.CB_ON_STREAM = self.on_stream
        self.CB_ON_SAVE = self.on_graph_save
        self.CB_ON_LOAD = self.on_graph_load
        self.CB_ON_DEL = self.on_delete
        self.CACHED = False

        self.has = self.has_property
        self.get = self.get_property
        self.set = self.set_property
        self.add = self.create_property

        UTILITY_WIDGET = self.on_gui()
        if UTILITY_WIDGET is not None:
            self.integrate_widget(UTILITY_WIDGET)

    def reset(self) -> None:
        """Utilty empty function."""
        ...

    # GUI WRAPPERS
    def on_gui(self) -> QWidget | None:
        """This function should Build and Return a Naitive PySide6.QtWidgets.* to be in the node content."""
        ...

    def integrate_widget(self, qt_widget, label="") -> None:
        qt_widget = NODE_WIDGET(qt_widget, label=label, parent=self.view)
        self.add_custom_widget(qt_widget)

    def get_socket_color(self,data_type):
        """
        Returns an RGB tuple (0-255)
        """
        # BLENDER REFERENCE MAPPING
        colors = {
            # Grey: Simple numerical or undefined values
            t.NONE: (150, 150, 150),
            t.ANY: (200, 200, 200),
            # Lime Green: Booleans
            t.BOOL: (163, 201, 126),
            # Darker Green: Integers
            t.INT: (28, 138, 70),
            # Grey/Light Blue: Floats
            t.F: (161, 161, 161),
            t.F2: (119, 143, 168),  # Light Blue-ish
            t.F3: (63, 126, 252),  # Blue (Vectors)
            t.F4: (44, 88, 176),  # Deep Blue
            t.F16: (30, 60, 120),
            # Blue: Strings
            t.STR: (111, 190, 240),
            # Yellow: RGBA / Colors
            t.RGBA: (199, 199, 41),
            # Green: Shaders / Materials
            t.SHADER: (78, 209, 115),
            # Turquoise/Cyan: Geometry
            t.GEO: (0, 214, 163),
            # White: Execution Flow
            t.EXEC: (255, 255, 255),
        # Orange/Gold: Dictionaries and Complex Containers
            t.DICT: (255, 155, 0),
            t.DICTS: (200, 120, 0),
            t.ARRAY: (255, 180, 50),
        }

        # Return the color or a default pink if type is unknown (so you notice the error!)
        return colors.get(data_type, (255, 0, 255))

    def add_input(
        self,
        name="input",
        type=None,
        format=None,
        default_value=None,
        multi_input=False,
        display_name=True,
        color=None,
        locked=False,
        painter_func=None,
    ) -> PortType:
        port = super().add_input(
            name,
            multi_input,
            display_name,
            color if color is not None else self.get_socket_color(type),
            locked,
            painter_func,
        )
        port.val = default_value
        port.Type = type
        port.fmt = format
        return port

    def add_output(
        self,
        name="output",
        type=None,
        format=None,
        default_value=None,
        multi_output=True,
        display_name=True,
        color=None,
        locked=False,
        painter_func=None,
    ) -> PortType:
        port = super().add_output(
            name,
            multi_output,
            display_name,
            color if color is not None else self.get_socket_color(type),
            locked,
            painter_func,
        )
        port.val = default_value
        port.Type = type
        port.fmt = format
        return port

    # EXECUTION BEHAVIOURS
    def on_should_stream(self) -> bool:
        """
        Called by PAG,

        Return True if node is at GLOBAL_OUTPUT_NODES
        and its connected branch needs to evaluate each node
        """
        ...

    def on_stream(self) -> None:
        """
        Called by PAG,

        when its the node's turn inside ordering of an ACTIVE node branches (stream)
        """

    def on_graph_save(self) -> None:
        """Called by Qt shortcuts, THis function Runs when we save a seesion"""

    def on_graph_load(self) -> None:
        """Called by Qt shortcuts, THis function Runs when we Load a seesion"""

    def on_delete(self) -> None:
        """Called by Qt shortcuts, when the node is selcted and deleted"""

    def on_sync_port_values(self) -> None:
        """Utlity function, Clones values from inputs to outputs at type matching or input is type of "ANY", so data steam is handled per node if overiden"""
        for i_p in self.input_ports():
            o_ps = i_p.connected_ports()
            if o_ps:
                o_p = o_ps[0]
                if i_p.Type == t.ANY or (i_p.Type == o_p.Type):
                    i_p.val = o_p.val
