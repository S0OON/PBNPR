from typing import Any

from gl_studio.util import util_types as t
from NodeGraphQt import BaseNode, NodeBaseWidget, Port
from PySide6 import QtWidgets


class PortType(Port):
    value = Any
    Type = t.NONE


class UniversalWrapper(NodeBaseWidget):
    """
    A generic wrapper that takes any QWidget and makes it
    compatible with NodeGraphQt without requiring a custom class.
    """

    def __init__(self, qt_widget, label="Control", parent=None):
        super(UniversalWrapper, self).__init__(parent)
        self.set_name(label)
        self.set_label(label)

        self.custom_ui = qt_widget
        self.set_custom_widget(self.custom_ui)

    def get_value(self):
        return ""  # Satisfies the library requirements

    def set_value(self, value):
        pass  # Satisfies the library requirements


class NODE_INTERFACE(BaseNode):
    NODE_NAME = "Node"
    CATEGORY = ""

    # INTERNALS
    def __init__(self):
        super(NODE_INTERFACE, self).__init__()

        self.CB_IS_CRAWLER = self.on_should_crawl
        self.CB_ON_CRAWLER = self.on_execute_crawler
        self.CACHED = False

        widgeto = self.build_ui()
        self.integrate_widget(widgeto)

    # GUI WRAPPERS
    def build_ui(self) -> QtWidgets.QWidget:
        """Build a QtWidget and return it."""
        return QtWidgets.QWidget()

    def integrate_widget(self, qt_widget, label=""):
        self.node_widget = UniversalWrapper(qt_widget, label=label, parent=self.view)

        self.add_custom_widget(self.node_widget)

        self.widget = qt_widget

    def add_input(
        self,
        name="input",
        type=None,
        default_value=None,
        multi_input=False,
        display_name=True,
        color=None,
        locked=False,
        painter_func=None,
    ) -> PortType:
        port = super().add_input(
            name, multi_input, display_name, color, locked, painter_func
        )
        port.value = default_value
        port.Type = type
        return port

    def add_output(
        self,
        name="output",
        type=None,
        default_value=None,
        multi_output=True,
        display_name=True,
        color=None,
        locked=False,
        painter_func=None,
    ) -> PortType:
        port = super().add_output(
            name, multi_output, display_name, color, locked, painter_func
        )
        port.value = default_value
        port.Type = type
        return port

    # EXECUTION BEHAVIOURS
    def on_should_crawl(self):
        """Return True if this node is an output of a node connection branches"""

    def on_execute_crawler(self) -> None:
        """What will happen if executed by connected nodes (by Crawler)"""
