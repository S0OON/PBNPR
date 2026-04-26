import importlib.util
import inspect
import os
import traceback
from typing import cast

from gl_studio.examples.nodes.Node_zPattren import NODE_INTERFACE as NODE
from gl_studio.examples.nodes.Node_zPattren import PortType as PORT
from gl_studio.ui.pyside6.internals import cfg as PROG_CFG
from gl_studio.util import util_types as t
from OdenGraphQt import BaseNode, NodeGraph, Port
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import QSizePolicy,QFileDialog, QMenu, QMenuBar, QVBoxLayout, QWidget, QSplitter,QTabWidget
from PySide6 import QtCore

class INTERFACE:
    Tab_main_label = "Node Editor"
    Tab_settings_label = "Settings"
    Tab_Inspec_label = "Inspect"
    nodes = {}
    active_links = {}  # { Input_socket_id : Output_socket_id }
    directories = []

    def __init__(self):
        self.widget:QWidget = None
        self.lay: QVBoxLayout = None

        self.menu_bar: QMenuBar = None
        self.menu_add_node: QMenu = None
        self.menu_Graph: QMenu = None

        self.splitter:QWidget = None
        self.graph: NodeGraph = None
        self.side_panel:QTabWidget = None
        self.tab_sets:QWidget = None
        self.tab_inspec:QWidget = None

    def setup_layout(self):
        PROG_CFG.tabs.addTab(self.widget,self.Tab_main_label)

        self.widget.setLayout(self.lay)

        self.lay.addWidget(self.menu_bar)
        self.lay.addWidget(self.splitter)
        #self.widget.setStyleSheet("border: 2px solid red;")


        self.menu_bar.addMenu(self.menu_add_node)
        self.menu_bar.addMenu(self.menu_Graph)
        self.menu_bar.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Fixed)

        self.splitter.addWidget(self.graph.widget)
        self.splitter.addWidget(self.side_panel)

        self.side_panel.addTab(self.tab_sets,self.Tab_settings_label)
        self.side_panel.addTab(self.tab_inspec,self.Tab_Inspec_label)

    def toggle_side_panel(self):
        if self.side_panel.isHidden():
            self.side_panel.show()
        else:
            self.side_panel.hide()

    def save_graph(self):
        """Opens a dialog to save the current node session to a JSON file."""
        # The dialog returns a tuple: (file_path, selected_filter)
        file_path, _ = QFileDialog.getSaveFileName(
            None,  # Parent widget (can be your main window)
            "Save Node Session",  # Dialog Title
            "",  # Default directory (leave blank for current)
            "JSON Files (*.json);;All Files (*)",  # File filters
        )

        try:
            for node in self.graph.all_nodes():
                if hasattr(node, "CB_ON_SAVE"):
                    node.CB_ON_SAVE()
        except Exception as e:
            print("Load failure: ", e)

        if file_path:
            self.graph.save_session(file_path)
            print(f"Graph saved successfully to: {file_path}")

    def load_graph(self):
        """Opens a dialog to load a node session from a JSON file."""
        file_path, _ = QFileDialog.getOpenFileName(
            None, "Load Node Session", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            self.graph.clear_session()

            # Load session - this will trigger property restoration
            self.graph.load_session(file_path)
            print(f"Graph loaded successfully from: {file_path}")

            # Now trigger load callbacks on all nodes
            # Use a slight delay or process events to ensure properties are ready
            for node in self.graph.all_nodes():
                node = cast(NODE, node)
                if hasattr(node, "CB_ON_LOAD"):
                    try:
                        node.CB_ON_LOAD()
                    except Exception as e:
                        print(f"Load callback error on {node.NODE_NAME}: {e}")

    def ref_pos(self):
        for node in self.graph.all_nodes():
            p = self.graph.widget.pos()
            node.set_pos(p.x(), p.y())


cfg = INTERFACE()


class PAG:
    def __init__(self):
        self.visited = set()
        self.exec_order = []

    def run(self):
        # 2. Find "Terminal" nodes (Nodes that SHOULD_CRAWL)
        for node in t.GLOBAL_OUTPUT_NODES:
            if hasattr(node, "CB_IS_STREAM") and node.CB_IS_STREAM():
                self.order(node)

        self.exec()
        self.reset()

    def order(self, node: NODE):
        if not node or node.id in self.visited:
            return

        self.visited.add(node.id)

        for name, input_port in node.inputs().items():
            if out_ports := input_port.connected_ports():
                for out_port in out_ports:
                    out_node = out_port.node()
                    self.order(out_node)

        # Post-order traversal: add to list after children are visited
        self.exec_order.append(node)

    def exec(self):
        for node in self.exec_order:
            node = cast(NODE, node)
            # 2. Execute the node's logic
            if hasattr(node, "CACHED"):
                # FIX: Check if CACHED is False, not None
                if not node.CACHED:
                    # FIX: Correct typo 'CB_ON_STERAM' to 'CB_ON_STREAM'
                    if hasattr(node, "CB_ON_STREAM"):
                        node.CACHED = True
                        try:
                            node.CB_ON_STREAM()
                        except Exception as e:
                            print(f"[NODE GRAPH NODE REPORT] at {node.type_} : {e}")
                            traceback.print_exc()

    def reset(self):
        for node in self.exec_order:
            node.CACHED = False
        self.exec_order.clear()
        self.visited.clear()


pag = PAG()


# ============== NODES SPECIFIC ==============
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
        for node in selected_nodes:
            if hasattr(node, "CB_ON_DEL"):
                node.CB_ON_DEL()
        cfg.graph.delete_nodes(selected_nodes)


def duplicate_selected():
    selections = cfg.graph.selected_nodes()
    for node in selections:
        safe_create_node(type(node))


# ============================
def check_state():
    if cfg.graph:
        return True
    else:
        print("[NODE GRAPH CRITICAL]  cfg.graph is NONE.")
        return False


def process_frame():
    pag.run()
    for node in cfg.graph.all_nodes():
        node = cast(NODE, node)
        pos = node.view.pos()
        x = pos.x()
        y = pos.y()
        node.set_pos(x, y)


def _PreProcess():
    """This function monkey-hooks Direct Property acceess functions inside NodeGraphQt.Port class"""
    Port.val = None
    Port.Fmt = None
    Port.Type = None


def _Create_shortcuts():
    shortcut_del = QShortcut(QKeySequence("Delete"), cfg.graph.widget)
    shortcut_del.activated.connect(delete_selected_nodes)

    shortcut_x = QShortcut(QKeySequence("X"), cfg.graph.widget)
    shortcut_x.activated.connect(delete_selected_nodes)

    shortcut_save = QShortcut(QKeySequence("Ctrl+S"), cfg.graph.widget)
    shortcut_save.activated.connect(cfg.save_graph)

    shortcut_load = QShortcut(QKeySequence("Ctrl+L"), cfg.graph.widget)
    shortcut_load.activated.connect(cfg.load_graph)

    shortcut_dup = QShortcut(QKeySequence("Shift+D"), cfg.graph.widget)
    shortcut_dup.activated.connect(duplicate_selected)

    short_tog_panel = QShortcut(QKeySequence("N"), cfg.graph.widget)
    short_tog_panel.activated.connect(cfg.toggle_side_panel)

def _Create_GUI():
    cfg.widget = QWidget()

    cfg.lay = QVBoxLayout()

    cfg.menu_bar = QMenuBar()

    cfg.splitter = QSplitter(QtCore.Qt.Horizontal)

    cfg.graph = NodeGraph()

    cfg.side_panel = QTabWidget()

    cfg.tab_sets = QWidget()

    cfg.tab_inspec = QWidget()

    cfg.menu_add_node = QMenu(title="Add Node")

    cfg.menu_Graph = QMenu(title="Graph settings")

    cfg.setup_layout()

    (cfg.menu_Graph.addAction("Save")).triggered.connect(cfg.save_graph)
    (cfg.menu_Graph.addAction("Load")).triggered.connect(cfg.load_graph)
    (cfg.menu_Graph.addAction("Panel")).triggered.connect(cfg.toggle_side_panel)

    # --- DYNAMIC NODE REGISTRATION ---

    current_dir = os.path.dirname(os.path.abspath(__file__))
    nodes_directory = os.path.normpath(
        os.path.join(current_dir, "..", "..", "examples", "nodes")
    )

    node_classes = load_nodes_from_directory(nodes_directory)

    sub_menus = {}
    for node_class in node_classes:
        cfg.graph.register_node(node_class)

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


def register():
    _PreProcess()
    _Create_GUI()
    _Create_shortcuts()
    t.GLOB_INSPECTOR_WIDGET = cfg.tab_inspec


def unregister():
    global cfg
    if cfg.graph:
        cfg.graph.close()
    del cfg
