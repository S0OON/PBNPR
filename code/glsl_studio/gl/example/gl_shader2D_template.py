
from PySide6 import QtWidgets

class MAIN:
    NAME = "Color Control"
    
    def __init__(self):
        self.width = 512.0
        self.height = 512.0

    def BUILD_UI(self, target_layout):
        # --- Row for Width ---
        row_w = QtWidgets.QHBoxLayout()
        row_w.addWidget(QtWidgets.QLabel("Width:"))
        
        spin_w = QtWidgets.QDoubleSpinBox()
        spin_w.setMaximum(4096.0)
        spin_w.setValue(self.width)
        
        spin_w.valueChanged.connect(self.on_width_changed) # Owned connection 
        
        row_w.addWidget(spin_w)
        target_layout.addLayout(row_w)

        # --- Row for Height ---
        row_h = QtWidgets.QHBoxLayout()
        row_h.addWidget(QtWidgets.QLabel("Height:"))
        
        spin_h = QtWidgets.QDoubleSpinBox()
        spin_h.setMaximum(4096.0)
        spin_h.setValue(self.height)
        spin_h.valueChanged.connect(self.on_height_changed)
        
        row_h.addWidget(spin_h)
        target_layout.addLayout(row_h)

    # These functions fire instantly when the user clicks the UI arrows
    def on_width_changed(self, value):
        self.width = value
        print(f"Shader internal width updated to: {self.width}")

    def on_height_changed(self, value):
        self.height = value
        print(f"Shader internal height updated to: {self.height}")

    def EXECUTE(self):
        import moderngl
        import numpy as np
        from PIL import Image

        ctx = moderngl.create_context()

        width, height = 800, 600
        fbo = ctx.framebuffer(color_attachments=[ctx.renderbuffer((width, height))])
        fbo.use()
        
        prog = ctx.program(
            vertex_shader='''
                #version 330
                in vec2 in_vert;
                void main() {
                    gl_Position = vec4(in_vert, 0.0, 1.0);
                }
            ''',
            fragment_shader='''
                #version 330
                out vec4 f_color;
                void main() {
                    // Normalize coordinates to create a gradient
                    f_color = vec4(gl_FragCoord.x / 800.0, 0.5, gl_FragCoord.y / 600.0, 1.0);
                }
            ''',
        )
        
        vertices = np.array([
            -1.0,  1.0,
            -1.0, -1.0,
            1.0,  1.0,
            1.0, -1.0,
        ], dtype='f4')

        vbo = ctx.buffer(vertices)
        vao = ctx.vertex_array(prog, [(vbo, '2f', 'in_vert')])

        fbo.clear(0.0, 0.0, 0.0, 1.0)
        vao.render(moderngl.TRIANGLE_STRIP)

        data = fbo.read(components=3)
        img = Image.frombytes('RGB', fbo.size, data).transpose(Image.FLIP_TOP_BOTTOM)
        img.show()