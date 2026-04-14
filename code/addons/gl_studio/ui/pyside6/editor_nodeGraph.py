import importlib.util
import inspect
import os
from typing import cast

from gl_studio.ui.examples.nodes.Node_zPattren import NODE_INTERFACE as NODE
from gl_studio.ui.examples.nodes.Node_zPattren import PortType as PORT
from gl_studio.ui.pyside6.internals import cfg as CFG
from gl_studio.util import util_types as t
from NodeGraphQt import BaseNode, NodeGraph
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QMenu, QMenuBar, QVBoxLayout, QWidget


class INTERFACE:
    nodes = {}
    active_links = {}  # { Input_socket_id : Output_socket_id }
    global_node_address = "node.pyside6"
    directories = []

    def __init__(self):
        self.lay: QVBoxLayout = None
        self.graph: NodeGraph = None
        self.menu_bar: QMenuBar = None
        self.menu_IO: QMenu = None
        self.menu_add_node: QMenu = None


cfg = INTERFACE()


class PAG:
    def __init__(self):
        self.graph = None
        self.visited = set()
        self.exec_order = []

    def run(self):
        self.graph = cfg.graph
        if self.graph is None:
            print("PAG.run skipped: no graph available yet.")
            return

        self.visited.clear()
        self.exec_order.clear()

        # 2. Find "Terminal" nodes (Nodes that SHOULD_CRAWL)
        for node in self.graph.all_nodes():
            node = cast(NODE, node)
            if hasattr(node, "CB_IS_CRAWLER") and node.CB_IS_CRAWLER():
                self.order(node)

        self.execs_order()
        self.reset()

    def order(self, node: NODE):
        """Builds the Topological Sort (Execution Order)"""
        if not node or node.id in self.visited:
            return

        self.visited.add(node.id)

        # Look at all input ports
        for name, input_port in node.inputs().items():
            # Get what is connected to this input
            connected_ports = input_port.connected_ports()
            if connected_ports:
                # In NodeGraphQt, connected_ports[0] is the Output port of the sender
                sender_node = connected_ports[0].node()
                self.order(sender_node)

        # Post-order traversal: add to list after children are visited
        self.exec_order.append(node)

    def execs_order(self):
        for node in self.exec_order:
            node = cast(NODE, node)
            # 1. Pull data from upstream
            self._propagate_inputs(node)

            # 2. Execute the node's logic
            if hasattr(node, "CACHED"):
                if not node.CACHED:
                    if hasattr(node, "CB_ON_CRAWLER"):
                        node.CACHED = True
                        node.CB_ON_CRAWLER()

    def _propagate_inputs(self, node):
        """The 'Sync' : Copies values from Output ports to Input ports"""
        for name, input_port in node.inputs().items():
            connected_ports = input_port.connected_ports()
            if not connected_ports:
                continue

            output_port = connected_ports[0]

            input_port = cast(PORT, input_port)
            output_port = cast(PORT, output_port)

            # Pull the 'value' property from the output socket to the input socket
            if (output_port.Type == input_port.Type) or input_port.Type == t.ANY:
                input_port.value = output_port.value

    def reset(self):
        for node in self.exec_order:
            node.CACHED = False


pag = PAG()


# ============================
def load_nodes_from_directory(directory_path):
    """Scans directory and returns a list of valid BaseNode subclasses."""
    discovered_nodes = []
    if not os.path.exists(directory_path):
        print(f"Directory '{directory_path}' not found.")
        return discovered_nodes

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(file)[0]

                spec = importlib.util.spec_from_file_location(module_name, file_path)
                if spec and spec.loader:
                    module = importlib.util.module_from_spec(spec)
                    try:
                        spec.loader.exec_module(module)
                        for name, obj in inspect.getmembers(module, inspect.isclass):
                            if issubclass(obj, BaseNode) and obj is not BaseNode:
                                discovered_nodes.append(obj)
                    except Exception as e:
                        print(f"Failed to load {file_path}: {e}")
    return discovered_nodes


def safe_create_node(n_type):
    # Clear current selection to prevent other nodes from moving with the new one
    cfg.graph.clear_selection()

    # Calculate position
    cursor_pos = cfg.graph.viewer().cursor().pos()
    scene_pos = cfg.graph.viewer().mapToScene(cursor_pos)

    # Create the node
    cfg.graph.create_node(n_type.type_, pos=[scene_pos.x(), scene_pos.y()])


def delete_selected_nodes():
    # Get nodes currently selected in the graph
    selected_nodes = cfg.graph.selected_nodes()
    if selected_nodes:
        # delete_nodes is the standard safe way to remove nodes in NodeGraphQt
        cfg.graph.delete_nodes(selected_nodes)


# ===================================
def check_state():
    if cfg.graph:
        return True
    else:
        return False


def process_frame():
    try:
        if check_state():
            pag.run()
    except Exception as e:
        print(f"Error during frame processing: {e}")


def register():
    widget = QWidget()
    CFG.tabs.addTab(widget, "Node editor")

    cfg.lay = QVBoxLayout()
    widget.setLayout(cfg.lay)

    cfg.menu_bar = QMenuBar()
    cfg.lay.addWidget(cfg.menu_bar)

    cfg.graph = NodeGraph()
    cfg.lay.addWidget(cfg.graph.widget)

    cfg.menu_add_node = QMenu(title="Add Node")
    cfg.menu_bar.addMenu(cfg.menu_add_node)

    cfg.menu_IO = QMenu(title="Import / export")
    cfg.menu_bar.addMenu(cfg.menu_IO)

    shortcut_del = QShortcut(QKeySequence("Delete"), cfg.graph.widget)
    shortcut_del.activated.connect(delete_selected_nodes)

    shortcut_x = QShortcut(QKeySequence("X"), cfg.graph.widget)
    shortcut_x.activated.connect(delete_selected_nodes)

    # --- DYNAMIC NODE REGISTRATION ---

    # 1. Resolve the absolute path to your 'nodes' directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Adjust this relative path to point exactly to your 'nodes' folder
    nodes_directory = os.path.normpath(
        os.path.join(current_dir, "..", "examples", "nodes")
    )

    # ... inside register() in editor_nodeGraph.py ...

    # 2. Discover classes
    node_classes = load_nodes_from_directory(nodes_directory)

    # Dictionary to keep track of created submenus
    sub_menus = {}

    # 3. Register to graph and add to QMenu with submenus
    for node_class in node_classes:
        # Registers to NodeGraphQt (for Tab search)
        cfg.graph.register_node(node_class)

        # Get the category; default to 'Misc' if not defined
        category_name = getattr(node_class, "CATEGORY", "Misc")

        # Create the submenu if it doesn't exist yet
        if category_name not in sub_menus:
            new_sub_menu = cfg.menu_add_node.addMenu(category_name)
            sub_menus[category_name] = new_sub_menu

        target_menu = sub_menus[category_name]

        # Create the action in the specific category submenu
        display_name = getattr(node_class, "NODE_NAME", node_class.__name__)
        action = target_menu.addAction(display_name)

        action.triggered.connect(lambda _, n=node_class: safe_create_node(n))


def unregister():
    if cfg.graph:
        cfg.graph.widget.close()
        cfg.graph = None
