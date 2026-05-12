import bpy
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QLineEdit, QVBoxLayout, QWidget

SCENE_NAME = "scene_name"

class NODE_TIMELINE(BASE.NODE_INTERFACE):
    NODE_NAME = "Timeline"
    CATEGORY = "Blender"

    def __init__(self):
        super().__init__()
        # Inputs
        self.I_scene = self.add_input("Scene Name", type=t.STR)
        
        # Outputs
        self.O_current = self.add_output(name="Current", type=t.F)
        self.O_start = self.add_output(name="Start", type=t.F)
        self.O_end = self.add_output(name="End", type=t.F)
        self.O_progress = self.add_output(name="Progress", type=t.F)
        self.O_fps = self.add_output(name="FPS", type=t.F)
        
        self.reset()

    def on_gui(self):
        widget = QWidget()
        lay = QVBoxLayout()
        widget.setLayout(lay)

        self.line_scene = QLineEdit()
        self.line_scene.setPlaceholderText("Scene Name (Leave blank for Active)")
        self.line_scene.textChanged.connect(lambda v: self.set(SCENE_NAME, v))
        lay.addWidget(self.line_scene)

        self.status_label = QLabel()
        lay.addWidget(self.status_label)

        return widget

    def reset(self, v=None):
        if self.has(SCENE_NAME):
            self.line_scene.setText(self.get(SCENE_NAME))
        else:
            self.add(SCENE_NAME, "")

        self.status_label.setText("Ready")
        self.status_label.setStyleSheet(t.WHITE)

    def on_stream(self):
        self.on_sync_port_values()
        
        # 1. Determine Target Scene
        scene_name = self.I_scene.val if self.I_scene.val is not None and self.I_scene.val != "" else self.get(SCENE_NAME)
        
        scene = None
        if scene_name:
            scene = bpy.data.scenes.get(scene_name)
            if not scene:
                self.status_label.setText(f"Scene '{scene_name}' not found")
                self.status_label.setStyleSheet(t.RED)
        
        # Fallback to active scene
        if not scene:
            scene = bpy.context.scene
            if scene_name == "":
                self.safe_set_status(f"Active Scene: {scene.name}", t.WHITE)
            else:
                self.safe_set_status(f"Fallback to Active: {scene.name}", t.WHITE)
        else:
            self.safe_set_status(f"Using Scene: {scene.name}", t.GREEN)

        # 2. Extract Timeline Info
        f_current = float(scene.frame_current)
        f_start = float(scene.frame_start)
        f_end = float(scene.frame_end)
        fps = float(scene.render.fps) / float(scene.render.fps_base)
        
        # Calculate Progress (0.0 to 1.0)
        range_len = f_end - f_start
        if range_len != 0:
            progress = (f_current - f_start) / range_len
        else:
            progress = 0.0
            
        # 3. Set Outputs
        self.O_current.val = f_current
        self.O_start.val = f_start
        self.O_end.val = f_end
        self.O_progress.val = progress
        self.O_fps.val = fps

    def on_graph_load(self):
        self.reset()
