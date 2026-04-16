from NodeGraphQt import BaseNode, NodeBaseWidget
from Qt import QtCore, QtWidgets


class MyCustomWidget(QtWidgets.QWidget):
    """
    Custom widget to be embedded inside a node.
    """

    def __init__(self, parent=None):
        super(MyCustomWidget, self).__init__(parent)
        self.combo_1 = QtWidgets.QComboBox()
        self.combo_1.addItems(["a", "b", "c"])
        self.combo_2 = QtWidgets.QComboBox()
        self.combo_2.addItems(["a", "b", "c"])
        self.btn_go = QtWidgets.QPushButton("Go")

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.combo_1)
        layout.addWidget(self.combo_2)
        layout.addWidget(self.btn_go)


class NodeWidgetWrapper(NodeBaseWidget):
    """
    Wrapper that allows the widget to be added in a node object.
    """

    def __init__(self, parent=None):
        super(NodeWidgetWrapper, self).__init__(parent)

        # set the name for node property.
        self.set_name("my_widget")

        # set the label above the widget.
        self.set_label("Custom Widget")

        # set the custom widget.
        self.set_custom_widget(MyCustomWidget())

        # connect up the signals & slots.
        self.wire_signals()

    def wire_signals(self):
        widget = self.get_custom_widget()

        # wire up the combo boxes.
        widget.combo_1.currentIndexChanged.connect(self.on_value_changed)
        widget.combo_2.currentIndexChanged.connect(self.on_value_changed)

        # wire up the button.
        widget.btn_go.clicked.connect(self.on_btn_go_clicked)

    def on_btn_go_clicked(self):
        print('Clicked on node: "{}"'.format(self.node.name()))

    def get_value(self):
        widget = self.get_custom_widget()
        return "{}/{}".format(
            widget.combo_1.currentText(), widget.combo_2.currentText()
        )

    def set_value(self, value):
        value = value.split("/")
        if len(value) < 2:
            combo1_val = value[0]
            combo2_val = ""
        else:
            combo1_val, combo2_val = value
        widget = self.get_custom_widget()

        cb1_index = widget.combo_1.findText(combo1_val, QtCore.Qt.MatchExactly)
        cb2_index = widget.combo_1.findText(combo2_val, QtCore.Qt.MatchExactly)

        widget.combo_1.setCurrentIndex(cb1_index)
        widget.combo_2.setCurrentIndex(cb2_index)


class MyNode(BaseNode):
    """
    Example node.
    """

    # set a unique node identifier.
    __identifier__ = "io.github.jchanvfx"

    # set the initial default node name.
    NODE_NAME = "my node"

    def __init__(self):
        super(MyNode, self).__init__()

        # create input and output port.
        self.add_input("in")
        self.add_output("out")

        # add custom widget to node with "node.view" as the parent.
        node_widget = NodeWidgetWrapper(self.view)
        self.add_custom_widget(node_widget, tab="Custom")
