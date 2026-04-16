import moderngl as mgl
from gl_studio.examples.nodes import Node_zPattren as BASE
from gl_studio.opengl.mgl import GL as SHADER
from gl_studio.util import util_types as t
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class NODE_MGL_SHADER(BASE.NODE_INTERFACE):
    NODE_NAME = "MGL Dynamic Shader"
    CATEGORY = "OpenGL"

    def __init__(self):
        super().__init__()

        # --- INPUTS ---
        self.I_width = self.add_input("width", type=t.F, default_value=t.RES_W)
        self.I_height = self.add_input("height", type=t.F, default_value=t.RES_H)

        self.I_vert = self.add_input("vertex_code", type=t.STR)
        self.I_frag = self.add_input("fragment_code", type=t.STR)

        self.I_uni = self.add_input("dict_uni", type=t.DICT)
        self.I_res = self.add_input("dict_res", type=t.DICT)

        # --- OUTPUTS ---
        # Outputs the dict containing {'Combined': np.ndarray, ...}
        self.O_maps = self.add_output("render_maps", type=t.DICT)

    def build_ui(self):
        widget = QWidget()

        lay = QVBoxLayout()
        lay.setContentsMargins(5, 5, 5, 5)
        widget.setLayout(lay)

        self.status_label = QLabel("Status: Waiting...")
        self.status_label.setStyleSheet("color: #AAA; font-weight: bold;")
        lay.addWidget(self.status_label)

        return widget

    def on_execute_crawler(self):
        # 1. Fetch Inputs
        v_code = str(self.I_vert.value) if self.I_vert.value else ""
        f_code = str(self.I_frag.value) if self.I_frag.value else ""

        # Ensure we have dictionaries even if nothing is connected
        dict_uni = self.I_uni.value if isinstance(self.I_uni.value, dict) else {}
        dict_res = self.I_res.value if isinstance(self.I_res.value, dict) else {}

        # Fallback if no shaders are provided
        if not v_code or not f_code:
            self.status_label.setText("Status: Missing GLSL Code")
            self.status_label.setStyleSheet("color: #FFaa00;")
            self.O_maps.value = {}
            return

        ctx = None
        shader = None
        # START
        try:
            ctx = mgl.create_context()
            shader = SHADER(ctx)  # Instantiate our dynamic GL class

            shader.compile(
                V=v_code,
                F=f_code,
                dict_uni=dict_uni,
                dict_res=dict_res,
                out_size=(
                    int(self.I_width.value),
                    int(self.I_height.value),
                ),
            )

            # 4. Execute (Render to FBO and get the pixel dictionary back)
            result_maps_dict = shader.execute()

            # 5. Output the results downstream
            self.O_maps.value = result_maps_dict

            # Update UI on success
            self.status_label.setText("Status: Rendered OK")
            self.status_label.setStyleSheet("color: #55FF55;")

        except Exception as e:
            # Update UI on failure (e.g., GLSL syntax error, missing uniform)
            self.status_label.setText("Status: Error")
            self.status_label.setStyleSheet("color: #FF5555;")
            print(f"[MGL Shader Error]: {e}")
            self.O_maps.value = {}

        finally:
            # 6. ALWAYS Cleanup GPU Resources!
            # The try/finally block ensures that even if the shader crashes
            # midway through compiling, the GPU memory is released.
            if shader:
                shader.release()
            if ctx:
                ctx.release()
