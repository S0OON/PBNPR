from PySide6.QtWidgets import QVBoxLayout, QWidget

class InspectorManager:
    def __init__(self):
        self.layout: QVBoxLayout = None
        self._current_widgets = []

    def set_layout(self, layout: QVBoxLayout):
        self.layout = layout

    def clear(self):
        if not self.layout:
            return
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.setParent(None)
                widget.deleteLater()
            # Also handle spacers/layouts if any
        self._current_widgets.clear()

    def update_selection(self, nodes):
        self.clear()
        if not self.layout:
            return
            
        for node in nodes:
            # Check if it has the required interface
            node_name = getattr(node, "NODE_NAME", node.type_)
            
            # Create a container for this node's inspection
            container = QWidget()
            v_lay = QVBoxLayout()
            container.setLayout(v_lay)
            
            # Label for the node name
            from PySide6.QtWidgets import QLabel
            name_label = QLabel(f"<b>{node_name}</b>")
            name_label.setStyleSheet("background-color: #444; padding: 5px; color: #eee; border-radius: 3px;")
            v_lay.addWidget(name_label)
            
            if hasattr(node, "on_gui"):
                try:
                    w = node.on_gui()
                    if w:
                        v_lay.addWidget(w)
                        # Initialize the GUI with current property values
                        if hasattr(node, "reset"):
                            node.reset()
                except Exception as e:
                    error_label = QLabel(f"Error loading GUI: {e}")
                    error_label.setStyleSheet("color: red;")
                    v_lay.addWidget(error_label)
            
            self.layout.addWidget(container)
            self._current_widgets.append(container)
        
        # Add a spacer at the end to keep widgets at the top
        self.layout.addStretch()

INSPECTOR = InspectorManager()

# Output nodes list,
# itterated by PAG to evaluate the branches's nodes.
# lifetime is managed by node itself
OUTPUT_NODES = {}
CLOUD_NODES = {}
EXPORT = {}

# moderngl
CTX = None
